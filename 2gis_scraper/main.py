#!/usr/bin/env python3
"""
2GIS Business Scraper - Main CLI Entry Point

Extract business leads from 2GIS search results across multiple countries.
Optimized for finding qualified leads (businesses without websites).
"""

import argparse
import logging
import sys
from pathlib import Path

from scraper import TwoGISScraper
from exporter import DataExporter
import config


def setup_logging(level: str = 'INFO', log_to_file: bool = False):
    """
    Configure logging

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_to_file: Whether to log to file
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_to_file:
        handlers.append(logging.FileHandler(config.LOG_FILE))

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description='2GIS Business Scraper - Extract qualified leads from 2GIS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape restaurants in Dubai (5 pages)
  python main.py --city dubai --query "restaurant" --pages 5

  # Find auto detailing leads in Moscow (no website filter)
  python main.py --city moscow --query "auto detailing" --no-website-only

  # ENRICH with contact info to find TRUE leads without websites
  python main.py --city dubai --query "car wash" --pages 2 --enrich-contacts --no-website-only

  # Scrape cafes with minimum rating filter
  python main.py --city spb --query "cafe" --min-rating 4.0 --pages 3

  # Export to specific file
  python main.py --city almaty --query "barbershop" --output leads.csv

  # Disable caching for fresh data
  python main.py --city dubai --query "gym" --no-cache

  # Scrape multiple queries
  python main.py --city moscow --queries "cafe" "restaurant" "bar" --pages 2

Supported cities:
  Russia: moscow, spb, novosibirsk, kazan, etc.
  UAE: dubai, abu_dhabi, sharjah
  Kazakhstan: almaty, astana
  Other: bishkek, santiago, prague, milan
        """
    )

    # Required arguments
    parser.add_argument(
        '--city',
        required=True,
        help='City name (e.g., dubai, moscow, almaty)'
    )

    # Query options
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument(
        '--query',
        help='Search query (e.g., "restaurant", "auto detailing")'
    )
    query_group.add_argument(
        '--queries',
        nargs='+',
        help='Multiple search queries to scrape'
    )

    # Scraping options
    parser.add_argument(
        '--pages',
        type=int,
        default=None,
        help='Maximum pages to scrape per query (default: auto-detect all)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=config.DEFAULT_DELAY,
        help=f'Delay between requests in seconds (default: {config.DEFAULT_DELAY})'
    )
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable HTML response caching'
    )
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='Clear cache before scraping'
    )
    parser.add_argument(
        '--enrich-contacts',
        action='store_true',
        help='Visit each business page to get phone/website (SLOW but accurate for lead filtering)'
    )

    # Filtering options
    parser.add_argument(
        '--no-website-only',
        action='store_true',
        help='Only export businesses WITHOUT websites (qualified leads)'
    )
    parser.add_argument(
        '--min-rating',
        type=float,
        default=None,
        help='Minimum rating filter (e.g., 4.0)'
    )
    parser.add_argument(
        '--min-reviews',
        type=int,
        default=None,
        help='Minimum review count filter'
    )
    parser.add_argument(
        '--require-phone',
        action='store_true',
        help='Only export businesses with phone numbers'
    )

    # Output options
    parser.add_argument(
        '--output',
        default='businesses.csv',
        help='Output filename (default: businesses.csv)'
    )
    parser.add_argument(
        '--format',
        choices=['csv', 'json', 'both'],
        default='csv',
        help='Output format (default: csv)'
    )
    parser.add_argument(
        '--output-dir',
        default=config.DEFAULT_OUTPUT_DIR,
        help=f'Output directory (default: {config.DEFAULT_OUTPUT_DIR})'
    )
    parser.add_argument(
        '--export-leads',
        action='store_true',
        help='Also export qualified_leads.csv (businesses without websites)'
    )

    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=config.LOG_LEVEL,
        help=f'Logging level (default: {config.LOG_LEVEL})'
    )
    parser.add_argument(
        '--log-file',
        action='store_true',
        default=config.LOG_TO_FILE,
        help='Log to file'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(level=args.log_level, log_to_file=args.log_file)
    logger = logging.getLogger(__name__)

    try:
        # Initialize scraper
        cache_enabled = not args.no_cache
        scraper = TwoGISScraper(
            cache_enabled=cache_enabled,
            delay=args.delay
        )

        # Clear cache if requested
        if args.clear_cache:
            deleted = scraper.clear_cache()
            logger.info(f"Cleared cache: {deleted} files deleted")

        # Initialize exporter
        exporter = DataExporter(output_dir=args.output_dir)

        # Determine queries to scrape
        queries = [args.query] if args.query else args.queries

        # Scrape data
        all_businesses = []

        if len(queries) == 1:
            # Single query
            businesses = scraper.scrape(
                city=args.city,
                query=queries[0],
                max_pages=args.pages
            )
            all_businesses.extend(businesses)

        else:
            # Multiple queries
            results = scraper.scrape_multiple_queries(
                city=args.city,
                queries=queries,
                max_pages_per_query=args.pages
            )
            for query, businesses in results.items():
                all_businesses.extend(businesses)

        # Deduplicate businesses across queries
        all_businesses = exporter.deduplicate(all_businesses)

        # Enrich with contact information if requested
        if args.enrich_contacts:
            logger.info("\n" + "="*50)
            logger.info("ENRICHING WITH CONTACT INFORMATION")
            logger.info("="*50)
            logger.info(f"Visiting {len(all_businesses)} business pages to extract phone/website...")
            logger.info(f"This will take approximately {len(all_businesses) * args.delay:.0f} seconds")
            logger.info("="*50 + "\n")

            from profile_scraper import enrich_businesses
            all_businesses = enrich_businesses(
                all_businesses,
                city=args.city,
                headless=True,
                delay=args.delay
            )

        # Print summary
        exporter.print_summary(all_businesses)

        # Export data
        if not all_businesses:
            logger.warning("No businesses found, nothing to export")
            return

        # Determine export parameters
        filter_kwargs = {
            'no_website': args.no_website_only,
            'min_rating': args.min_rating,
            'min_reviews': args.min_reviews,
            'require_phone': args.require_phone
        }

        # Export based on format
        if args.format == 'csv':
            output_path = exporter.export_csv(
                all_businesses,
                filename=args.output,
                apply_filters=True,
                **filter_kwargs
            )
            print(f"\n✓ Exported to: {output_path}")

        elif args.format == 'json':
            output_path = exporter.export_json(
                all_businesses,
                filename=args.output,
                apply_filters=True,
                **filter_kwargs
            )
            print(f"\n✓ Exported to: {output_path}")

        elif args.format == 'both':
            base_name = Path(args.output).stem
            csv_path = exporter.export_csv(
                all_businesses,
                filename=f'{base_name}.csv',
                apply_filters=True,
                **filter_kwargs
            )
            json_path = exporter.export_json(
                all_businesses,
                filename=f'{base_name}.json',
                apply_filters=True,
                **filter_kwargs
            )
            print(f"\n✓ Exported to:")
            print(f"  - {csv_path}")
            print(f"  - {json_path}")

        # Export qualified leads if requested
        if args.export_leads:
            leads_filename = f"{Path(args.output).stem}_qualified_leads.csv"
            leads_path = exporter.export_qualified_leads(
                all_businesses,
                filename=leads_filename,
                min_rating=args.min_rating,
                min_reviews=args.min_reviews
            )
            print(f"  - {leads_path} (qualified leads)")

        # Show cache stats
        cache_stats = scraper.get_cache_stats()
        if cache_stats['enabled']:
            print(f"\nCache: {cache_stats['total_files']} files, {cache_stats['total_size_mb']} MB")

        print("\n✓ Scraping complete!\n")

    except KeyboardInterrupt:
        logger.info("\nScraping interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
