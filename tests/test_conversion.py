#!/usr/bin/env python3
"""
Test script for currency conversion accuracy.
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

from utils.currencyMap import calculate_currency_amount


def test_vp_conversions():
    """Test VP to USD conversions with known values."""
    print("🧪 Testing VP to USD Conversions")
    print("=" * 40)
    
    test_cases = [
        (1000, "$9.09"),
        (1100, "$10.00"),
        (11000, "$100.00"),
        (22000, "$200.00"),
        (50000, "$454.55"),
    ]
    
    print("Expected conversions:")
    for vp, expected in test_cases:
        print(f"  {vp:,} VP = {expected}")
    
    print("\nActual conversions:")
    for vp, expected in test_cases:
        actual = calculate_currency_amount(vp, "United States Dollar ($)")
        print(f"  {vp:,} VP = {actual}")
        
        try:
            actual_value = float(actual.replace("$", "").replace(",", ""))
            expected_value = float(expected.replace("$", "").replace(",", ""))
            if abs(actual_value - expected_value) < 1.0:
                print(f"    ✅ Close to expected")
            else:
                print(f"    ❌ Significantly different from expected")
        except ValueError:
            print(f"    ❌ Could not parse result")
    
    print("\n" + "=" * 40)
    
    total_vp = 150000
    total_usd = calculate_currency_amount(total_vp, "United States Dollar ($)")
    print(f"Total skin collection ({total_vp:,} VP) = {total_usd}")
    
    print("\nOther currencies:")
    currencies = [
        "Euro (€)",
        "Pound Sterling (£)",
        "Australian Dollar (A$)",
        "Canadian Dollar (CA$)"
    ]
    
    for currency in currencies:
        amount = calculate_currency_amount(total_vp, currency)
        print(f"  {currency}: {amount}")


if __name__ == "__main__":
    test_vp_conversions() 