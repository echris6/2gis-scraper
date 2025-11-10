#!/usr/bin/env python3
"""
Script to get car detailing businesses in Moscow without websites
Uses the existing scraper with visible browser
"""
import subprocess
import sys
import json
import os

# Change to the scraper directory
script_dir = os.path.dirname(os.path.abspath(__file__))
scraper_dir = os.path.join(script_dir, 'yandex-maps-scraper', 'python')
scraper_script = os.path.join(scraper_dir, 'scrape_with_browser.py')

# Run the scraper to get 100 businesses without websites
# Checking up to 300 businesses (adjust if needed)
print("Starting scraper to find 100 car detailing businesses in Moscow without websites...")
print("Note: You may need to solve CAPTCHAs in the browser window that opens.")
print("=" * 70)

try:
    result = subprocess.run(
        [sys.executable, scraper_script, "Car detailing moscow", "100", "300"],
        cwd=scraper_dir,
        capture_output=True,
        text=True,
        timeout=3600  # 1 hour timeout
    )
    
    # Print stderr (progress messages)
    if result.stderr:
        print(result.stderr)
    
    # Parse and display results
    if result.stdout:
        try:
            data = json.loads(result.stdout)
            if 'error' in data:
                print(f"Error: {data['error']}")
                sys.exit(1)
            
            results = data.get('results', [])
            count = data.get('count', 0)
            
            print("\n" + "=" * 70)
            print(f"FOUND {count} BUSINESSES WITHOUT WEBSITES")
            print("=" * 70)
            
            if results:
                # Save to file
                output_file = os.path.join(script_dir, 'car_detailing_leads_no_websites.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"\nResults saved to: {output_file}")
                
                # Also create a simple text list
                txt_file = os.path.join(script_dir, 'car_detailing_leads_no_websites.txt')
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write("CAR DETAILING BUSINESSES IN MOSCOW WITHOUT WEBSITES\n")
                    f.write("=" * 70 + "\n\n")
                    for i, business in enumerate(results, 1):
                        f.write(f"{i}. {business.get('title', 'Unknown')}\n")
                        if business.get('address'):
                            f.write(f"   Address: {business['address']}\n")
                        if business.get('phone'):
                            f.write(f"   Phone: {business['phone']}\n")
                        if business.get('url'):
                            f.write(f"   Yandex Maps URL: {business['url']}\n")
                        f.write("\n")
                print(f"Text list saved to: {txt_file}")
                
                # Print first 10 to console
                print("\nFirst 10 businesses without websites:")
                print("-" * 70)
                for i, business in enumerate(results[:10], 1):
                    print(f"{i}. {business.get('title', 'Unknown')}")
                    if business.get('address'):
                        print(f"   Address: {business['address']}")
                    if business.get('phone'):
                        print(f"   Phone: {business['phone']}")
                    print()
                
                if len(results) > 10:
                    print(f"... and {len(results) - 10} more (see files for full list)")
            else:
                print("\nNo businesses without websites found.")
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON output: {e}")
            print("Raw output:", result.stdout)
            sys.exit(1)
    else:
        print("No output from scraper")
        sys.exit(1)
        
except subprocess.TimeoutExpired:
    print("Scraper timed out after 1 hour")
    sys.exit(1)
except Exception as e:
    print(f"Error running scraper: {e}")
    sys.exit(1)








