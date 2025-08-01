import logging
import requests
import json
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Cache for exchange rates
EXCHANGE_RATE_CACHE_FILE = Path("cache/exchange_rates.json")
EXCHANGE_RATE_CACHE_DURATION = timedelta(hours=24)  # Cache for 24 hours

# Base currency conversion rates (VP to USD)
# Based on Valorant's actual pricing: 11000 VP = $100 USD
VP_TO_USD_RATE = 1 / 110  # 1 VP ≈ $0.00909 USD

# Currency mapping with format strings and base prices
CURRENCY_MAP: Dict[str, Tuple[str, float]] = {
    "United States Dollar ($)": ("${:,.2f}", 99.99),
    "Australian Dollar (A$)": ("A${:,.2f}", 129.99),
    "Brazilian Real (R$)": ("R${:,.2f}", 349.9),
    "Canadian Dollar (CA$)": ("CA${:,.2f}", 139.99),
    "Euro (€)": ("€{:,.2f}", 100),
    "Indian Rupee (₹)": ("₹{:,.2f}", 7900),
    "Malaysian Ringgit (MYR)": ("MYR{:,.2f}", 199.90),
    "Mexican Peso (MX$)": ("MX${:,.2f}", 1999),
    "New Zealand Dollar (NZ$)": ("NZ${:,.2f}", 144.99),
    "Russian Ruble (₽)": ("₽{:,.2f}", 5990),
    "Singapore Dollar (SGD)": ("SGD{:,.2f}", 128.98),
    "Turkish Lira (₺)": ("₺{:,.2f}", 700),
    "Pound Sterling (£)": ("£{:,.2f}", 90)
}


class CurrencyConverter:
    """Enhanced currency converter with live exchange rates and caching."""
    
    def __init__(self):
        self.cache_file = EXCHANGE_RATE_CACHE_FILE
        self.cache_file.parent.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_exchange_rates(self) -> Dict[str, float]:
        """Get current exchange rates with caching."""
        cached_rates = self._get_cached_rates()
        if cached_rates is not None:
            return cached_rates
        
        rates = self._fetch_exchange_rates()
        self._cache_rates(rates)
        return rates
    
    def _get_cached_rates(self) -> Optional[Dict[str, float]]:
        """Get cached exchange rates if they exist and are not expired."""
        try:
            if not self.cache_file.exists():
                return None
            
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time < EXCHANGE_RATE_CACHE_DURATION:
                return cache_data['rates']
            
            logger.info("Exchange rate cache expired, fetching fresh rates")
            return None
            
        except Exception as e:
            logger.warning(f"Error reading exchange rate cache: {e}")
            return None
    
    def _cache_rates(self, rates: Dict[str, float]) -> None:
        """Cache the exchange rates with timestamp."""
        try:
            cache_data = {
                'rates': rates,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info("Cached exchange rates successfully")
            
        except Exception as e:
            logger.error(f"Error caching exchange rates: {e}")
    
    def _fetch_exchange_rates(self) -> Dict[str, float]:
        """Fetch live exchange rates from multiple sources."""
        sources = [
            self._fetch_from_exchangerate_api,
            self._fetch_from_fallback_api,
            self._get_fallback_rates
        ]
        
        for i, source_func in enumerate(sources):
            try:
                logger.info(f"Trying exchange rate source {i + 1}")
                rates = source_func()
                if rates:
                    logger.info(f"Successfully fetched rates from source {i + 1}")
                    return rates
            except Exception as e:
                logger.warning(f"Exchange rate source {i + 1} failed: {e}")
                continue
        
        raise Exception("All exchange rate sources failed")
    
    def _fetch_from_exchangerate_api(self) -> Dict[str, float]:
        """Fetch rates from a free exchange rate API."""
        try:
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            currency_mapping = {
                'USD': 1.0,
                'AUD': rates.get('AUD', 1.5),
                'BRL': rates.get('BRL', 5.0),
                'CAD': rates.get('CAD', 1.35),
                'EUR': rates.get('EUR', 0.85),
                'INR': rates.get('INR', 75.0),
                'MYR': rates.get('MYR', 4.2),
                'MXN': rates.get('MXN', 20.0),
                'NZD': rates.get('NZD', 1.45),
                'RUB': rates.get('RUB', 75.0),
                'SGD': rates.get('SGD', 1.35),
                'TRY': rates.get('TRY', 7.5),
                'GBP': rates.get('GBP', 0.75)
            }
            
            return currency_mapping
            
        except Exception as e:
            logger.error(f"Error fetching from exchange rate API: {e}")
            raise
    
    def _fetch_from_fallback_api(self) -> Dict[str, float]:
        """Fetch from a backup exchange rate API."""
        try:
            raise Exception("Fallback API not implemented")
            
        except Exception as e:
            logger.error(f"Error fetching from fallback API: {e}")
            raise
    
    def _get_fallback_rates(self) -> Dict[str, float]:
        """Get fallback rates based on approximate values."""
        logger.warning("Using fallback exchange rates")
        
        return {
            'USD': 1.0,
            'AUD': 1.5,
            'BRL': 5.0,
            'CAD': 1.35,
            'EUR': 0.85,
            'INR': 75.0,
            'MYR': 4.2,
            'MXN': 20.0,
            'NZD': 1.45,
            'RUB': 75.0,
            'SGD': 1.35,
            'TRY': 7.5,
            'GBP': 0.75
        }
    
    def convert_vp_to_currency(self, vp_amount: int, currency_key: str) -> str:
        """Convert VP amount to a specific currency."""
        try:
            # Get currency info
            if currency_key not in CURRENCY_MAP:
                raise ValueError(f"Invalid currency key: {currency_key}")
            
            format_string, base_price = CURRENCY_MAP[currency_key]
            
            # Convert VP to USD first
            usd_amount = vp_amount * VP_TO_USD_RATE
            
            # Get the currency code
            currency_code = self._get_currency_code(currency_key)
            
            # For USD, use the amount directly
            if currency_code == "USD":
                target_amount = usd_amount
            else:
                # For other currencies, apply exchange rates
                rates = self.get_exchange_rates()
                if currency_code not in rates:
                    raise ValueError(f"Exchange rate not available for {currency_code}")
                target_amount = usd_amount * rates[currency_code]
            
            # Format the result
            formatted_amount = format_string.format(target_amount)
            
            # Clean up trailing zeros and decimal point
            return formatted_amount.rstrip('0').rstrip('.')
            
        except Exception as e:
            logger.error(f"Error converting VP to currency: {e}")
            return f"Error: {str(e)}"
    
    def _get_currency_code(self, currency_key: str) -> str:
        """Extract currency code from currency key."""
        currency_codes = {
            "United States Dollar ($)": "USD",
            "Australian Dollar (A$)": "AUD",
            "Brazilian Real (R$)": "BRL",
            "Canadian Dollar (CA$)": "CAD",
            "Euro (€)": "EUR",
            "Indian Rupee (₹)": "INR",
            "Malaysian Ringgit (MYR)": "MYR",
            "Mexican Peso (MX$)": "MXN",
            "New Zealand Dollar (NZ$)": "NZD",
            "Russian Ruble (₽)": "RUB",
            "Singapore Dollar (SGD)": "SGD",
            "Turkish Lira (₺)": "TRY",
            "Pound Sterling (£)": "GBP"
        }
        return currency_codes.get(currency_key, "USD")
    
    def refresh_rates(self) -> None:
        """Force refresh the exchange rates by clearing the cache."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                logger.info("Exchange rate cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing exchange rate cache: {e}")


# Global converter instance
_converter = CurrencyConverter()


# Backward compatibility function
def calculate_currency_amount(vp_amount: int, currency_key: str) -> str:
    """
    Calculate and format currency amount for a given currency.
    
    Args:
        vp_amount: Amount in Valorant Points
        currency_key: Currency key from CURRENCY_MAP
        
    Returns:
        str: Formatted currency amount
    """
    return _converter.convert_vp_to_currency(vp_amount, currency_key)


# Export the converter for direct use
def get_currency_converter() -> CurrencyConverter:
    """Get the global currency converter instance."""
    return _converter
