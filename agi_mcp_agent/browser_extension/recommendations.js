/**
 * MCP Search Recommendations - Detail View Script
 */

// DOM elements
const searchQueryElem = document.getElementById('search-query');
const analysisCriteriaElem = document.getElementById('analysis-criteria');
const recommendationsContainer = document.getElementById('recommendations-container');

// Configuration and state
const CONFIG_KEY = "mcp_google_assistant_config";
let recommendations = [];
let searchQuery = "";
let criteria = [];
let analysisDetails = {};

// Initialize when the document is ready
document.addEventListener('DOMContentLoaded', async () => {
  // Get recommendations from URL parameters or storage
  const urlParams = new URLSearchParams(window.location.search);
  searchQuery = urlParams.get('query') || "";
  
  if (searchQuery) {
    searchQueryElem.textContent = searchQuery;
    
    // Try to get data from the referring tab
    try {
      // Load configuration for criteria
      const config = await loadConfiguration();
      criteria = config.criteria || ["relevance", "authority", "recency"];
      analysisCriteriaElem.textContent = criteria.map(c => c.charAt(0).toUpperCase() + c.slice(1)).join(', ');
      
      // Get recommendations from the sender tab
      await loadRecommendations();
    } catch (error) {
      console.error("Error loading recommendations:", error);
      showNoRecommendations("Failed to load recommendations. Please try again.");
    }
  } else {
    searchQueryElem.textContent = "No query specified";
    showNoRecommendations("No search query specified.");
  }
});

/**
 * Load extension configuration from storage
 */
async function loadConfiguration() {
  return new Promise(resolve => {
    chrome.storage.sync.get(CONFIG_KEY, (data) => {
      const config = data[CONFIG_KEY] || {
        mcpServer: "ws://localhost:8080/ws",
        criteria: ["relevance", "authority", "recency"]
      };
      resolve(config);
    });
  });
}

/**
 * Load recommendations from sender tab or MCP server
 */
async function loadRecommendations() {
  // Try to get recommendations from the sender tab
  chrome.runtime.sendMessage({ action: "get_recommendations", query: searchQuery }, response => {
    if (response && response.recommendations && response.recommendations.length > 0) {
      // Got recommendations from background script
      recommendations = response.recommendations;
      analysisDetails = response.analysisDetails || {};
      renderRecommendations();
    } else {
      // If we couldn't get recommendations from the sender, show error
      showNoRecommendations("No recommendations available for this search query.");
    }
  });
}

/**
 * Render recommendations to the page
 */
function renderRecommendations() {
  if (!recommendations || recommendations.length === 0) {
    showNoRecommendations("No recommendations found for this search query.");
    return;
  }
  
  // Create recommendations HTML
  let html = '<div class="recommendations">';
  
  for (const rec of recommendations) {
    const recDetails = analysisDetails[rec.url] || { 
      relevance: "-", 
      authority: "-", 
      recency: "-" 
    };
    
    html += `
      <div class="recommendation-card">
        <h2 class="recommendation-title">
          <a href="${rec.url}" target="_blank">${rec.title}</a>
        </h2>
        <div class="recommendation-snippet">${rec.snippet}</div>
        <div class="recommendation-reason">
          <div class="recommendation-reason-title">Why this is recommended:</div>
          ${rec.reason}
        </div>
        <div class="recommendation-scores">
          ${criteria.includes("relevance") ? `
            <div class="score-item">
              <div class="score-label">Relevance</div>
              <div class="score-value">${formatScore(recDetails.relevance)}</div>
            </div>
          ` : ''}
          ${criteria.includes("authority") ? `
            <div class="score-item">
              <div class="score-label">Authority</div>
              <div class="score-value">${formatScore(recDetails.authority)}</div>
            </div>
          ` : ''}
          ${criteria.includes("recency") ? `
            <div class="score-item">
              <div class="score-label">Recency</div>
              <div class="score-value">${formatScore(recDetails.recency)}</div>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }
  
  html += '</div>';
  recommendationsContainer.innerHTML = html;
}

/**
 * Format a score for display
 */
function formatScore(score) {
  if (score === undefined || score === null || score === "-") {
    return "-";
  }
  
  return typeof score === 'number' ? score.toFixed(1) : score;
}

/**
 * Show a message when no recommendations are available
 */
function showNoRecommendations(message) {
  recommendationsContainer.innerHTML = `
    <div class="no-recommendations">
      ${message}
    </div>
  `;
}

// Listen for messages from the popup or content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "update_recommendations" && message.recommendations) {
    recommendations = message.recommendations;
    analysisDetails = message.analysisDetails || {};
    renderRecommendations();
    return true;
  }
}); 