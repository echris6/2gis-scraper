#!/bin/bash
# Deploy frontend to Vercel with environment variables

echo "Deploying to Vercel..."
echo ""

# Deploy to production with environment variable
vercel --prod \
  --env NEXT_PUBLIC_API_URL=https://2gis-scraper-production.up.railway.app \
  --yes
