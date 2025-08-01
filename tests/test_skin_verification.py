#!/usr/bin/env python3
"""
Comprehensive test script for skin verification and scraping accuracy.
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

from utils.data_sources import get_data_source_manager
from utils.skin_verifier import generate_verification_report, verify_skins_from_html
from utils.playwright_scraper import scrape_fandom_wiki_sync


def test_skin_scraping():
    """Test skin scraping and generate verification report."""
    print("🧪 Testing Skin Scraping and Verification")
    print("=" * 60)
    
    try:
        # Test Playwright scraping
        print("🔄 Testing Playwright scraping...")
        prices = scrape_fandom_wiki_sync()
        
        if prices and len(prices) > 0:
            total_price = sum(prices)
            print(f"✅ Successfully scraped {len(prices)} skin prices")
            print(f"💰 Total price: {total_price:,} VP")
            print(f"📊 Average price: {total_price / len(prices):,.0f} VP")
            
            # Test data source manager
            print("\n🔄 Testing data source manager...")
            manager = get_data_source_manager()
            manager_prices = manager.get_prices()
            
            if manager_prices and len(manager_prices) > 0:
                manager_total = sum(manager_prices)
                print(f"✅ Data source manager returned {len(manager_prices)} prices")
                print(f"💰 Total price: {manager_total:,} VP")
                
                # Compare results
                if len(prices) == len(manager_prices):
                    print("✅ Price counts match between direct scraping and manager")
                else:
                    print(f"⚠️  Price count mismatch: {len(prices)} vs {len(manager_prices)}")
                
                if total_price == manager_total:
                    print("✅ Total prices match between direct scraping and manager")
                else:
                    print(f"⚠️  Total price mismatch: {total_price:,} vs {manager_total:,}")
                
                # Get statistics
                stats = manager.get_price_statistics()
                print(f"\n📊 Statistics:")
                print(f"   Total Skins: {stats['total_skins']:,}")
                print(f"   Total Price: {stats['total_price']:,} VP")
                print(f"   Average Price: {stats['average_price']:,.0f} VP")
                print(f"   Min Price: {stats['min_price']:,} VP")
                print(f"   Max Price: {stats['max_price']:,} VP")
                print(f"   Price Range: {stats['price_range']:,} VP")
                
                return True
            else:
                print("❌ Data source manager returned no prices")
                return False
        else:
            print("❌ No prices scraped")
            return False
            
    except Exception as e:
        print(f"❌ Skin scraping test failed: {e}")
        return False


def test_verification_system():
    """Test the skin verification system."""
    print("\n🔍 Testing Skin Verification System")
    print("=" * 60)
    
    try:
        # Get HTML content using Playwright
        from utils.playwright_scraper import PlaywrightScraper
        import asyncio
        
        async def get_html_content():
            async with PlaywrightScraper() as scraper:
                url = "https://valorant.fandom.com/wiki/Weapon_Skins"
                await scraper.page.goto(url, wait_until="networkidle", timeout=30000)
                await scraper.page.wait_for_selector("table.wikitable.sortable", timeout=10000)
                return await scraper.page.content()
        
        html_content = asyncio.run(get_html_content())
        
        if not html_content:
            print("❌ Could not get HTML content for verification")
            return False
        
        # Run verification
        from utils.skin_verifier import SkinVerifier
        verifier = SkinVerifier()
        analysis = verifier.verify_skins_from_html(html_content)
        report = verifier.generate_report(analysis)
        
        print(report)
        
        # Check if we found a reasonable number of purchasable skins
        total_skins = analysis['total_skins']
        if total_skins >= 400:  # Should find at least 400 purchasable skins
            print("✅ Verification System passed")
            return True
        else:
            print(f"❌ Verification System failed - only found {total_skins} purchasable skins")
            return False
            
    except Exception as e:
        print(f"❌ Verification test failed: {e}")
        return False


def test_price_accuracy():
    """Test price accuracy against known values."""
    print("\n💰 Testing Price Accuracy")
    print("=" * 60)
    
    try:
        # Test with data source manager
        manager = get_data_source_manager()
        prices = manager.get_prices()
        
        if not prices:
            print("❌ No prices to test")
            return False
        
        # Analyze price distribution
        price_ranges = {
            "875": 0,    # Select Edition
            "1275": 0,   # Deluxe Edition
            "1775": 0,   # Premium Edition
            "2175": 0,   # Exclusive Edition
            "2375": 0,   # Exclusive Edition (variant)
            "2675": 0,   # Exclusive Edition (variant)
            "2475": 0,   # Ultra Edition
            "2975": 0,   # Ultra Edition (variant)
            "1750": 0,   # Select Melee
            "2550": 0,   # Deluxe Melee
            "3550": 0,   # Premium Melee
            "4350": 0,   # Exclusive Melee
            "5350": 0,   # Exclusive Melee (variant)
            "4950": 0,   # Ultra Melee
            "5950": 0,   # Ultra Melee (variant)
        }
        
        for price in prices:
            price_str = str(price)
            if price_str in price_ranges:
                price_ranges[price_str] += 1
        
        print("📊 Price Distribution:")
        for price, count in sorted(price_ranges.items(), key=lambda x: int(x[0])):
            if count > 0:
                print(f"   {price} VP: {count:,} skins")
        
        # Check for unexpected prices
        unexpected_prices = [p for p in prices if str(p) not in price_ranges]
        if unexpected_prices:
            print(f"\n⚠️  Unexpected prices found:")
            for price in set(unexpected_prices):
                count = unexpected_prices.count(price)
                print(f"   {price} VP: {count} skins")
        
        total_expected_prices = sum(price_ranges.values())
        if total_expected_prices == len(prices):
            print(f"\n✅ All prices are within expected ranges")
            return True
        else:
            print(f"\n⚠️  {len(prices) - total_expected_prices} prices outside expected ranges")
            return False
            
    except Exception as e:
        print(f"❌ Price accuracy test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("🚀 VALORANT SKIN VERIFICATION SUITE")
    print("=" * 60)
    
    tests = [
        ("Skin Scraping", test_skin_scraping),
        ("Verification System", test_verification_system),
        ("Price Accuracy", test_price_accuracy),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Skin scraping is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 