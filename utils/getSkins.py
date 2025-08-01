import logging
import re
import requests
import json
import time
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

from config import NETWORK_CONFIG, URLS
from utils.data_sources import get_data_source_manager

# Constants
REQUEST_TIMEOUT = NETWORK_CONFIG["timeout"]
VP_URL = URLS["valorant_skins"]
USER_AGENT = NETWORK_CONFIG["user_agent"]
CACHE_FILE = Path("cache/skin_prices.json")
CACHE_DURATION = timedelta(hours=6)  # Cache for 6 hours


class SkinPriceFetcher:
    """Enhanced skin price fetcher with caching and multiple data sources."""
    
    def __init__(self):
        self.cache_file = CACHE_FILE
        self.cache_file.parent.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.data_source_manager = get_data_source_manager()
    
    def get_price(self) -> int:
        """
        Get the total price of all Valorant skins in VP with caching.
        
        Returns:
            int: Total price of all skins in Valorant Points (VP)
        """
        # Try to get cached data first
        cached_data = self._get_cached_prices()
        if cached_data is not None:
            logger.info("Using cached skin prices")
            return cached_data
        
        # Try multiple data sources
        price = self._fetch_from_multiple_sources()
        
        # Cache the result
        self._cache_prices(price)
        
        return price
    
    def _get_cached_prices(self) -> Optional[int]:
        """Get cached prices if they exist and are not expired."""
        try:
            if not self.cache_file.exists():
                return None
            
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time < CACHE_DURATION:
                return cache_data['price']
            
            logger.info("Cache expired, fetching fresh data")
            return None
            
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def _cache_prices(self, price: int) -> None:
        """Cache the skin prices with timestamp."""
        try:
            cache_data = {
                'price': price,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            logger.info("Cached skin prices successfully")
            
        except Exception as e:
            logger.error(f"Error caching prices: {e}")
    
    def _fetch_from_multiple_sources(self) -> int:
        """Try multiple data sources with fallback."""
        try:
            price = self.data_source_manager.get_total_price()
            logger.info(f"Successfully fetched total price: {price} VP")
            return price
            
        except Exception as e:
            logger.error(f"All data sources failed: {e}")
            raise
    
    def get_price_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about skin prices."""
        try:
            return self.data_source_manager.get_price_statistics()
        except Exception as e:
            logger.error(f"Error getting price statistics: {e}")
            return {}
    
    def refresh_cache(self) -> None:
        """Force refresh the cache by deleting the cache file."""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")


# Backward compatibility function
def getPrice() -> int:
    """
    Get the total price of all Valorant skins in VP.
    
    Returns:
        int: Total price of all skins in Valorant Points (VP)
        
    Raises:
        Exception: If there's an error fetching or parsing the data
    """
    fetcher = SkinPriceFetcher()
    return fetcher.get_price()


# Legacy functions for backward compatibility
def _extract_weapon_skin_prices(soup: BeautifulSoup) -> List[int]:
    """
    Extract weapon skin prices from the parsed HTML.
    
    Args:
        soup: BeautifulSoup object containing the parsed HTML
        
    Returns:
        List[int]: List of skin prices in VP
    """
    vp_prices = []
    
    try:
        # Find the weapon skins table (second table with class wikitable sortable)
        tables = soup.select("table.wikitable.sortable")
        if len(tables) < 2:
            raise Exception("Could not find weapon skins table")
        
        weapon_table = tables[1]
        rows = weapon_table.find_all("tr")[1:]  # Skip header row
        
        for row in rows:
            price = _extract_price_from_row(row)
            if price is not None:
                vp_prices.append(price)
        
        logger.info(f"Extracted {len(vp_prices)} weapon skin prices")
        
    except Exception as e:
        logger.error(f"Error extracting weapon skin prices: {e}")
        raise
    
    return vp_prices


def _extract_price_from_row(row) -> Optional[int]:
    """
    Extract price from a table row.
    
    Args:
        row: BeautifulSoup row element
        
    Returns:
        Optional[int]: Price in VP if found, None otherwise
    """
    try:
        # Look for td element with data-sort-value attribute
        td_element = row.find("td", {"data-sort-value": True})
        if td_element:
            price_text = re.sub(r"[\xa0\n,]", "", td_element.text.strip())
            price = int(price_text)
            return price
    except (ValueError, AttributeError) as e:
        logger.debug(f"Could not extract price from row: {e}")
        return None
    
    return None