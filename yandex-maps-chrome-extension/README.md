# 🎯 Yandex Maps Lead Finder

A powerful Chrome extension that automatically finds businesses **without websites** on Yandex Maps - perfect for lead generation and sales prospecting.

## ✨ Features

- 🔍 **Smart Filtering** - Automatically filters out businesses that have websites
- 📊 **Real-time Progress** - Watch leads being found in real-time via side panel
- 🎚️ **Flexible Targets** - Choose to find 5, 10, 25, 50, or 100 qualified leads
- ♾️ **Infinite Scroll** - Automatically loads more results until target is reached
- 📥 **Export Options** - Download results as CSV or JSON
- ⚡ **Fast & Efficient** - Uses MutationObserver for dynamic content detection
- 🎨 **Modern UI** - Beautiful side panel interface with progress tracking
- 🔒 **Privacy-Focused** - All data stays local in your browser

## 🚀 Installation

### Method 1: Load Unpacked Extension (Development)

1. **Download the extension**
   - Clone or download this repository
   - Or download as ZIP and extract

2. **Open Chrome Extensions page**
   - Navigate to `chrome://extensions/`
   - Or click the three dots menu → More Tools → Extensions

3. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top right

4. **Load the extension**
   - Click "Load unpacked"
   - Select the `yandex-maps-chrome-extension` folder
   - The extension will now appear in your extensions list

5. **Pin the extension** (Optional)
   - Click the puzzle piece icon in Chrome toolbar
   - Find "Yandex Maps Lead Finder"
   - Click the pin icon to keep it visible

### Method 2: Chrome Web Store (Coming Soon)
*Extension will be published to Chrome Web Store soon*

## 📖 How to Use

### Step 1: Search on Yandex Maps
1. Go to [Yandex Maps](https://yandex.ru/maps) (or [yandex.com/maps](https://yandex.com/maps))
2. Search for the type of businesses you're interested in
   - Example: "Restaurants in Moscow"
   - Example: "Car detailing Moscow"
   - Example: "Hair salons St Petersburg"

### Step 2: Open the Extension
1. Click the extension icon in your Chrome toolbar
2. The side panel will open showing the Lead Finder interface

### Step 3: Configure and Start
1. **Select your target** - Choose how many leads you want (5, 10, 25, 50, or 100)
2. **Click "Start Scraping"** - The extension will begin finding businesses
3. **Watch the progress** - See leads being found in real-time

### Step 4: Review Results
- Results appear in the side panel as they're found
- Each result shows:
  - ✓ Business name
  - 📍 Address
  - 📞 Phone number

### Step 5: Export Your Leads
1. Once scraping is complete (or when you're satisfied), click:
   - **Export CSV** - For spreadsheet software (Excel, Google Sheets)
   - **Export JSON** - For developers or database import
2. File downloads automatically to your Downloads folder

### Tips for Best Results

💡 **Use specific searches**
- "Car wash Moscow" → Better than "Businesses Moscow"
- More specific = better quality leads

💡 **Try different cities/regions**
- Each region may have different businesses
- Small towns often have more businesses without websites

💡 **Adjust your target**
- Start with 10 to test
- Increase to 50-100 for larger campaigns

💡 **Stop and restart anytime**
- Click "Stop Scraping" if you find enough leads
- Click "Clear All Data" to start fresh

## 🏗️ Technical Architecture

### Components

```
yandex-maps-chrome-extension/
├── manifest.json           # Extension configuration (Manifest V3)
├── service-worker.js       # Background script for data & exports
├── content.js              # Injected script with DOM access
├── sidepanel/
│   ├── sidepanel.html     # Side panel UI
│   ├── sidepanel.css      # Styles
│   └── sidepanel.js       # UI logic & messaging
└── icons/                  # Extension icons
```

### How It Works

1. **Content Script** - Injects into Yandex Maps pages
   - Uses `MutationObserver` to detect new business cards
   - Extracts name, address, phone from DOM
   - Filters out businesses with websites

2. **Service Worker** - Manages data and state
   - Aggregates businesses found
   - Prevents duplicates
   - Generates CSV/JSON exports
   - Handles chrome.downloads API

3. **Side Panel** - Provides user interface
   - Real-time progress updates
   - Results preview
   - Export controls

4. **Message Passing** - Communication layer
   - Content Script ↔ Service Worker ↔ Side Panel
   - Real-time state synchronization

## 🔧 Development

### Prerequisites
- Chrome browser (version 114+)
- Basic knowledge of JavaScript (for customization)

### Local Development

1. Make changes to the files
2. Go to `chrome://extensions/`
3. Click the refresh icon on the extension card
4. Test your changes

### Debugging

**Content Script**
- Right-click on Yandex Maps page → Inspect
- Console tab will show content script logs

**Service Worker**
- Go to `chrome://extensions/`
- Click "service worker" link under the extension
- View service worker console

**Side Panel**
- Open side panel
- Right-click inside panel → Inspect
- View side panel console

## 📝 Data Format

### CSV Export Format
```csv
Position,Business Name,Address,Phone,Yandex Maps URL
1,"Pizza Place","123 Main St, Moscow","555-1234","https://yandex.ru/maps/..."
2,"Hair Salon","456 Oak Ave, Moscow","555-5678","https://yandex.ru/maps/..."
```

### JSON Export Format
```json
{
  "exportDate": "2025-01-08T12:00:00.000Z",
  "totalLeads": 10,
  "businesses": [
    {
      "title": "Pizza Place",
      "address": "123 Main St, Moscow",
      "phone": "555-1234",
      "url": "https://yandex.ru/maps/...",
      "extractedAt": "2025-01-08T12:00:00.000Z"
    }
  ]
}
```

## 🤝 Use Cases

- **Sales Teams** - Find local businesses without websites for outreach
- **Web Developers** - Identify potential clients who need websites
- **Marketing Agencies** - Build targeted prospect lists
- **Lead Generation** - Create qualified B2B leads
- **Market Research** - Analyze businesses in specific regions

## ⚠️ Limitations

- Only works on Yandex Maps (yandex.com/maps and yandex.ru/maps)
- Requires Chrome browser version 114 or higher
- DOM structure changes by Yandex may require updates
- Respects Yandex's rate limiting (uses realistic delays)

## 🛡️ Privacy & Security

- ✅ All data stored locally in your browser
- ✅ No data sent to external servers
- ✅ No tracking or analytics
- ✅ Open source - inspect the code yourself
- ✅ Minimal permissions (only what's needed)

## 📄 License

MIT License - feel free to modify and distribute

## 🐛 Troubleshooting

**Extension not finding results?**
- Make sure you're on Yandex Maps with search results visible
- Try refreshing the page and starting again
- Check browser console for errors

**Export not working?**
- Make sure you have businesses in the results
- Check Downloads folder for the file
- Try the other export format (CSV vs JSON)

**Side panel not opening?**
- Make sure you're using Chrome 114+
- Try reloading the extension
- Check that side panel permission is granted

**Scraping stopped early?**
- May have reached end of results for that search
- Try a broader search query
- Try a different city/region

## 🔄 Updates

Check back for updates! The extension will be updated to:
- Adapt to Yandex Maps changes
- Add new features
- Fix bugs
- Improve performance

## 💬 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing issues for solutions
- Read the troubleshooting section above

---

**Made with ❤️ for lead generation**
