/**
 * MCP Google Search Assistant - Background Script
 * 
 * This script runs in the background and manages the extension state.
 */

// Configuration
const CONFIG_KEY = "mcp_google_assistant_config";
const DEFAULT_MCP_SERVER = "ws://localhost:8080/ws";
let serverStatus = {
  connected: false,
  lastChecked: null
};

// When extension is installed or updated
chrome.runtime.onInstalled.addListener(function(details) {
  console.log("MCP Google Search Assistant: Extension installed/updated", details.reason);
  
  // Initialize default settings if needed
  chrome.storage.sync.get(CONFIG_KEY, function(data) {
    if (!data[CONFIG_KEY]) {
      const defaultConfig = {
        mcpServer: DEFAULT_MCP_SERVER
      };
      chrome.storage.sync.set({ [CONFIG_KEY]: defaultConfig });
      console.log("MCP Google Search Assistant: Initialized default settings");
    }
  });
  
  // Update extension icon
  updateExtensionIcon(false);
});

// On extension startup
chrome.runtime.onStartup.addListener(function() {
  console.log("MCP Google Search Assistant: Extension started");
  updateExtensionIcon(false);
});

// Listen for tab updates to check if we're on Google search pages
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.includes('google.com/search')) {
    // We're on a Google search page, set the extension icon to active
    chrome.action.setIcon({
      path: {
        16: "icons/icon16.png",
        48: "icons/icon48.png",
        128: "icons/icon128.png"
      },
      tabId: tabId
    });
    
    // Check connection after a delay to allow content script to initialize
    setTimeout(() => {
      checkContentScriptConnection(tabId);
    }, 1000);
  }
});

// Listen for messages from content script or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "update_server_status") {
    serverStatus.connected = message.connected;
    serverStatus.lastChecked = new Date();
    updateExtensionIcon(message.connected);
    
    // Notify popup if open
    chrome.runtime.sendMessage({ action: "update_status" }).catch(() => {});
    
    sendResponse({ success: true });
    return true;
  }
  
  if (message.action === "get_server_status") {
    sendResponse({
      connected: serverStatus.connected,
      lastChecked: serverStatus.lastChecked
    });
    return true;
  }
});

/**
 * Update the extension icon based on connection status
 */
function updateExtensionIcon(connected) {
  const iconPrefix = connected ? "active" : "icon";
  
  chrome.action.setIcon({
    path: {
      16: `icons/${iconPrefix}16.png`,
      48: `icons/${iconPrefix}48.png`,
      128: `icons/${iconPrefix}128.png`
    }
  });
}

/**
 * Check if content script is connected to MCP server
 */
function checkContentScriptConnection(tabId) {
  chrome.tabs.sendMessage(tabId, { action: "get_status" })
    .then(response => {
      if (response && response.connected) {
        serverStatus.connected = true;
        updateExtensionIcon(true);
      } else {
        serverStatus.connected = false;
        updateExtensionIcon(false);
      }
      serverStatus.lastChecked = new Date();
    })
    .catch(() => {
      // Content script not ready or not available
      serverStatus.connected = false;
      updateExtensionIcon(false);
      serverStatus.lastChecked = new Date();
    });
} 