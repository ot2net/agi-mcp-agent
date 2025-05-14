/**
 * MCP Google Search Assistant - Popup Script
 */

// Configuration
const CONFIG_KEY = "mcp_google_assistant_config";
const DEFAULT_MCP_SERVER = "ws://localhost:8080/ws";

// DOM elements
const serverInput = document.getElementById('mcp-server');
const saveButton = document.getElementById('save-button');
const statusIndicator = document.getElementById('status-indicator');
const statusText = document.getElementById('status-text');
const serverError = document.getElementById('server-error');
const statsSection = document.getElementById('stats-section');
const lastQueryElem = document.getElementById('last-query');
const recommendationsCountElem = document.getElementById('recommendations-count');
const connectionStatusElem = document.getElementById('connection-status');

// Initialize popup
document.addEventListener('DOMContentLoaded', async () => {
  // Load configuration
  const config = await loadConfiguration();
  
  // Set input values
  serverInput.value = config.mcpServer || DEFAULT_MCP_SERVER;
  
  // Check connection status
  checkConnectionStatus();
  
  // Set up event listeners
  saveButton.addEventListener('click', saveConfiguration);
  serverInput.addEventListener('input', () => {
    serverError.style.display = 'none';
  });
});

/**
 * Load extension configuration from storage
 */
async function loadConfiguration() {
  return new Promise(resolve => {
    chrome.storage.sync.get(CONFIG_KEY, (data) => {
      const config = data[CONFIG_KEY] || { mcpServer: DEFAULT_MCP_SERVER };
      resolve(config);
    });
  });
}

/**
 * Save extension configuration to storage
 */
async function saveConfiguration() {
  // Get values from inputs
  const mcpServer = serverInput.value.trim();
  
  // Validate
  if (!isValidWebSocketUrl(mcpServer)) {
    serverError.textContent = 'Please enter a valid WebSocket URL (starts with ws:// or wss://)';
    serverError.style.display = 'block';
    return;
  }
  
  // Save to storage
  const config = {
    mcpServer: mcpServer
  };
  
  chrome.storage.sync.set({ [CONFIG_KEY]: config }, () => {
    console.log('Configuration saved');
    
    // Update status
    updateStatus('Saved, connecting...', 'disconnected');
    
    // Notify content script
    notifyContentScript();
    
    // Check connection after a delay
    setTimeout(checkConnectionStatus, 1000);
  });
}

/**
 * Notify content script about configuration change
 */
function notifyContentScript() {
  // Send message to content script
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs.length > 0) {
      chrome.tabs.sendMessage(tabs[0].id, { action: 'config_updated' })
        .catch(() => console.log('No content script listening'));
    }
  });
}

/**
 * Check the connection status of the MCP server
 */
async function checkConnectionStatus() {
  try {
    // Query active tab
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (tabs.length === 0) {
      updateStatus('Unknown', 'disconnected');
      return;
    }
    
    // Send message to content script
    const response = await chrome.tabs.sendMessage(tabs[0].id, { action: 'get_status' })
      .catch(() => ({ connected: false }));
    
    // Update status based on response
    if (response && response.connected) {
      updateStatus('Connected', 'connected');
      updateStats(response.stats || {});
    } else {
      updateStatus('Disconnected', 'disconnected');
    }
  } catch (error) {
    console.error('Error checking connection status:', error);
    updateStatus('Error', 'disconnected');
  }
}

/**
 * Update connection status display
 */
function updateStatus(text, state) {
  statusText.textContent = text;
  
  if (state === 'connected') {
    statusIndicator.classList.remove('status-disconnected');
    statusIndicator.classList.add('status-connected');
  } else {
    statusIndicator.classList.remove('status-connected');
    statusIndicator.classList.add('status-disconnected');
  }
}

/**
 * Update statistics display
 */
function updateStats(stats) {
  // Show stats section
  statsSection.style.display = 'block';
  
  // Update values
  lastQueryElem.textContent = stats.lastSearchQuery || '-';
  recommendationsCountElem.textContent = stats.recommendationsCount || '0';
  connectionStatusElem.textContent = 'Active';
}

/**
 * Validate WebSocket URL
 */
function isValidWebSocketUrl(url) {
  return /^wss?:\/\/.+/.test(url);
}

// Set up message listener for background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'update_status') {
    checkConnectionStatus();
  }
  return true;
}); 