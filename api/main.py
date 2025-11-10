"""
FastAPI backend for 2GIS scraper
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path
from collections import deque
import logging
import io

# Add scraper to path
sys.path.insert(0, str(Path(__file__).parent.parent / '2gis_scraper'))

from scraper import TwoGISScraper
from profile_scraper import ProfileEnricher
from exporter import DataExporter

app = FastAPI(title="2GIS Lead Scraper API")

# Create a log buffer to store recent logs
log_buffer = deque(maxlen=100)

class LogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_buffer.append(log_entry)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
log_handler = LogHandler()
log_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(log_handler)

# CORS
import os
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    city: str
    query: str
    pages: int = 2
    enrich_contacts: bool = True
    no_website_only: bool = False
    require_phone: bool = False

@app.get("/")
def read_root():
    return {"status": "ok", "message": "2GIS Scraper API", "version": "2.0-playwright"}

@app.get("/debug/cors")
def debug_cors():
    """Debug endpoint to check CORS configuration"""
    return {
        "allowed_origins": allowed_origins,
        "origins_count": len(allowed_origins)
    }

@app.get("/cities")
def get_cities():
    """Get list of available cities"""
    from config import CITY_TLD_MAP
    return {"cities": list(CITY_TLD_MAP.keys())}

@app.get("/logs")
def get_logs():
    """Get recent backend logs"""
    return {"logs": list(log_buffer)}

@app.post("/scrape")
async def scrape_businesses(request: ScrapeRequest):
    """Scrape businesses from 2GIS"""
    try:
        # Initialize scraper
        logger.info(f"Initializing scraper for {request.city} - {request.query}")
        scraper = TwoGISScraper()

        # Search businesses
        logger.info(f"Searching {request.pages} pages...")
        businesses = []
        for page in range(1, request.pages + 1):
            logger.info(f"Scraping page {page}/{request.pages}...")
            results = scraper.scrape_page(request.city, request.query, page=page)
            if not results:
                logger.info(f"No results on page {page}, stopping")
                break
            logger.info(f"Found {len(results)} businesses on page {page}")
            businesses.extend(results)

        logger.info(f"Total businesses found: {len(businesses)}")

        # Enrich with contacts if requested
        if request.enrich_contacts and businesses:
            logger.info(f"Starting contact enrichment for {len(businesses)} businesses...")
            async with ProfileEnricher() as enricher:
                businesses = await enricher.enrich_businesses(businesses, request.city)
            logger.info(f"Contact enrichment completed")

        # Apply filters
        if request.no_website_only:
            before = len(businesses)
            businesses = [b for b in businesses if not b.get('website')]
            logger.info(f"Filtered to businesses without websites: {len(businesses)}/{before}")

        if request.require_phone:
            before = len(businesses)
            businesses = [b for b in businesses if b.get('phone')]
            logger.info(f"Filtered to businesses with phone: {len(businesses)}/{before}")

        # Calculate stats
        with_phone = sum(1 for b in businesses if b.get('phone'))
        with_website = sum(1 for b in businesses if b.get('website'))
        ratings = [b['rating'] for b in businesses if b.get('rating')]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        logger.info(f"Stats - Phone: {with_phone}, Website: {with_website}, Avg Rating: {round(avg_rating, 1)}")
        logger.info(f"Scrape completed successfully!")

        return {
            "success": True,
            "total": len(businesses),
            "stats": {
                "with_phone": with_phone,
                "with_website": with_website,
                "no_website": len(businesses) - with_website,
                "avg_rating": round(avg_rating, 1)
            },
            "businesses": businesses
        }

    except Exception as e:
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        logger.error(f"ERROR in scrape endpoint: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
