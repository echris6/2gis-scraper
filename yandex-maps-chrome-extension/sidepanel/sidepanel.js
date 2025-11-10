/**
 * Side Panel JavaScript for Yandex Maps Lead Finder
 * Handles UI interactions and communication with service worker
 */

// State
let currentTarget = 10;
let currentState = null;

// DOM Elements
const targetButtons = document.querySelectorAll('.target-btn');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const progressSection = document.getElementById('progressSection');
const progressText = document.getElementById('progressText');
const progressPercent = document.getElementById('progressPercent');
const progressFill = document.getElementById('progressFill');
const resultsSection = document.getElementById('resultsSection');
const resultsList = document.getElementById('resultsList');
const resultsCount = document.getElementById('resultsCount');
const exportSection = document.getElementById('exportSection');
const exportCsvBtn = document.getElementById('exportCsvBtn');
const exportJsonBtn = document.getElementById('exportJsonBtn');
const clearBtn = document.getElementById('clearBtn');
const statusMessage = document.getElementById('statusMessage');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  console.log('Side panel loaded');

  // Load current state
  loadState();

  // Set up event listeners
  setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
  // Target buttons
  targetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      targetButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentTarget = parseInt(btn.dataset.target);
      console.log('Target set to:', currentTarget);
    });
  });

  // Start button
  startBtn.addEventListener('click', () => {
    startScraping();
  });

  // Stop button
  stopBtn.addEventListener('click', () => {
    stopScraping();
  });

  // Export CSV
  exportCsvBtn.addEventListener('click', () => {
    exportData('csv');
  });

  // Export JSON
  exportJsonBtn.addEventListener('click', () => {
    exportData('json');
  });

  // Clear data
  clearBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
      clearData();
    }
  });

  // Listen for state updates from service worker
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'STATE_UPDATE') {
      updateUI(message.state);
    }
  });
}

// Load current state
function loadState() {
  chrome.runtime.sendMessage({ type: 'GET_STATE' }, (response) => {
    if (response && response.state) {
      currentState = response.state;
      updateUI(currentState);
    }
  });
}

// Start scraping
function startScraping() {
  console.log('Starting scraping with target:', currentTarget);

  // Check if on Yandex Maps
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const currentTab = tabs[0];

    if (!currentTab.url || (!currentTab.url.includes('yandex.com/maps') && !currentTab.url.includes('yandex.ru/maps'))) {
      showStatus('Please open Yandex Maps and search for businesses first!', 'error');
      return;
    }

    // Send start message to service worker
    chrome.runtime.sendMessage({
      type: 'START_SCRAPING',
      target: currentTarget
    }, (response) => {
      if (response && response.success) {
        showStatus(`Started scraping for ${currentTarget} leads...`, 'info');
        startBtn.style.display = 'none';
        stopBtn.style.display = 'block';
        progressSection.style.display = 'block';
      }
    });
  });
}

// Stop scraping
function stopScraping() {
  console.log('Stopping scraping');

  chrome.runtime.sendMessage({ type: 'STOP_SCRAPING' }, (response) => {
    if (response && response.success) {
      showStatus('Scraping stopped', 'info');
      startBtn.style.display = 'block';
      stopBtn.style.display = 'none';
    }
  });
}

// Export data
function exportData(format) {
  console.log('Exporting as:', format);

  const messageType = format === 'csv' ? 'EXPORT_CSV' : 'EXPORT_JSON';

  chrome.runtime.sendMessage({ type: messageType }, (response) => {
    if (response && response.success) {
      showStatus(`Exported as ${format.toUpperCase()}!`, 'success');
    } else {
      showStatus(`Failed to export ${format.toUpperCase()}`, 'error');
    }
  });
}

// Clear data
function clearData() {
  chrome.runtime.sendMessage({ type: 'CLEAR_DATA' }, (response) => {
    if (response && response.success) {
      showStatus('All data cleared', 'info');
      resultsList.innerHTML = '';
      resultsSection.style.display = 'none';
      exportSection.style.display = 'none';
      progressSection.style.display = 'none';
      startBtn.style.display = 'block';
      stopBtn.style.display = 'none';
    }
  });
}

// Update UI based on state
function updateUI(state) {
  if (!state) return;

  currentState = state;

  // Update progress
  if (state.isActive || state.found > 0) {
    progressSection.style.display = 'block';

    const progress = Math.min((state.found / state.target) * 100, 100);

    progressText.textContent = `${state.found}/${state.target} leads found`;
    progressPercent.textContent = `${Math.round(progress)}%`;
    progressFill.style.width = `${progress}%`;
  }

  // Update buttons
  if (state.isActive) {
    startBtn.style.display = 'none';
    stopBtn.style.display = 'block';
  } else {
    startBtn.style.display = 'block';
    stopBtn.style.display = 'none';
  }

  // Update results
  if (state.businesses && state.businesses.length > 0) {
    resultsSection.style.display = 'block';
    exportSection.style.display = 'block';

    resultsCount.textContent = `${state.businesses.length} lead${state.businesses.length !== 1 ? 's' : ''}`;

    // Show last 10 results (most recent first)
    const recentBusinesses = state.businesses.slice(-10).reverse();
    updateResultsList(recentBusinesses);
  }

  // Show completion message if target reached
  if (!state.isActive && state.found >= state.target && state.found > 0) {
    showStatus(`🎉 Found ${state.found} qualified leads! Ready to export.`, 'success');
  }
}

// Update results list
function updateResultsList(businesses) {
  resultsList.innerHTML = '';

  businesses.forEach((business, index) => {
    const item = document.createElement('div');
    item.className = 'result-item';
    if (index === 0) item.classList.add('new');

    const title = document.createElement('div');
    title.className = 'result-title';
    title.textContent = business.title || 'Unnamed Business';

    const address = document.createElement('div');
    address.className = 'result-detail';
    address.innerHTML = `<span class="result-icon">📍</span>${business.address || 'No address'}`;

    const phone = document.createElement('div');
    phone.className = 'result-detail';
    phone.innerHTML = `<span class="result-icon">📞</span>${business.phone || 'No phone'}`;

    item.appendChild(title);
    item.appendChild(address);
    item.appendChild(phone);

    resultsList.appendChild(item);
  });
}

// Show status message
function showStatus(message, type = 'info') {
  statusMessage.textContent = message;
  statusMessage.className = `status-message show ${type}`;

  // Auto-hide after 5 seconds
  setTimeout(() => {
    statusMessage.classList.remove('show');
  }, 5000);
}

// Periodically refresh state while scraping
setInterval(() => {
  if (currentState && currentState.isActive) {
    loadState();
  }
}, 2000); // Refresh every 2 seconds
