# Web Environment

The `WebEnvironment` provides browser-like capabilities for agents to interact with web pages, extract content, and navigate websites through a consistent interface.

## Overview

Web browsing is a critical capability for agents that need to access online information. The `WebEnvironment` provides a simplified browser interface to:

- Visit and navigate web pages
- Extract content using CSS or XPath selectors
- Interact with page elements
- Capture screenshots
- Manage browser state and cookies
- Follow links and navigate site structures

## Initialization

```python
from agi_mcp_agent.environment import WebEnvironment

# Basic initialization
web_env = WebEnvironment(
    name="example-web"
)

# With advanced options
web_env = WebEnvironment(
    name="custom-web",
    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    viewport_size={"width": 1920, "height": 1080},
    timeout=30,
    headless=True,
    cookies_enabled=True
)
```

## Basic Operations

### Visiting Web Pages

```python
# Visit a URL
result = web_env.execute_action({
    "operation": "visit",
    "url": "https://example.com"
})

# Access the page information
if result["success"]:
    title = result["title"]
    url = result["url"]
    status_code = result["status_code"]
    content_type = result["content_type"]
    
    print(f"Page title: {title}")
    print(f"Final URL: {url}")  # May differ if redirected
    print(f"Status code: {status_code}")
else:
    print(f"Error: {result['error']}")
```

### Extracting Content

```python
# Extract text using CSS selectors
extract_result = web_env.execute_action({
    "operation": "extract_content",
    "selector": "h1, p.summary",
    "selector_type": "css"
})

# Access the extracted content
if extract_result["success"]:
    elements = extract_result["content"]
    for i, element in enumerate(elements):
        print(f"Element {i+1}: {element}")
else:
    print(f"Error: {extract_result['error']}")

# Extract text using XPath
xpath_result = web_env.execute_action({
    "operation": "extract_content",
    "selector": "//div[@class='article']/p",
    "selector_type": "xpath"
})
```

### Finding Links

```python
# Find links on a page
links_result = web_env.execute_action({
    "operation": "get_links",
    "filter": {
        "text_contains": "Documentation",
        "href_contains": "/docs"
    }
})

# Access the links
if links_result["success"]:
    links = links_result["links"]
    for link in links:
        print(f"Link: {link['text']} - {link['href']}")
else:
    print(f"Error: {links_result['error']}")
```

### Capturing Screenshots

```python
# Capture a full-page screenshot
screenshot_result = web_env.execute_action({
    "operation": "screenshot",
    "output_path": "screenshots/example.png",
    "full_page": True
})

# Capture a specific element
element_screenshot = web_env.execute_action({
    "operation": "screenshot",
    "output_path": "screenshots/header.png",
    "selector": "header.main-header",
    "selector_type": "css"
})
```

## Advanced Features

### Navigation

```python
# Navigate back and forward
back_result = web_env.execute_action({
    "operation": "back"
})

forward_result = web_env.execute_action({
    "operation": "forward"
})

# Refresh the current page
refresh_result = web_env.execute_action({
    "operation": "refresh"
})
```

### Interacting with Forms

```python
# Fill out a form field
fill_result = web_env.execute_action({
    "operation": "fill_field",
    "selector": "input[name='search']",
    "value": "artificial intelligence"
})

# Click a button
click_result = web_env.execute_action({
    "operation": "click",
    "selector": "button.search-submit"
})

# Submit a form
submit_result = web_env.execute_action({
    "operation": "submit_form",
    "selector": "form#search-form"
})
```

### Waiting for Elements

```python
# Wait for an element to appear
wait_result = web_env.execute_action({
    "operation": "wait_for_element",
    "selector": ".results-container",
    "timeout": 10  # seconds
})

# Wait for navigation to complete
nav_wait = web_env.execute_action({
    "operation": "wait_for_navigation",
    "url_contains": "results",
    "timeout": 5  # seconds
})
```

### Cookie Management

```python
# Get all cookies
cookies_result = web_env.execute_action({
    "operation": "get_cookies"
})
if cookies_result["success"]:
    cookies = cookies_result["cookies"]
    for cookie in cookies:
        print(f"Cookie: {cookie['name']} = {cookie['value']}")

# Set a cookie
set_cookie = web_env.execute_action({
    "operation": "set_cookie",
    "name": "user_preference",
    "value": "dark_mode",
    "domain": "example.com",
    "path": "/"
})

# Clear cookies
clear_cookies = web_env.execute_action({
    "operation": "clear_cookies"
})
```

### Executing JavaScript

```python
# Execute JavaScript on the page
js_result = web_env.execute_action({
    "operation": "execute_javascript",
    "script": "return document.title;"
})
if js_result["success"]:
    result = js_result["result"]
    print(f"JavaScript result: {result}")
```

## Working with Tables

```python
# Extract table data
table_result = web_env.execute_action({
    "operation": "extract_table",
    "selector": "table.data-table",
    "include_headers": True
})
if table_result["success"]:
    headers = table_result["headers"]
    rows = table_result["rows"]
    
    print(f"Table headers: {headers}")
    for row in rows:
        print(f"Row: {row}")
```

## Handling Authentication

```python
# Login to a website
login_result = web_env.execute_action({
    "operation": "login",
    "url": "https://example.com/login",
    "username_selector": "input[name='username']",
    "password_selector": "input[name='password']",
    "submit_selector": "button[type='submit']",
    "username": "user@example.com",
    "password": "secure-password",
    "success_indicator": ".welcome-message"
})
```

## Security Features

The `WebEnvironment` implements several security features:

- **URL validation**: Restricts navigation to allowed domains and schemes
- **Cookie isolation**: Maintains cookies separate from the system browser
- **Credential masking**: Masks sensitive information in logs
- **Resource limitations**: Controls JavaScript execution and resource loading
- **Content security**: Implements content security policies to prevent malicious code execution

## Handling Errors

The environment provides detailed error information:

```python
# Handle various error scenarios
try:
    result = web_env.execute_action({
        "operation": "visit",
        "url": "https://nonexistent-site.example"
    })
    
    if not result["success"]:
        error_type = result["error_type"]
        error_message = result["error"]
        
        if error_type == "connection":
            print(f"Connection error: {error_message}")
        elif error_type == "timeout":
            print(f"Timeout error: {error_message}")
        elif error_type == "navigation":
            print(f"Navigation error: {error_message}")
        else:
            print(f"Other error: {error_message}")
except Exception as e:
    print(f"Unexpected error: {str(e)}")
```

## Example Usage

Complete example of using the `WebEnvironment`:

```python
from agi_mcp_agent.environment import WebEnvironment

# Initialize the environment
web_env = WebEnvironment(
    name="example-web",
    headless=True  # Run browser in headless mode
)

try:
    # Visit a website
    visit_result = web_env.execute_action({
        "operation": "visit",
        "url": "https://example.com"
    })
    print(f"Page title: {visit_result['title']}")
    
    # Extract content
    content_result = web_env.execute_action({
        "operation": "extract_content",
        "selector": "p",
        "selector_type": "css"
    })
    
    # Print extracted paragraphs
    if content_result["success"]:
        paragraphs = content_result["content"]
        for i, p in enumerate(paragraphs):
            print(f"Paragraph {i+1}: {p}")
    
    # Get links
    links_result = web_env.execute_action({
        "operation": "get_links"
    })
    
    if links_result["success"]:
        links = links_result["links"]
        print(f"Found {len(links)} links on the page")
        for link in links[:3]:  # Show first 3 links
            print(f"Link: {link['text']} -> {link['href']}")
    
finally:
    # Clean up resources
    web_env.close() 