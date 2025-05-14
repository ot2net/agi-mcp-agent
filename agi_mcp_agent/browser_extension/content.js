/**
 * MCP Google Search Assistant - Content Script
 * 
 * This script runs on Google search result pages and provides search recommendations
 * powered by MCP (Model Context Protocol).
 */

// Configuration
const DEFAULT_MCP_SERVER = "ws://localhost:8080/ws";
const CONFIG_KEY = "mcp_google_assistant_config";

// State management
let mcpConnection = null;
let currentQuery = "";
let pendingRecommendations = false;
let lastRequestId = 0;
let pendingRequests = {};

// DOM elements
let recommendationsContainer = null;

/**
 * Initialize the content script
 */
function initialize() {
  console.log("MCP Google Search Assistant: Initializing content script");
  
  // Extract search query
  extractSearchQuery();
  
  // Create recommendations UI
  createRecommendationsUI();
  
  // Connect to MCP server
  loadConfiguration().then(config => {
    connectToMCPServer(config.mcpServer || DEFAULT_MCP_SERVER);
  });
  
  // Set up mutation observer to handle Google's dynamic content loading
  setupMutationObserver();
}

/**
 * Extract the current search query from the URL
 */
function extractSearchQuery() {
  const urlParams = new URLSearchParams(window.location.search);
  currentQuery = urlParams.get('q') || "";
  console.log(`MCP Google Search Assistant: Detected search query "${currentQuery}"`);
}

/**
 * Create the recommendations UI
 */
function createRecommendationsUI() {
  // Create container for recommendations
  recommendationsContainer = document.createElement('div');
  recommendationsContainer.id = 'mcp-recommendations';
  recommendationsContainer.className = 'mcp-recommendations-container';
  
  // Initial state - loading
  recommendationsContainer.innerHTML = `
    <div class="mcp-recommendations-header">
      <img src="${chrome.runtime.getURL('icons/icon48.png')}" alt="MCP" class="mcp-logo">
      <h3>AI-Powered Recommendations</h3>
    </div>
    <div class="mcp-recommendations-content">
      <div class="mcp-loading">
        <div class="mcp-spinner"></div>
        <p>Analyzing search results...</p>
      </div>
    </div>
  `;
  
  // Insert into the page
  const searchContainer = document.getElementById('search');
  if (searchContainer) {
    // Insert after the search box but before results
    const rightColumn = document.getElementById('rhs');
    if (rightColumn) {
      rightColumn.prepend(recommendationsContainer);
    } else {
      // If no right column, create one
      const resultsContainer = document.getElementById('rcnt');
      if (resultsContainer) {
        const rightPanel = document.createElement('div');
        rightPanel.id = 'rhs';
        rightPanel.className = 'mcp-custom-rhs';
        rightPanel.appendChild(recommendationsContainer);
        resultsContainer.appendChild(rightPanel);
      }
    }
  } else {
    // Fallback insertion
    document.body.appendChild(recommendationsContainer);
  }
}

/**
 * Update the recommendations UI with new recommendations
 */
function updateRecommendationsUI(recommendations) {
  if (!recommendationsContainer) {
    createRecommendationsUI();
  }
  
  // Generate HTML for recommendations
  let recommendationsHTML = `
    <div class="mcp-recommendations-header">
      <img src="${chrome.runtime.getURL('icons/icon48.png')}" alt="MCP" class="mcp-logo">
      <h3>AI-Powered Recommendations</h3>
    </div>
    <div class="mcp-recommendations-content">
  `;
  
  if (recommendations.length === 0) {
    recommendationsHTML += `
      <div class="mcp-no-recommendations">
        <p>No recommendations available for this search.</p>
      </div>
    `;
  } else {
    recommendationsHTML += `<ul class="mcp-recommendations-list">`;
    
    for (const rec of recommendations) {
      recommendationsHTML += `
        <li class="mcp-recommendation-item">
          <a href="${rec.url}" class="mcp-recommendation-link" target="_blank">
            <h4 class="mcp-recommendation-title">${rec.title}</h4>
            <p class="mcp-recommendation-snippet">${rec.snippet}</p>
            <div class="mcp-recommendation-reason">
              <span class="mcp-reason-label">Why this is recommended:</span>
              <span class="mcp-reason-text">${rec.reason}</span>
            </div>
          </a>
        </li>
      `;
    }
    
    recommendationsHTML += `</ul>`;
  }
  
  recommendationsHTML += `
      <div class="mcp-recommendations-footer">
        <p>Powered by MCP Protocol</p>
      </div>
    </div>
  `;
  
  recommendationsContainer.innerHTML = recommendationsHTML;
  
  // Add highlight effect for recommended links in search results
  highlightRecommendedResults(recommendations);
}

/**
 * Highlight recommended results in the main search results
 */
function highlightRecommendedResults(recommendations) {
  // Extract URLs from recommendations
  const recommendedUrls = recommendations.map(rec => rec.url);
  
  // Find matching results in the page
  const searchResults = document.querySelectorAll('a[href^="http"]');
  
  searchResults.forEach(link => {
    const href = link.getAttribute('href');
    if (recommendedUrls.some(url => href.startsWith(url))) {
      // Find the result container
      let resultContainer = link;
      while (resultContainer && !resultContainer.matches('.g, .xpd')) {
        resultContainer = resultContainer.parentElement;
      }
      
      if (resultContainer) {
        resultContainer.classList.add('mcp-recommended-result');
        
        // Add badge
        if (!resultContainer.querySelector('.mcp-recommendation-badge')) {
          const badge = document.createElement('div');
          badge.className = 'mcp-recommendation-badge';
          badge.textContent = 'Recommended';
          resultContainer.appendChild(badge);
        }
      }
    }
  });
}

/**
 * Connect to MCP server via WebSocket
 */
function connectToMCPServer(url) {
  try {
    console.log(`MCP Google Search Assistant: Connecting to MCP server at ${url}`);
    
    // Close existing connection if any
    if (mcpConnection) {
      mcpConnection.close();
    }
    
    // Create new connection
    mcpConnection = new WebSocket(url);
    
    // Set up event handlers
    mcpConnection.onopen = () => {
      console.log("MCP Google Search Assistant: Connected to MCP server");
      initializeMCPConnection();
    };
    
    mcpConnection.onclose = (event) => {
      console.log(`MCP Google Search Assistant: Disconnected from MCP server (${event.code})`);
      mcpConnection = null;
      
      // Update UI
      if (recommendationsContainer) {
        recommendationsContainer.innerHTML = `
          <div class="mcp-recommendations-header">
            <img src="${chrome.runtime.getURL('icons/icon48.png')}" alt="MCP" class="mcp-logo">
            <h3>AI-Powered Recommendations</h3>
          </div>
          <div class="mcp-recommendations-content">
            <div class="mcp-error">
              <p>Connection to MCP server lost. Please check your configuration.</p>
              <button id="mcp-reconnect-button">Reconnect</button>
            </div>
          </div>
        `;
        
        // Add event listener to reconnect button
        const reconnectButton = document.getElementById('mcp-reconnect-button');
        if (reconnectButton) {
          reconnectButton.addEventListener('click', () => {
            loadConfiguration().then(config => {
              connectToMCPServer(config.mcpServer || DEFAULT_MCP_SERVER);
            });
          });
        }
      }
    };
    
    mcpConnection.onerror = (error) => {
      console.error("MCP Google Search Assistant: Connection error", error);
    };
    
    mcpConnection.onmessage = (event) => {
      handleMCPMessage(event.data);
    };
  } catch (error) {
    console.error("MCP Google Search Assistant: Error connecting to MCP server", error);
  }
}

/**
 * Initialize MCP connection after WebSocket is connected
 */
function initializeMCPConnection() {
  // Send initialize request
  sendMCPRequest("initialize", {
    clientInfo: {
      name: "MCP Google Search Assistant",
      version: "1.0.0"
    }
  }).then(response => {
    console.log("MCP Google Search Assistant: Server initialized", response);
    // Get capabilities
    return sendMCPRequest("capabilities");
  }).then(response => {
    console.log("MCP Google Search Assistant: Server capabilities", response);
    // List available tools
    return sendMCPRequest("listTools");
  }).then(response => {
    console.log("MCP Google Search Assistant: Available tools", response);
    
    // Check if required tools are available
    const tools = response.tools || [];
    const hasGoogleSearch = tools.some(tool => tool.name === "google_search");
    const hasAnalyze = tools.some(tool => tool.name === "analyze_search_results");
    
    if (hasGoogleSearch && hasAnalyze && currentQuery) {
      // Analyze current search results
      analyzeSearchResults();
    } else {
      console.warn("MCP Google Search Assistant: Required tools not available");
      
      // Update UI
      if (recommendationsContainer) {
        recommendationsContainer.innerHTML = `
          <div class="mcp-recommendations-header">
            <img src="${chrome.runtime.getURL('icons/icon48.png')}" alt="MCP" class="mcp-logo">
            <h3>AI-Powered Recommendations</h3>
          </div>
          <div class="mcp-recommendations-content">
            <div class="mcp-error">
              <p>Required MCP capabilities not available on the server.</p>
            </div>
          </div>
        `;
      }
    }
  }).catch(error => {
    console.error("MCP Google Search Assistant: Error during initialization", error);
  });
}

/**
 * Handle a message from the MCP server
 */
function handleMCPMessage(data) {
  try {
    const message = JSON.parse(data);
    console.log("MCP Google Search Assistant: Received message", message);
    
    // Check if this is a response to a pending request
    const requestId = message.id;
    if (requestId && pendingRequests[requestId]) {
      const { resolve, reject } = pendingRequests[requestId];
      delete pendingRequests[requestId];
      
      if (message.error) {
        reject(message.error);
      } else {
        resolve(message.result);
      }
    }
  } catch (error) {
    console.error("MCP Google Search Assistant: Error handling message", error, data);
  }
}

/**
 * Send a request to the MCP server
 */
function sendMCPRequest(method, params = {}) {
  return new Promise((resolve, reject) => {
    if (!mcpConnection || mcpConnection.readyState !== WebSocket.OPEN) {
      reject(new Error("Not connected to MCP server"));
      return;
    }
    
    const requestId = ++lastRequestId;
    
    const request = {
      jsonrpc: "2.0",
      method: method,
      params: params,
      id: requestId
    };
    
    // Store the promise callbacks
    pendingRequests[requestId] = { resolve, reject };
    
    // Send the request
    mcpConnection.send(JSON.stringify(request));
  });
}

/**
 * Analyze the current search results
 */
function analyzeSearchResults() {
  if (!currentQuery || pendingRecommendations) {
    return;
  }
  
  pendingRecommendations = true;
  
  // Execute the analysis tool
  console.log(`MCP Google Search Assistant: Analyzing search results for "${currentQuery}"`);
  
  sendMCPRequest("executeTool", {
    name: "analyze_search_results",
    arguments: {
      query: currentQuery,
      criteria: ["relevance", "authority", "recency"],
      count: 3
    }
  }).then(result => {
    pendingRecommendations = false;
    console.log("MCP Google Search Assistant: Analysis complete", result);
    
    if (result.success && result.recommendations) {
      updateRecommendationsUI(result.recommendations);
    } else {
      throw new Error("Failed to get recommendations");
    }
  }).catch(error => {
    pendingRecommendations = false;
    console.error("MCP Google Search Assistant: Error analyzing search results", error);
    
    // Update UI with error
    if (recommendationsContainer) {
      recommendationsContainer.innerHTML = `
        <div class="mcp-recommendations-header">
          <img src="${chrome.runtime.getURL('icons/icon48.png')}" alt="MCP" class="mcp-logo">
          <h3>AI-Powered Recommendations</h3>
        </div>
        <div class="mcp-recommendations-content">
          <div class="mcp-error">
            <p>Error analyzing search results. Please try again later.</p>
            <button id="mcp-retry-button">Retry</button>
          </div>
        </div>
      `;
      
      // Add event listener to retry button
      const retryButton = document.getElementById('mcp-retry-button');
      if (retryButton) {
        retryButton.addEventListener('click', () => {
          analyzeSearchResults();
        });
      }
    }
  });
}

/**
 * Load extension configuration from storage
 */
function loadConfiguration() {
  return new Promise(resolve => {
    chrome.storage.sync.get(CONFIG_KEY, (data) => {
      const config = data[CONFIG_KEY] || { mcpServer: DEFAULT_MCP_SERVER };
      resolve(config);
    });
  });
}

/**
 * Set up mutation observer to monitor for dynamic content changes
 */
function setupMutationObserver() {
  // Create a mutation observer to detect when the page is updated
  const observer = new MutationObserver((mutations) => {
    // Check if the URL has changed
    const urlParams = new URLSearchParams(window.location.search);
    const newQuery = urlParams.get('q') || "";
    
    if (newQuery !== currentQuery) {
      currentQuery = newQuery;
      console.log(`MCP Google Search Assistant: Query changed to "${currentQuery}"`);
      
      // Delay slightly to ensure the page has loaded
      setTimeout(() => {
        // Reconnect to MCP server if needed
        if (!mcpConnection || mcpConnection.readyState !== WebSocket.OPEN) {
          loadConfiguration().then(config => {
            connectToMCPServer(config.mcpServer || DEFAULT_MCP_SERVER);
          });
        } else {
          analyzeSearchResults();
        }
      }, 500);
    }
  });
  
  // Observe changes to the URL
  observer.observe(document, { subtree: true, childList: true });
}

// Initialize when the DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  initialize();
} 