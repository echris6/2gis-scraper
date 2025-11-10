/**
 * Service Worker for Yandex Maps Lead Finder
 * Handles message passing, data aggregation, and export functionality
 */

// State management
let scrapingState = {
  isActive: false,
  target: 10,
  found: 0,
  businesses: [],
  currentTabId: null
};

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('Yandex Maps Lead Finder installed');

  // Load saved state if exists
  chrome.storage.local.get(['scrapingState'], (result) => {
    if (result.scrapingState) {
      scrapingState = result.scrapingState;
    }
  });
});

// Handle messages from content script and side panel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Service worker received message:', message.type);

  switch (message.type) {
    case 'START_SCRAPING':
      handleStartScraping(message, sender);
      sendResponse({ success: true });
      break;

    case 'STOP_SCRAPING':
      handleStopScraping();
      sendResponse({ success: true });
      break;

    case 'BUSINESS_FOUND':
      handleBusinessFound(message.data);
      sendResponse({ success: true });
      break;

    case 'GET_STATE':
      sendResponse({ state: scrapingState });
      break;

    case 'EXPORT_CSV':
      exportAsCSV();
      sendResponse({ success: true });
      break;

    case 'EXPORT_JSON':
      exportAsJSON();
      sendResponse({ success: true });
      break;

    case 'CLEAR_DATA':
      handleClearData();
      sendResponse({ success: true });
      break;

    default:
      console.warn('Unknown message type:', message.type);
  }

  return true; // Keep channel open for async response
});

// Start scraping
function handleStartScraping(message, sender) {
  scrapingState = {
    isActive: true,
    target: message.target || 10,
    found: 0,
    businesses: [],
    currentTabId: sender.tab?.id || null
  };

  saveState();
  notifySidePanel();

  // Send message to content script to start
  if (scrapingState.currentTabId) {
    chrome.tabs.sendMessage(scrapingState.currentTabId, {
      type: 'START_SCRAPING',
      target: scrapingState.target
    });
  }

  console.log('Scraping started, target:', scrapingState.target);
}

// Stop scraping
function handleStopScraping() {
  scrapingState.isActive = false;
  saveState();
  notifySidePanel();

  // Notify content script to stop
  if (scrapingState.currentTabId) {
    chrome.tabs.sendMessage(scrapingState.currentTabId, {
      type: 'STOP_SCRAPING'
    });
  }

  console.log('Scraping stopped');
}

// Handle new business found
function handleBusinessFound(business) {
  // Check for duplicates
  const isDuplicate = scrapingState.businesses.some(
    b => b.title === business.title && b.phone === business.phone
  );

  if (isDuplicate) {
    console.log('Duplicate business, skipping:', business.title);
    return;
  }

  // Add business
  scrapingState.businesses.push(business);
  scrapingState.found = scrapingState.businesses.length;

  console.log(`Business added: ${business.title} (${scrapingState.found}/${scrapingState.target})`);

  // Check if target reached
  if (scrapingState.found >= scrapingState.target) {
    console.log('Target reached!');
    handleStopScraping();

    // Show completion notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Scraping Complete!',
      message: `Found ${scrapingState.found} businesses without websites`,
      priority: 2
    });
  }

  saveState();
  notifySidePanel();
}

// Clear all data
function handleClearData() {
  scrapingState = {
    isActive: false,
    target: 10,
    found: 0,
    businesses: [],
    currentTabId: null
  };

  saveState();
  notifySidePanel();

  console.log('Data cleared');
}

// Save state to chrome.storage
function saveState() {
  chrome.storage.local.set({ scrapingState }, () => {
    if (chrome.runtime.lastError) {
      console.error('Error saving state:', chrome.runtime.lastError);
    }
  });
}

// Notify side panel of state changes
function notifySidePanel() {
  chrome.runtime.sendMessage({
    type: 'STATE_UPDATE',
    state: scrapingState
  }).catch(() => {
    // Side panel might not be open, ignore error
  });
}

// Export as CSV
function exportAsCSV() {
  if (scrapingState.businesses.length === 0) {
    console.warn('No businesses to export');
    return;
  }

  // Build CSV content
  const headers = ['Position', 'Business Name', 'Address', 'Phone', 'Yandex Maps URL'];
  const rows = scrapingState.businesses.map((b, index) => [
    index + 1,
    escapeCSV(b.title),
    escapeCSV(b.address || ''),
    escapeCSV(b.phone || ''),
    escapeCSV(b.url || '')
  ]);

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');

  // Create data URL (Manifest V3 requirement)
  const base64 = btoa(unescape(encodeURIComponent(csvContent)));
  const dataUrl = `data:text/csv;charset=utf-8;base64,${base64}`;

  // Download file
  const filename = `yandex_leads_${Date.now()}.csv`;
  chrome.downloads.download({
    url: dataUrl,
    filename: filename,
    saveAs: true
  }, (downloadId) => {
    if (chrome.runtime.lastError) {
      console.error('Download failed:', chrome.runtime.lastError);
    } else {
      console.log('CSV exported:', filename);
    }
  });
}

// Export as JSON
function exportAsJSON() {
  if (scrapingState.businesses.length === 0) {
    console.warn('No businesses to export');
    return;
  }

  const jsonContent = JSON.stringify({
    exportDate: new Date().toISOString(),
    totalLeads: scrapingState.businesses.length,
    businesses: scrapingState.businesses
  }, null, 2);

  // Create data URL (Manifest V3 requirement)
  const base64 = btoa(unescape(encodeURIComponent(jsonContent)));
  const dataUrl = `data:application/json;charset=utf-8;base64,${base64}`;

  // Download file
  const filename = `yandex_leads_${Date.now()}.json`;
  chrome.downloads.download({
    url: dataUrl,
    filename: filename,
    saveAs: true
  }, (downloadId) => {
    if (chrome.runtime.lastError) {
      console.error('Download failed:', chrome.runtime.lastError);
    } else {
      console.log('JSON exported:', filename);
    }
  });
}

// Helper: Escape CSV fields
function escapeCSV(field) {
  if (typeof field !== 'string') return '';

  // Escape quotes and wrap in quotes if contains comma, quote, or newline
  if (field.includes(',') || field.includes('"') || field.includes('\n')) {
    return `"${field.replace(/"/g, '""')}"`;
  }
  return field;
}

// Listen for tab updates to track current Yandex Maps tab
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' &&
      tab.url &&
      (tab.url.includes('yandex.com/maps') || tab.url.includes('yandex.ru/maps'))) {
    scrapingState.currentTabId = tabId;
    saveState();
  }
});
