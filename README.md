# 2GIS Lead Scraper

Modern web scraper for extracting qualified business leads from 2GIS directory.

## Stack

- **Frontend**: Next.js 15 + TypeScript + Tailwind CSS 4
- **Backend**: FastAPI (Python)
- **Scraping**: Playwright + Requests

## Setup

### 1. Backend API

```bash
cd api
pip install -r requirements.txt
python main.py
```

API will run on `http://localhost:8000`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:3000`

## Usage

1. Open `http://localhost:3000`
2. Select city (Moscow, SPB, etc.)
3. Enter search query (e.g., "автомойка")
4. Configure options:
   - Enrich with phone/website (slower but gets contact info)
   - Filter by no website only
   - Filter by phone required
5. Click "Start Scraping"
6. Download results as CSV

## Features

- Clean, modern UI with Tailwind CSS
- Real-time scraping progress
- Stats dashboard (total, with phone, no website, avg rating)
- CSV export
- Contact enrichment (phone/website extraction)
- Advanced filtering

## Deployment

- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Render (requires Playwright)
