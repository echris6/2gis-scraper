# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies required for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY 2gis_scraper/requirements.txt ./2gis_scraper/requirements.txt
COPY api/requirements.txt ./api/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r api/requirements.txt
RUN pip install --no-cache-dir -r 2gis_scraper/requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY 2gis_scraper ./2gis_scraper
COPY api ./api

# Copy and set up start script
COPY railway-start.sh /app/railway-start.sh
RUN chmod +x /app/railway-start.sh

# Expose port
EXPOSE 8000

# Start the application using the bash script
CMD ["/app/railway-start.sh"]
