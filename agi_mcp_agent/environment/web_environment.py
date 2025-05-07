"""Web environment implementation for agent interactions with web pages."""

import logging
import re
import time
from typing import Any, Dict, List, Optional
import urllib.parse

import aiohttp
from bs4 import BeautifulSoup
import requests

from agi_mcp_agent.environment.base import Environment

logger = logging.getLogger(__name__)


class WebEnvironment(Environment):
    """Environment that provides access to web browsing capabilities."""

    def __init__(
        self, 
        name: str, 
        headers: Dict[str, str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        user_agent: str = None
    ):
        """Initialize the web environment.

        Args:
            name: The name of the environment
            headers: Default headers to use for HTTP requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            user_agent: User agent string to use (if None, a default is provided)
        """
        super().__init__(name)
        
        self.default_user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
        self.headers = headers or {}
        if not self.headers.get("User-Agent") and not user_agent:
            self.headers["User-Agent"] = self.default_user_agent
        elif user_agent:
            self.headers["User-Agent"] = user_agent
            
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
        
        # State management
        self.state = {
            "current_url": None,
            "history": [],
            "cookies": {},
            "last_page_content": None,
            "last_page_soup": None,
            "last_error": None
        }
        
        logger.info(f"Web Environment {self.name} initialized")

    async def create_session(self):
        """Create an aiohttp session for async requests."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session

    async def close_session(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a web browsing action.

        Args:
            action: The action to execute with the following keys:
                - action_type: The type of action (visit, extract, search, etc.)
                - additional action-specific parameters

        Returns:
            The result of the action
        """
        action_type = action.get("action_type", "").lower()
        
        try:
            if action_type == "visit":
                return self._visit_url(action.get("url", ""), action.get("parse", True))
            elif action_type == "extract":
                return self._extract_content(
                    selector=action.get("selector", ""),
                    selector_type=action.get("selector_type", "css"),
                    attribute=action.get("attribute", None)
                )
            elif action_type == "back":
                return self._go_back()
            elif action_type == "search":
                return self._search(
                    query=action.get("query", ""),
                    engine=action.get("engine", "google")
                )
            elif action_type == "click":
                return self._click_link(
                    selector=action.get("selector", ""),
                    selector_type=action.get("selector_type", "css"),
                    text_match=action.get("text_match", None)
                )
            elif action_type == "get_links":
                return self._get_links()
            elif action_type == "get_images":
                return self._get_images()
            else:
                logger.warning(f"Unknown web action: {action_type}")
                return {"success": False, "error": f"Unknown action: {action_type}"}
                
        except Exception as e:
            logger.error(f"Error in web action {action_type}: {str(e)}")
            self.state["last_error"] = str(e)
            return {"success": False, "error": str(e)}

    def _visit_url(self, url: str, parse: bool = True) -> Dict[str, Any]:
        """Visit a URL and optionally parse the content.

        Args:
            url: The URL to visit
            parse: Whether to parse the content as HTML

        Returns:
            The page content and metadata
        """
        if not url:
            return {"success": False, "error": "No URL provided"}
        
        # Ensure the URL has a scheme
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        for attempt in range(self.max_retries):
            try:
                response = requests.get(
                    url=url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                
                # Update state
                self.state["current_url"] = url
                if self.state["current_url"] not in self.state["history"]:
                    self.state["history"].append(url)
                self.state["last_page_content"] = response.text
                self.state["cookies"].update(dict(response.cookies))
                
                content_type = response.headers.get("Content-Type", "").lower()
                is_html = "text/html" in content_type
                
                if parse and is_html:
                    soup = BeautifulSoup(response.text, "html.parser")
                    self.state["last_page_soup"] = soup
                    
                    # Extract key information
                    title = soup.title.text.strip() if soup.title else "No title"
                    
                    # Extract metadata
                    meta_tags = {}
                    for meta in soup.find_all("meta"):
                        name = meta.get("name") or meta.get("property")
                        content = meta.get("content")
                        if name and content:
                            meta_tags[name] = content
                    
                    # Extract links
                    links = [a.get("href") for a in soup.find_all("a") if a.get("href")]
                    
                    return {
                        "success": True,
                        "url": url,
                        "status_code": response.status_code,
                        "content_type": content_type,
                        "title": title,
                        "meta_tags": meta_tags,
                        "links_count": len(links),
                        "content_length": len(response.text)
                    }
                else:
                    # Non-HTML content
                    return {
                        "success": True,
                        "url": url,
                        "status_code": response.status_code,
                        "content_type": content_type,
                        "content_length": len(response.text)
                    }
                
            except requests.RequestException as e:
                logger.warning(f"Request to {url} failed (attempt {attempt+1}/{self.max_retries}): {str(e)}")
                time.sleep(1)  # Wait before retrying
        
        # All attempts failed
        self.state["last_error"] = f"Failed to visit URL after {self.max_retries} attempts"
        return {"success": False, "error": self.state["last_error"]}

    def _extract_content(self, selector: str, selector_type: str = "css", attribute: str = None) -> Dict[str, Any]:
        """Extract content from the current page using a CSS or XPath selector.

        Args:
            selector: The selector to use
            selector_type: The type of selector ('css' or 'xpath')
            attribute: The attribute to extract (if None, extracts text content)

        Returns:
            The extracted content
        """
        if not self.state["last_page_soup"]:
            return {"success": False, "error": "No page loaded"}
        
        soup = self.state["last_page_soup"]
        results = []
        
        try:
            if selector_type.lower() == "css":
                elements = soup.select(selector)
            elif selector_type.lower() == "xpath":
                from lxml import etree
                html = etree.HTML(str(soup))
                xml_elements = html.xpath(selector)
                
                # Convert lxml elements to BS4 elements
                elements = []
                for xml_el in xml_elements:
                    path = soup.find(
                        xml_el.tag, 
                        attrs={k: v for k, v in xml_el.attrib.items()}
                    )
                    if path:
                        elements.append(path)
            else:
                return {"success": False, "error": f"Unknown selector type: {selector_type}"}
            
            for element in elements:
                if attribute:
                    # Extract attribute
                    value = element.get(attribute)
                    if value:
                        results.append(value)
                else:
                    # Extract text
                    text = element.get_text(strip=True)
                    if text:
                        results.append(text)
            
            return {
                "success": True,
                "selector": selector,
                "selector_type": selector_type,
                "attribute": attribute,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error extracting content with selector {selector}: {str(e)}")
            return {"success": False, "error": str(e)}

    def _go_back(self) -> Dict[str, Any]:
        """Navigate back to the previous page in history.

        Returns:
            Result of the navigation
        """
        if len(self.state["history"]) <= 1:
            return {"success": False, "error": "No history to go back to"}
        
        # Remove current URL from history
        if self.state["current_url"] == self.state["history"][-1]:
            self.state["history"].pop()
        
        # Go to previous URL
        if self.state["history"]:
            previous_url = self.state["history"][-1]
            return self._visit_url(previous_url)
        
        return {"success": False, "error": "No previous URL in history"}

    def _search(self, query: str, engine: str = "google") -> Dict[str, Any]:
        """Perform a search using a search engine.

        Args:
            query: The search query
            engine: The search engine to use

        Returns:
            The search results page
        """
        if not query:
            return {"success": False, "error": "No search query provided"}
        
        encoded_query = urllib.parse.quote_plus(query)
        
        if engine.lower() == "google":
            url = f"https://www.google.com/search?q={encoded_query}"
        elif engine.lower() == "bing":
            url = f"https://www.bing.com/search?q={encoded_query}"
        elif engine.lower() == "duckduckgo":
            url = f"https://duckduckgo.com/?q={encoded_query}"
        else:
            return {"success": False, "error": f"Unsupported search engine: {engine}"}
        
        result = self._visit_url(url)
        
        if result["success"]:
            result["query"] = query
            result["engine"] = engine
        
        return result

    def _click_link(self, selector: str = "", selector_type: str = "css", text_match: str = None) -> Dict[str, Any]:
        """Click a link on the current page.

        Args:
            selector: CSS or XPath selector to find the link
            selector_type: Type of selector ('css' or 'xpath')
            text_match: Text to match in the link (if provided, overrides selector)

        Returns:
            Result of visiting the link
        """
        if not self.state["last_page_soup"]:
            return {"success": False, "error": "No page loaded"}
        
        soup = self.state["last_page_soup"]
        link = None
        
        try:
            if text_match:
                # Find by link text
                links = soup.find_all("a")
                for a in links:
                    if text_match.lower() in a.get_text().lower():
                        link = a
                        break
            elif selector:
                # Find by selector
                if selector_type.lower() == "css":
                    elements = soup.select(selector)
                elif selector_type.lower() == "xpath":
                    from lxml import etree
                    html = etree.HTML(str(soup))
                    xml_elements = html.xpath(selector)
                    
                    # Get the first element and find it in BeautifulSoup
                    if xml_elements:
                        el = xml_elements[0]
                        elements = [soup.find(
                            el.tag, 
                            attrs={k: v for k, v in el.attrib.items()}
                        )]
                    else:
                        elements = []
                else:
                    return {"success": False, "error": f"Unknown selector type: {selector_type}"}
                
                if elements:
                    link = elements[0]
            
            if not link:
                return {"success": False, "error": "Link not found"}
            
            href = link.get("href")
            if not href:
                return {"success": False, "error": "Link has no href attribute"}
            
            # Handle relative URLs
            if not href.startswith(("http://", "https://", "mailto:", "tel:")):
                base_url = self.state["current_url"]
                if base_url:
                    parsed_base = urllib.parse.urlparse(base_url)
                    base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
                    
                    if href.startswith("/"):
                        href = f"{base_domain}{href}"
                    else:
                        href = f"{base_domain}/{href}"
            
            if href.startswith(("mailto:", "tel:")):
                return {
                    "success": True,
                    "message": f"Not following non-HTTP link: {href}",
                    "href": href
                }
            
            # Visit the link
            return self._visit_url(href)
            
        except Exception as e:
            logger.error(f"Error clicking link: {str(e)}")
            return {"success": False, "error": str(e)}

    def _get_links(self) -> Dict[str, Any]:
        """Get all links from the current page.

        Returns:
            List of links with their text and href attributes
        """
        if not self.state["last_page_soup"]:
            return {"success": False, "error": "No page loaded"}
        
        soup = self.state["last_page_soup"]
        links = []
        
        try:
            for a in soup.find_all("a", href=True):
                href = a.get("href")
                text = a.get_text(strip=True)
                
                if href:
                    # Handle relative URLs
                    if not href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:")):
                        base_url = self.state["current_url"]
                        if base_url:
                            parsed_base = urllib.parse.urlparse(base_url)
                            base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
                            
                            if href.startswith("/"):
                                href = f"{base_domain}{href}"
                            else:
                                href = f"{base_domain}/{href}"
                    
                    links.append({
                        "text": text or "[No text]",
                        "href": href,
                        "title": a.get("title", ""),
                        "is_external": not (self.state["current_url"] and href.startswith(self.state["current_url"]))
                    })
            
            return {
                "success": True,
                "links": links,
                "count": len(links),
                "current_url": self.state["current_url"]
            }
            
        except Exception as e:
            logger.error(f"Error getting links: {str(e)}")
            return {"success": False, "error": str(e)}

    def _get_images(self) -> Dict[str, Any]:
        """Get all images from the current page.

        Returns:
            List of images with their src, alt, and other attributes
        """
        if not self.state["last_page_soup"]:
            return {"success": False, "error": "No page loaded"}
        
        soup = self.state["last_page_soup"]
        images = []
        
        try:
            for img in soup.find_all("img"):
                src = img.get("src", "")
                
                if src:
                    # Handle relative URLs
                    if not src.startswith(("http://", "https://", "data:")):
                        base_url = self.state["current_url"]
                        if base_url:
                            parsed_base = urllib.parse.urlparse(base_url)
                            base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
                            
                            if src.startswith("/"):
                                src = f"{base_domain}{src}"
                            else:
                                src = f"{base_domain}/{src}"
                    
                    images.append({
                        "src": src,
                        "alt": img.get("alt", ""),
                        "width": img.get("width", ""),
                        "height": img.get("height", ""),
                        "title": img.get("title", "")
                    })
            
            return {
                "success": True,
                "images": images,
                "count": len(images),
                "current_url": self.state["current_url"]
            }
            
        except Exception as e:
            logger.error(f"Error getting images: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_observation(self) -> Dict[str, Any]:
        """Get the current state of the web environment.

        Returns:
            The current state
        """
        return {
            "current_url": self.state["current_url"],
            "history_count": len(self.state["history"]),
            "last_error": self.state["last_error"]
        }

    def reset(self) -> Dict[str, Any]:
        """Reset the environment state.

        Returns:
            The initial state
        """
        self.state = {
            "current_url": None,
            "history": [],
            "cookies": {},
            "last_page_content": None,
            "last_page_soup": None,
            "last_error": None
        }
        return self.get_observation()
    
    async def __aenter__(self):
        """Async context manager enter."""
        await self.create_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close_session() 