"""Browser MCP environment implementation for agent interactions with browser and Google search."""

import json
import logging
import time
from typing import Any, Dict, List, Optional
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup

from agi_mcp_agent.environment.base import Environment
from agi_mcp_agent.environment.web_environment import WebEnvironment

logger = logging.getLogger(__name__)


class BrowserMCPEnvironment(Environment):
    """Environment that provides access to browser and Google search with MCP capabilities."""

    def __init__(
        self, 
        name: str, 
        headers: Dict[str, str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        user_agent: str = None,
        recommendation_count: int = 3
    ):
        """Initialize the browser MCP environment.

        Args:
            name: The name of the environment
            headers: Default headers to use for HTTP requests
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            user_agent: User agent string to use (if None, a default is provided)
            recommendation_count: Number of recommendations to generate
        """
        super().__init__(name)
        
        # Create a web environment instance for web operations
        self.web_env = WebEnvironment(
            name=f"{name}-web",
            headers=headers,
            timeout=timeout,
            max_retries=max_retries,
            user_agent=user_agent
        )
        
        self.recommendation_count = recommendation_count
        
        # State management
        self.state = {
            "last_search_query": None,
            "last_search_results": None,
            "last_recommendations": None,
            "last_error": None
        }
        
        logger.info(f"Browser MCP Environment {self.name} initialized")
    
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a browser MCP action.

        Args:
            action: The action to execute with the following keys:
                - operation: The operation to perform (google_search, analyze_results, etc.)
                - additional operation-specific parameters

        Returns:
            The result of the operation
        """
        operation = action.get("operation", "").lower()
        
        try:
            if operation == "google_search":
                return self._google_search(
                    query=action.get("query", ""),
                    num_results=action.get("num_results", 10)
                )
            elif operation == "analyze_results":
                return self._analyze_results(
                    query=action.get("query", ""),
                    results=action.get("results", None),
                    criteria=action.get("criteria", None)
                )
            elif operation == "generate_recommendations":
                return self._generate_recommendations(
                    query=action.get("query", ""),
                    results=action.get("results", None),
                    analysis=action.get("analysis", None),
                    count=action.get("count", self.recommendation_count)
                )
            elif operation == "browse_url":
                return self._browse_url(
                    url=action.get("url", ""),
                    extract_content=action.get("extract_content", True)
                )
            else:
                logger.warning(f"Unknown browser MCP operation: {operation}")
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            logger.error(f"Error in browser MCP operation {operation}: {str(e)}")
            self.state["last_error"] = str(e)
            return {"success": False, "error": str(e)}
    
    def _google_search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform a Google search.

        Args:
            query: The search query
            num_results: Number of results to return

        Returns:
            The search results and metadata
        """
        if not query:
            return {"success": False, "error": "No search query provided"}
        
        # Use the web environment to perform the search
        search_action = {
            "action_type": "search",
            "query": query,
            "engine": "google"
        }
        
        search_result = self.web_env.execute_action(search_action)
        
        if not search_result.get("success", False):
            return search_result
        
        # Extract search results
        soup = BeautifulSoup(search_result.get("content", ""), "html.parser")
        results = []
        
        # Process search results
        result_elements = soup.select("div.g")[:num_results]
        
        for elem in result_elements:
            try:
                title_elem = elem.select_one("h3")
                link_elem = elem.select_one("a")
                snippet_elem = elem.select_one("div.VwiC3b")
                
                if title_elem and link_elem:
                    title = title_elem.get_text()
                    link = link_elem.get("href")
                    snippet = snippet_elem.get_text() if snippet_elem else ""
                    
                    if link and link.startswith("http"):
                        results.append({
                            "title": title,
                            "url": link,
                            "snippet": snippet
                        })
            except Exception as e:
                logger.error(f"Error extracting search result: {str(e)}")
        
        # Store results in state
        self.state["last_search_query"] = query
        self.state["last_search_results"] = results
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "results_count": len(results)
        }
    
    def _analyze_results(self, query: str = None, results: List[Dict[str, Any]] = None, criteria: List[str] = None) -> Dict[str, Any]:
        """Analyze search results based on criteria.

        Args:
            query: The original search query (optional if results are provided)
            results: Search results to analyze (optional, will use last results if None)
            criteria: List of criteria to use for analysis (default: relevance, authority, recency)

        Returns:
            Analysis of the search results
        """
        # Use provided results or last results from state
        if results is None:
            results = self.state.get("last_search_results", [])
            if not results:
                # If no results in state, try to perform a search if query is provided
                if query:
                    search_result = self._google_search(query)
                    if search_result.get("success", False):
                        results = search_result.get("results", [])
                
                if not results:
                    return {"success": False, "error": "No search results available for analysis"}
        
        # Use default criteria if none provided
        if criteria is None:
            criteria = ["relevance", "authority", "recency"]
        
        analysis = {}
        
        # Perform basic analysis on each result
        for i, result in enumerate(results):
            result_analysis = {}
            
            # Basic analysis based on criteria
            for criterion in criteria:
                if criterion == "relevance":
                    # Simple relevance score based on keyword presence in title/snippet
                    score = 0
                    if query:
                        keywords = set(query.lower().split())
                        title_words = set(result.get("title", "").lower().split())
                        snippet_words = set(result.get("snippet", "").lower().split())
                        
                        common_title = keywords.intersection(title_words)
                        common_snippet = keywords.intersection(snippet_words)
                        
                        score = (len(common_title) * 2 + len(common_snippet)) / (len(keywords) * 3)
                        score = min(score * 10, 10)  # Scale to 0-10
                    
                    result_analysis["relevance"] = score
                    
                elif criterion == "authority":
                    # Simple authority heuristic based on domain
                    url = result.get("url", "")
                    domain = urllib.parse.urlparse(url).netloc
                    
                    # Very basic authority scoring
                    authority_score = 5  # Default score
                    
                    # Educational or government domains
                    if domain.endswith((".edu", ".gov", ".org")):
                        authority_score = 8
                    # Well-known domains (simplified example)
                    elif any(known in domain for known in ["wikipedia", "github", "medium", "stackoverflow"]):
                        authority_score = 7
                    
                    result_analysis["authority"] = authority_score
                    
                elif criterion == "recency":
                    # For recency, we would need to visit each page and extract dates
                    # This is a simplified version that defaults to a neutral score
                    result_analysis["recency"] = 5  # Default neutral score
            
            analysis[f"result_{i+1}"] = {
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "analysis": result_analysis
            }
        
        return {
            "success": True,
            "analysis": analysis,
            "criteria": criteria
        }
    
    def _generate_recommendations(self, query: str = None, results: List[Dict[str, Any]] = None, 
                                analysis: Dict[str, Any] = None, count: int = 3) -> Dict[str, Any]:
        """Generate recommendations based on analyzed results.

        Args:
            query: The original search query (optional)
            results: Search results (optional, will use last results if None)
            analysis: Analysis of results (optional, will perform analysis if None)
            count: Number of recommendations to generate

        Returns:
            List of recommended results with reasons
        """
        # Use provided analysis or generate if not provided
        if analysis is None:
            analysis_result = self._analyze_results(query, results)
            if not analysis_result.get("success", False):
                return analysis_result
            
            analysis = analysis_result.get("analysis", {})
        
        # Use provided results or last results from state
        if results is None:
            results = self.state.get("last_search_results", [])
        
        if not results or not analysis:
            return {"success": False, "error": "Insufficient data for generating recommendations"}
        
        # Process and rank results
        ranked_results = []
        
        for key, item in analysis.items():
            if not key.startswith("result_"):
                continue
                
            idx = int(key.split("_")[1]) - 1
            if idx < len(results):
                result = results[idx]
                
                # Calculate composite score
                item_analysis = item.get("analysis", {})
                composite_score = sum(item_analysis.values()) / len(item_analysis) if item_analysis else 0
                
                ranked_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "snippet": result.get("snippet", ""),
                    "score": composite_score,
                    "analysis": item_analysis
                })
        
        # Sort by composite score
        ranked_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Generate recommendations with reasoning
        recommendations = []
        for i, result in enumerate(ranked_results[:count]):
            # Generate reason based on analysis
            reason_parts = []
            
            analysis_data = result.get("analysis", {})
            
            if "relevance" in analysis_data and analysis_data["relevance"] > 7:
                reason_parts.append("highly relevant to your search query")
            elif "relevance" in analysis_data and analysis_data["relevance"] > 5:
                reason_parts.append("relevant to your search query")
                
            if "authority" in analysis_data and analysis_data["authority"] > 7:
                reason_parts.append("from a trustworthy source")
                
            if "recency" in analysis_data and analysis_data["recency"] > 7:
                reason_parts.append("contains recent information")
            
            # Default reason if nothing specific stands out
            if not reason_parts:
                reason = "This result may answer your query based on overall quality"
            else:
                reason = f"This result is {', '.join(reason_parts[:-1])}{' and ' if len(reason_parts) > 1 else ''}{reason_parts[-1] if reason_parts else ''}"
            
            recommendations.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "snippet": result.get("snippet", ""),
                "reason": reason
            })
        
        # Store recommendations in state
        self.state["last_recommendations"] = recommendations
        
        return {
            "success": True,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    
    def _browse_url(self, url: str, extract_content: bool = True) -> Dict[str, Any]:
        """Browse a URL and optionally extract content.

        Args:
            url: The URL to browse
            extract_content: Whether to extract and analyze the content

        Returns:
            The browsing result
        """
        # Use the web environment to visit the URL
        visit_action = {
            "action_type": "visit",
            "url": url,
            "parse": extract_content
        }
        
        visit_result = self.web_env.execute_action(visit_action)
        
        if not visit_result.get("success", False):
            return visit_result
            
        if not extract_content:
            return visit_result
            
        # Extract main content (simplified)
        soup = BeautifulSoup(visit_result.get("content", ""), "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        
        # Clean text (remove excessive newlines, etc.)
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r'\s+', ' ', text)
        
        return {
            "success": True,
            "url": url,
            "title": visit_result.get("title", ""),
            "content": text[:5000] + "..." if len(text) > 5000 else text,  # Truncate long content
            "full_content_length": len(text)
        }
    
    def get_observation(self) -> Dict[str, Any]:
        """Get the current state of the browser MCP environment.

        Returns:
            The current state
        """
        return {
            "last_search_query": self.state.get("last_search_query"),
            "results_count": len(self.state.get("last_search_results", [])),
            "recommendations_count": len(self.state.get("last_recommendations", [])),
            "last_error": self.state.get("last_error")
        }
    
    def reset(self) -> Dict[str, Any]:
        """Reset the environment state.

        Returns:
            The initial state
        """
        self.state = {
            "last_search_query": None,
            "last_search_results": None,
            "last_recommendations": None,
            "last_error": None
        }
        
        # Also reset the underlying web environment
        self.web_env.reset()
        
        return self.get_observation()
        
    def close(self) -> None:
        """Close all connections."""
        self.web_env.close()
        logger.info(f"Closed Browser MCP environment {self.name}") 