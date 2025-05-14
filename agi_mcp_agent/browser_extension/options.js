/**
 * MCP Google Search Assistant - Options Script
 */

// Configuration
const CONFIG_KEY = "mcp_google_assistant_config";
const DEFAULT_MCP_SERVER = "ws://localhost:8080/ws";

// DOM elements
const serverInput = document.getElementById('mcp-server');
const recommendationsCountSelect = document.getElementById('recommendations-count');
const criteriaRelevanceCheckbox = document.getElementById('criteria-relevance');
const criteriaAuthorityCheckbox = document.getElementById('criteria-authority');
const criteriaRecencyCheckbox = document.getElementById('criteria-recency');
const highlightResultsCheckbox = document.getElementById('highlight-results');
const showBadgesCheckbox = document.getElementById('show-badges');
const saveButton = document.getElementById('save-button');
const statusDiv = document.getElementById('status');

// Initialize options page
document.addEventListener('DOMContentLoaded', async () => {
  // Load configuration
  const config = await loadConfiguration();
  
  // Set input values
  serverInput.value = config.mcpServer || DEFAULT_MCP_SERVER;
  recommendationsCountSelect.value = config.recommendationsCount || "3";
  
  // Set analysis criteria
  const criteria = config.criteria || ["relevance", "authority", "recency"];
  criteriaRelevanceCheckbox.checked = criteria.includes("relevance");
  criteriaAuthorityCheckbox.checked = criteria.includes("authority");
  criteriaRecencyCheckbox.checked = criteria.includes("recency");
  
  // Set UI settings
  highlightResultsCheckbox.checked = config.highlightResults !== false; // Default to true
  showBadgesCheckbox.checked = config.showBadges !== false; // Default to true
  
  // Set up event listeners
  saveButton.addEventListener('click', saveConfiguration);
});

/**
 * Load extension configuration from storage
 */
async function loadConfiguration() {
  return new Promise(resolve => {
    chrome.storage.sync.get(CONFIG_KEY, (data) => {
      const config = data[CONFIG_KEY] || {
        mcpServer: DEFAULT_MCP_SERVER,
        recommendationsCount: "3",
        criteria: ["relevance", "authority", "recency"],
        highlightResults: true,
        showBadges: true
      };
      resolve(config);
    });
  });
}

/**
 * Save extension configuration to storage
 */
async function saveConfiguration() {
  // Get criteria values
  const criteria = [];
  if (criteriaRelevanceCheckbox.checked) criteria.push("relevance");
  if (criteriaAuthorityCheckbox.checked) criteria.push("authority");
  if (criteriaRecencyCheckbox.checked) criteria.push("recency");
  
  // Validate
  if (criteria.length === 0) {
    showStatus("Please select at least one analysis criterion", "error");
    return;
  }
  
  // Get values from inputs
  const mcpServer = serverInput.value.trim();
  
  // Validate server URL
  if (!isValidWebSocketUrl(mcpServer)) {
    showStatus("Please enter a valid WebSocket URL (starts with ws:// or wss://)", "error");
    return;
  }
  
  // Create config object
  const config = {
    mcpServer: mcpServer,
    recommendationsCount: recommendationsCountSelect.value,
    criteria: criteria,
    highlightResults: highlightResultsCheckbox.checked,
    showBadges: showBadgesCheckbox.checked
  };
  
  // Save to storage
  chrome.storage.sync.set({ [CONFIG_KEY]: config }, () => {
    console.log('Configuration saved', config);
    showStatus("Options saved successfully!", "success");
    
    // Notify content scripts in all tabs
    notifyContentScripts();
  });
}

/**
 * Validate WebSocket URL
 */
function isValidWebSocketUrl(url) {
  return /^wss?:\/\/.+/.test(url);
}

/**
 * Show status message
 */
function showStatus(message, type = "success") {
  statusDiv.textContent = message;
  statusDiv.className = `status ${type}`;
  
  // Hide after 3 seconds
  setTimeout(() => {
    statusDiv.className = "status";
  }, 3000);
}

/**
 * Notify all content scripts about configuration change
 */
function notifyContentScripts() {
  chrome.tabs.query({}, (tabs) => {
    tabs.forEach(tab => {
      // Only send to Google search tabs
      if (tab.url && tab.url.includes("google.com/search")) {
        chrome.tabs.sendMessage(tab.id, { action: "config_updated" })
          .catch(() => console.log(`No content script in tab ${tab.id}`));
      }
    });
  });
} 