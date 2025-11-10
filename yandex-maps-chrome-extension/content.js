/**
 * Content Script for Yandex Maps Lead Finder
 * Injected into Yandex Maps pages - has full DOM access
 */

// State
let isScrapingActive = false;
let targetLeads = 10;
let processedBusinesses = new Set(); // Track by title to avoid duplicates
let observer = null;
let scrollInterval = null;

console.log('Yandex Maps Lead Finder content script loaded');

// Listen for messages from service worker
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Content script received:', message.type);

  switch (message.type) {
    case 'START_SCRAPING':
      startScraping(message.target);
      sendResponse({ success: true });
      break;

    case 'STOP_SCRAPING':
      stopScraping();
      sendResponse({ success: true });
      break;
  }

  return true;
});

// Start scraping
function startScraping(target) {
  console.log('Starting scraping, target:', target);

  isScrapingActive = true;
  targetLeads = target;
  processedBusinesses.clear();

  // Start observing DOM for business cards
  startObserving();

  // Start infinite scroll
  startInfiniteScroll();

  // Process any existing businesses on the page
  processExistingBusinesses();
}

// Stop scraping
function stopScraping() {
  console.log('Stopping scraping');

  isScrapingActive = false;

  // Stop observing
  if (observer) {
    observer.disconnect();
    observer = null;
  }

  // Stop scrolling
  if (scrollInterval) {
    clearInterval(scrollInterval);
    scrollInterval = null;
  }
}

// Start observing DOM for new business cards
function startObserving() {
  // Find the search results container
  const resultsContainer = findSearchResultsContainer();

  if (!resultsContainer) {
    console.warn('Could not find search results container');
    return;
  }

  console.log('Found search results container, starting MutationObserver');

  // Create observer
  observer = new MutationObserver((mutations) => {
    if (!isScrapingActive) return;

    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1 && isBusinessCard(node)) {
          processBusinessCard(node);
        }
      });
    });
  });

  // Start observing
  observer.observe(resultsContainer, {
    childList: true,
    subtree: true
  });
}

// Find search results container
function findSearchResultsContainer() {
  const selectors = [
    '[class*="search-list-view"]',
    '[class*="search-snippet-view"]',
    'ul[class*="scroll__container"]',
    '[class*="search-results"]',
    '[class*="search__list"]'
  ];

  for (const selector of selectors) {
    const container = document.querySelector(selector);
    if (container) {
      console.log('Found container with selector:', selector);
      return container;
    }
  }

  return null;
}

// Check if node is a business card
function isBusinessCard(node) {
  // Check for common business card class patterns
  const className = node.className || '';

  return (
    className.includes('search-snippet') ||
    className.includes('business-card') ||
    className.includes('search-business') ||
    className.includes('orgcard') ||
    (node.tagName === 'LI' && className.includes('scroll__item'))
  );
}

// Process existing businesses on page
function processExistingBusinesses() {
  console.log('Processing existing businesses on page');

  const selectors = [
    '[class*="search-snippet-view"]',
    '[class*="search-business-snippet-view"]',
    'li[class*="scroll__item"]',
    '[class*="business-card"]'
  ];

  for (const selector of selectors) {
    const cards = document.querySelectorAll(selector);
    if (cards.length > 0) {
      console.log(`Found ${cards.length} business cards with selector: ${selector}`);

      cards.forEach(card => {
        if (isScrapingActive) {
          processBusinessCard(card);
        }
      });

      break; // Stop after finding first working selector
    }
  }
}

// Process a single business card
function processBusinessCard(card) {
  if (!isScrapingActive) return;

  try {
    // Extract business data
    const business = extractBusinessData(card);

    if (!business || !business.title) {
      return; // Invalid business
    }

    // Check if already processed
    if (processedBusinesses.has(business.title)) {
      return; // Skip duplicate
    }

    // Check if has website
    if (hasWebsite(card)) {
      console.log(`Skipping ${business.title} - has website`);
      return;
    }

    // Mark as processed
    processedBusinesses.add(business.title);

    // Send to service worker
    console.log(`✓ Found lead: ${business.title}`);
    chrome.runtime.sendMessage({
      type: 'BUSINESS_FOUND',
      data: business
    });

  } catch (error) {
    console.error('Error processing business card:', error);
  }
}

// Extract business data from card
function extractBusinessData(card) {
  const business = {
    title: '',
    address: '',
    phone: '',
    url: window.location.href,
    extractedAt: new Date().toISOString()
  };

  // Extract title/name
  const titleSelectors = [
    '[class*="title"]',
    '[class*="name"]',
    '[class*="orgcard-title"]',
    'h3',
    'h2',
    'a[class*="business"]'
  ];

  for (const selector of titleSelectors) {
    const titleElem = card.querySelector(selector);
    if (titleElem && titleElem.textContent.trim()) {
      business.title = titleElem.textContent.trim();
      break;
    }
  }

  // Extract address
  const addressSelectors = [
    '[class*="address"]',
    '[class*="location"]',
    '[class*="contacts-view__address"]',
    '[class*="business-contacts"] [class*="address"]'
  ];

  for (const selector of addressSelectors) {
    const addressElem = card.querySelector(selector);
    if (addressElem && addressElem.textContent.trim()) {
      business.address = addressElem.textContent.trim();
      break;
    }
  }

  // Extract phone
  const phoneSelectors = [
    '[class*="phone"]',
    '[class*="tel"]',
    '[class*="contacts-view__phone"]',
    '[href^="tel:"]'
  ];

  for (const selector of phoneSelectors) {
    const phoneElem = card.querySelector(selector);
    if (phoneElem) {
      const phoneText = phoneElem.textContent.trim() || phoneElem.getAttribute('href');
      if (phoneText) {
        business.phone = phoneText.replace('tel:', '');
        break;
      }
    }
  }

  return business;
}

// Check if business card has a website
function hasWebsite(card) {
  // Look for website links (excluding yandex.ru and yandex.com)
  const websiteSelectors = [
    'a[href*="http"]',
    '[class*="website"]',
    '[class*="url"]',
    '[class*="business-url"]',
    '[data-type="website"]'
  ];

  for (const selector of websiteSelectors) {
    const links = card.querySelectorAll(selector);

    for (const link of links) {
      const href = link.getAttribute('href') || '';
      const text = link.textContent.toLowerCase();

      // Filter out Yandex internal links
      if (href && !href.includes('yandex.ru') && !href.includes('yandex.com')) {
        // Check if it's actually a website link
        if (href.startsWith('http') || text.includes('website') || text.includes('site')) {
          return true;
        }
      }
    }
  }

  // Check for website text without link
  const cardText = card.textContent.toLowerCase();
  if (cardText.includes('website:') || cardText.includes('сайт:')) {
    return true;
  }

  return false;
}

// Start infinite scroll
function startInfiniteScroll() {
  console.log('Starting infinite scroll');

  let scrollAttempts = 0;
  let lastScrollHeight = 0;
  const maxAttempts = 50; // Max scrolls before giving up

  scrollInterval = setInterval(() => {
    if (!isScrapingActive) {
      clearInterval(scrollInterval);
      return;
    }

    scrollAttempts++;

    if (scrollAttempts > maxAttempts) {
      console.log('Max scroll attempts reached, stopping');
      stopScraping();
      return;
    }

    // Find scroll container
    const scrollContainer = findScrollContainer();

    if (!scrollContainer) {
      console.warn('Could not find scroll container');
      return;
    }

    const currentHeight = scrollContainer.scrollHeight;

    // Scroll to bottom
    scrollContainer.scrollTop = scrollContainer.scrollHeight;

    // Check if new content loaded
    if (currentHeight === lastScrollHeight) {
      console.log('No new content loaded');
    } else {
      console.log('New content loaded, continuing scroll');
      lastScrollHeight = currentHeight;
      scrollAttempts = 0; // Reset attempts when new content loads
    }

  }, 2000); // Scroll every 2 seconds
}

// Find scroll container
function findScrollContainer() {
  const selectors = [
    '[class*="search-list-view"]',
    '[class*="scroll__container"]',
    '[class*="search-results"]',
    '.ymaps-2-1-79-scroll__container'
  ];

  for (const selector of selectors) {
    const container = document.querySelector(selector);
    if (container && container.scrollHeight > container.clientHeight) {
      return container;
    }
  }

  // Fallback to window
  return document.documentElement;
}

// Log when content script loads
console.log('Yandex Maps Lead Finder ready - waiting for scraping command');
