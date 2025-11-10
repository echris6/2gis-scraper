"""
Data export and lead filtering for 2GIS scraper
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

import config

logger = logging.getLogger(__name__)


class DataExporter:
    """Handles data export and lead filtering"""

    def __init__(self, output_dir: str = None):
        """
        Initialize data exporter

        Args:
            output_dir: Directory for output files (default from config)
        """
        self.output_dir = Path(output_dir or config.DEFAULT_OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Exporter initialized: {self.output_dir}")

    @staticmethod
    def filter_businesses(
        businesses: List[Dict],
        no_website: bool = None,
        min_rating: float = None,
        min_reviews: int = None,
        require_phone: bool = None
    ) -> List[Dict]:
        """
        Filter businesses based on criteria

        Args:
            businesses: List of business dictionaries
            no_website: Only businesses without websites
            min_rating: Minimum rating threshold
            min_reviews: Minimum review count
            require_phone: Only businesses with phone numbers

        Returns:
            Filtered list of businesses
        """
        # Use config defaults if not specified
        if no_website is None:
            no_website = config.FILTER_NO_WEBSITE
        if min_rating is None:
            min_rating = config.FILTER_MIN_RATING
        if min_reviews is None:
            min_reviews = config.FILTER_MIN_REVIEWS
        if require_phone is None:
            require_phone = config.FILTER_REQUIRE_PHONE

        filtered = businesses.copy()
        original_count = len(filtered)

        # Filter: no website (qualified leads)
        if no_website:
            filtered = [b for b in filtered if not b.get('website')]
            logger.info(f"Filter no_website: {len(filtered)}/{original_count} businesses")

        # Filter: minimum rating
        if min_rating is not None:
            filtered = [
                b for b in filtered
                if b.get('rating') is not None and b['rating'] >= min_rating
            ]
            logger.info(f"Filter min_rating>={min_rating}: {len(filtered)} businesses")

        # Filter: minimum reviews
        if min_reviews is not None:
            filtered = [
                b for b in filtered
                if b.get('review_count') is not None and b['review_count'] >= min_reviews
            ]
            logger.info(f"Filter min_reviews>={min_reviews}: {len(filtered)} businesses")

        # Filter: require phone
        if require_phone:
            filtered = [b for b in filtered if b.get('phone')]
            logger.info(f"Filter require_phone: {len(filtered)} businesses")

        logger.info(f"Filtering complete: {len(filtered)}/{original_count} businesses remain")
        return filtered

    @staticmethod
    def deduplicate(businesses: List[Dict]) -> List[Dict]:
        """
        Remove duplicate businesses based on ID

        Args:
            businesses: List of business dictionaries

        Returns:
            Deduplicated list
        """
        seen_ids = set()
        unique = []

        for business in businesses:
            bid = business.get('id')
            if bid and bid not in seen_ids:
                seen_ids.add(bid)
                unique.append(business)

        duplicates = len(businesses) - len(unique)
        if duplicates > 0:
            logger.info(f"Removed {duplicates} duplicate businesses")

        return unique

    def to_dataframe(self, businesses: List[Dict]) -> pd.DataFrame:
        """
        Convert businesses to pandas DataFrame

        Args:
            businesses: List of business dictionaries

        Returns:
            DataFrame with flattened business data
        """
        if not businesses:
            return pd.DataFrame()

        # Flatten nested fields for CSV export
        flattened = []
        for business in businesses:
            flat = {
                'id': business.get('id'),
                'name': business.get('name'),
                'address': business.get('address'),
                'phone': business.get('phone'),
                'website': business.get('website'),
                'rating': business.get('rating'),
                'review_count': business.get('review_count'),
                'rubric': ', '.join(business.get('rubric', [])),
                'has_website': 'Yes' if business.get('website') else 'No',
                'has_phone': 'Yes' if business.get('phone') else 'No',
            }

            # Add coordinates
            coords = business.get('coordinates')
            if coords:
                flat['latitude'] = coords.get('lat')
                flat['longitude'] = coords.get('lon')
            else:
                flat['latitude'] = None
                flat['longitude'] = None

            # Add schedule info
            schedule = business.get('schedule')
            if schedule:
                if schedule.get('type') == '24/7':
                    flat['hours'] = '24/7'
                else:
                    flat['hours'] = schedule.get('comments', 'See details')
            else:
                flat['hours'] = None

            # Add attribute summary
            attributes = business.get('attributes', [])
            if attributes:
                attr_names = [attr.get('name') for attr in attributes if attr.get('name')]
                flat['attributes'] = '; '.join(attr_names[:5])  # Limit to 5 for readability
            else:
                flat['attributes'] = None

            flattened.append(flat)

        df = pd.DataFrame(flattened)
        return df

    def export_csv(
        self,
        businesses: List[Dict],
        filename: str = 'businesses.csv',
        apply_filters: bool = False,
        **filter_kwargs
    ) -> str:
        """
        Export businesses to CSV

        Args:
            businesses: List of business dictionaries
            filename: Output filename
            apply_filters: Apply filtering before export
            **filter_kwargs: Filter parameters (no_website, min_rating, etc.)

        Returns:
            Path to exported file
        """
        # Apply filters if requested
        if apply_filters:
            businesses = self.filter_businesses(businesses, **filter_kwargs)

        # Deduplicate
        businesses = self.deduplicate(businesses)

        # Convert to DataFrame
        df = self.to_dataframe(businesses)

        # Export with UTF-8 BOM for proper Excel compatibility with Cyrillic
        output_path = self.output_dir / filename
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        logger.info(f"Exported {len(df)} businesses to {output_path}")
        return str(output_path)

    def export_json(
        self,
        businesses: List[Dict],
        filename: str = 'businesses.json',
        apply_filters: bool = False,
        pretty: bool = True,
        **filter_kwargs
    ) -> str:
        """
        Export businesses to JSON

        Args:
            businesses: List of business dictionaries
            filename: Output filename
            apply_filters: Apply filtering before export
            pretty: Pretty-print JSON
            **filter_kwargs: Filter parameters

        Returns:
            Path to exported file
        """
        # Apply filters if requested
        if apply_filters:
            businesses = self.filter_businesses(businesses, **filter_kwargs)

        # Deduplicate
        businesses = self.deduplicate(businesses)

        # Export
        output_path = self.output_dir / filename
        indent = 2 if pretty else None

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(businesses, f, ensure_ascii=False, indent=indent)

        logger.info(f"Exported {len(businesses)} businesses to {output_path}")
        return str(output_path)

    def export_qualified_leads(
        self,
        businesses: List[Dict],
        filename: str = 'qualified_leads.csv',
        min_rating: float = None,
        min_reviews: int = None
    ) -> str:
        """
        Export qualified leads (businesses without websites)

        Args:
            businesses: List of business dictionaries
            filename: Output filename
            min_rating: Minimum rating filter (optional)
            min_reviews: Minimum review count filter (optional)

        Returns:
            Path to exported file
        """
        logger.info("Exporting qualified leads (no website)")

        return self.export_csv(
            businesses,
            filename=filename,
            apply_filters=True,
            no_website=True,
            min_rating=min_rating,
            min_reviews=min_reviews,
            require_phone=True  # Leads should have phone numbers
        )

    def export_all_formats(
        self,
        businesses: List[Dict],
        base_filename: str = 'businesses',
        export_leads: bool = True
    ) -> Dict[str, str]:
        """
        Export to all formats

        Args:
            businesses: List of business dictionaries
            base_filename: Base filename (without extension)
            export_leads: Also export qualified leads

        Returns:
            Dictionary mapping format to file path
        """
        exports = {}

        # Full CSV
        csv_path = self.export_csv(
            businesses,
            filename=f'{base_filename}.csv'
        )
        exports['csv'] = csv_path

        # Full JSON
        json_path = self.export_json(
            businesses,
            filename=f'{base_filename}.json'
        )
        exports['json'] = json_path

        # Qualified leads CSV
        if export_leads:
            leads_path = self.export_qualified_leads(
                businesses,
                filename=f'{base_filename}_qualified_leads.csv'
            )
            exports['qualified_leads'] = leads_path

        return exports

    def get_summary_stats(self, businesses: List[Dict]) -> Dict:
        """
        Get summary statistics about businesses

        Args:
            businesses: List of business dictionaries

        Returns:
            Dictionary with summary stats
        """
        if not businesses:
            return {
                'total': 0,
                'with_website': 0,
                'without_website': 0,
                'with_phone': 0,
                'with_rating': 0,
                'avg_rating': None
            }

        with_website = sum(1 for b in businesses if b.get('website'))
        without_website = sum(1 for b in businesses if not b.get('website'))
        with_phone = sum(1 for b in businesses if b.get('phone'))
        with_rating = sum(1 for b in businesses if b.get('rating') is not None)

        ratings = [b['rating'] for b in businesses if b.get('rating') is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        return {
            'total': len(businesses),
            'with_website': with_website,
            'without_website': without_website,
            'with_phone': with_phone,
            'with_rating': with_rating,
            'avg_rating': round(avg_rating, 2) if avg_rating else None
        }

    def print_summary(self, businesses: List[Dict]):
        """
        Print summary statistics to console

        Args:
            businesses: List of business dictionaries
        """
        stats = self.get_summary_stats(businesses)

        print("\n" + "="*50)
        print("SCRAPING SUMMARY")
        print("="*50)
        print(f"Total businesses: {stats['total']}")
        print(f"With website: {stats['with_website']} ({stats['with_website']/stats['total']*100:.1f}%)" if stats['total'] > 0 else "")
        print(f"WITHOUT website (qualified leads): {stats['without_website']} ({stats['without_website']/stats['total']*100:.1f}%)" if stats['total'] > 0 else "")
        print(f"With phone: {stats['with_phone']} ({stats['with_phone']/stats['total']*100:.1f}%)" if stats['total'] > 0 else "")
        print(f"With rating: {stats['with_rating']}")
        print(f"Average rating: {stats['avg_rating']}" if stats['avg_rating'] else "")
        print("="*50 + "\n")
