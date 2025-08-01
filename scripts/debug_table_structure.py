#!/usr/bin/env python3
"""
Debug script to analyze the table structure and identify the correct table.
"""

import sys
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from utils.playwright_scraper import PlaywrightScraper
import asyncio
from bs4 import BeautifulSoup


async def analyze_table_structure():
    """Analyze the table structure to identify the correct table."""
    print("🔍 Analyzing Table Structure")
    print("=" * 60)
    
    try:
        async with PlaywrightScraper() as scraper:
            url = "https://valorant.fandom.com/wiki/Weapon_Skins"
            await scraper.page.goto(url, wait_until="networkidle", timeout=30000)
            await scraper.page.wait_for_selector("table.wikitable.sortable", timeout=10000)
            
            content = await scraper.page.content()
            soup = BeautifulSoup(content, "lxml")
            
            # Find all tables
            all_tables = soup.find_all("table")
            print(f"📊 Found {len(all_tables)} total tables")
            
            # Find tables with class "wikitable sortable"
            wikitable_tables = soup.select("table.wikitable.sortable")
            print(f"📋 Found {len(wikitable_tables)} tables with class 'wikitable sortable'")
            
            for i, table in enumerate(wikitable_tables):
                print(f"\n🔍 Analyzing Table {i + 1}:")
                
                # Get table headers
                headers = table.find_all("th")
                header_texts = [h.get_text(strip=True) for h in headers]
                print(f"   Headers: {header_texts}")
                
                # Count rows
                rows = table.find_all("tr")
                print(f"   Total rows: {len(rows)}")
                
                # Count data rows (excluding header)
                data_rows = rows[1:] if rows else []
                print(f"   Data rows: {len(data_rows)}")
                
                # Sample first few rows
                print(f"   Sample rows:")
                for j, row in enumerate(data_rows[:5]):
                    cells = row.find_all("td")
                    cell_texts = [cell.get_text(strip=True)[:50] for cell in cells]
                    print(f"     Row {j + 1}: {cell_texts}")
                
                # Look for price data
                price_cells = table.find_all("td", {"data-sort-value": True})
                print(f"   Cells with data-sort-value: {len(price_cells)}")
                
                if price_cells:
                    sample_prices = []
                    for cell in price_cells[:5]:
                        price_text = cell.get_text(strip=True)
                        sample_prices.append(price_text)
                    print(f"   Sample prices: {sample_prices}")
                
                # Look for any numbers that could be prices
                import re
                all_text = table.get_text()
                price_matches = re.findall(r'\d{3,4}(?:,\d{3})*', all_text)
                unique_prices = list(set(price_matches))
                print(f"   Unique price-like numbers: {len(unique_prices)}")
                if unique_prices:
                    print(f"   Sample price-like numbers: {unique_prices[:10]}")
                
                print("-" * 40)
            
            # Identify the main table
            print(f"\n🎯 IDENTIFYING MAIN TABLE:")
            
            for i, table in enumerate(wikitable_tables):
                rows = table.find_all("tr")
                data_rows = rows[1:] if rows else []
                
                # Count rows with price data
                price_rows = 0
                for row in data_rows:
                    cells = row.find_all("td")
                    for cell in cells:
                        cell_text = cell.get_text(strip=True)
                        if re.search(r'\d{3,4}(?:,\d{3})*', cell_text):
                            price_rows += 1
                            break
                
                print(f"   Table {i + 1}: {price_rows} rows with price data")
                
                if price_rows > 100:  # Main table should have many rows with prices
                    print(f"   ✅ Table {i + 1} appears to be the main weapon skins table")
                    return i
            
            print("   ❌ Could not identify main table")
            return None
            
    except Exception as e:
        print(f"❌ Error analyzing table structure: {e}")
        return None


def main():
    """Run the table structure analysis."""
    print("🚀 VALORANT TABLE STRUCTURE DEBUG")
    print("=" * 60)
    
    try:
        result = asyncio.run(analyze_table_structure())
        
        if result is not None:
            print(f"\n✅ Main table identified as table {result + 1}")
            print(f"   Update the code to use tables[{result}] instead of tables[1]")
        else:
            print(f"\n❌ Could not identify main table")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 