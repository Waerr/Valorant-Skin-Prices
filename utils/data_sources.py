"""
Enhanced data sources for Valorant skin prices.
This module provides multiple data sources with fallback mechanisms.
"""

import logging
import requests
import json
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

# Import Playwright scraper
try:
    from utils.playwright_scraper import scrape_fandom_wiki_sync, scrape_with_retry_sync
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available, falling back to requests")

# Import skin verifier
try:
    from utils.skin_verifier import generate_verification_report
    VERIFICATION_AVAILABLE = True
except ImportError:
    VERIFICATION_AVAILABLE = False
    logger.warning("Skin verification not available")


class DataSource:
    """Base class for data sources."""
    
    def __init__(self, name: str):
        self.name = name
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def fetch_prices(self) -> List[int]:
        """Fetch skin prices from this source."""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if this data source is available."""
        return True


class FandomWikiSource(DataSource):
    """Data source for Fandom wiki using Playwright for better reliability."""
    
    def __init__(self):
        super().__init__("Fandom Wiki (Playwright)")
        self.url = "https://valorant.fandom.com/wiki/Weapon_Skins"
    
    def fetch_prices(self) -> List[int]:
        """Fetch prices from Fandom wiki using Playwright."""
        try:
            if PLAYWRIGHT_AVAILABLE:
                logger.info("Using Playwright for Fandom wiki scraping")
                return scrape_fandom_wiki_sync()
            else:
                logger.info("Playwright not available, using requests fallback")
                return self._fetch_with_requests()
                
        except Exception as e:
            logger.error(f"Error fetching from {self.name}: {e}")
            raise
    
    def _fetch_with_requests(self) -> List[int]:
        """Fallback method using requests + BeautifulSoup."""
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            return self._extract_prices(soup)
            
        except Exception as e:
            logger.error(f"Error fetching with requests: {e}")
            raise
    
    def _extract_prices(self, soup: BeautifulSoup) -> List[int]:
        """Extract prices from the parsed HTML."""
        prices = []
        
        try:
            tables = soup.select("table.wikitable.sortable")
            if len(tables) < 2:
                raise Exception("Could not find weapon skins table")
            
            # Process tables 2 and 3 (index 1 and 2) which contain the weapon skins
            target_tables = []
            if len(tables) > 1:
                target_tables.append(tables[1])  # Table 2
            if len(tables) > 2:
                target_tables.append(tables[2])  # Table 3
            
            if not target_tables:
                raise Exception("Could not find target tables (2 and 3)")
            
            # Process each target table
            for table_index, table in enumerate(target_tables):
                logger.info(f"Processing target table {table_index + 1} (index {1 + table_index})")
                rows = table.find_all("tr")[1:]
                
                logger.info(f"Processing {len(rows)} rows from target table {table_index + 1}")
                
                for row in rows:
                    price = self._extract_price_from_row(row)
                    if price is not None:
                        prices.append(price)
            
            logger.info(f"Extracted {len(prices)} prices from {self.name}")
            
            # Generate verification report if available
            if VERIFICATION_AVAILABLE:
                try:
                    report = generate_verification_report(str(soup))
                    logger.info("Skin verification report generated")
                    logger.debug(report)
                except Exception as e:
                    logger.warning(f"Could not generate verification report: {e}")
            
        except Exception as e:
            logger.error(f"Error extracting prices from {self.name}: {e}")
            raise
        
        return prices
    
    def _extract_price_from_row(self, row) -> Optional[int]:
        """Extract price from a table row."""
        try:
            # First try to find td element with data-sort-value attribute
            td_element = row.find("td", {"data-sort-value": True})
            if td_element:
                import re
                price_text = re.sub(r"[\xa0\n,]", "", td_element.text.strip())
                price = int(price_text)
                return price
            
            # If no data-sort-value, try to find price in any cell
            cells = row.find_all("td")
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                # Look for numbers that could be prices (3-4 digits, possibly with commas)
                price_match = re.search(r'(\d{3,4}(?:,\d{3})*)', cell_text)
                if price_match:
                    try:
                        price_text = price_match.group(1).replace(',', '')
                        price = int(price_text)
                        # Validate that it's a reasonable price
                        if 800 <= price <= 6000:  # Valid VP price range
                            return price
                    except (ValueError, AttributeError):
                        continue
                        
        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not extract price from row: {e}")
            return None
        
        return None


class FandomWikiRequestsSource(DataSource):
    """Fallback data source using requests + BeautifulSoup."""
    
    def __init__(self):
        super().__init__("Fandom Wiki (Requests)")
        self.url = "https://valorant.fandom.com/wiki/Weapon_Skins"
    
    def fetch_prices(self) -> List[int]:
        """Fetch prices from Fandom wiki using requests."""
        try:
            response = self.session.get(self.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "lxml")
            return self._extract_prices(soup)
            
        except Exception as e:
            logger.error(f"Error fetching from {self.name}: {e}")
            raise
    
    def _extract_prices(self, soup: BeautifulSoup) -> List[int]:
        """Extract prices from the parsed HTML."""
        prices = []
        
        try:
            tables = soup.select("table.wikitable.sortable")
            if len(tables) < 2:
                raise Exception("Could not find weapon skins table")
            
            weapon_table = tables[1]
            rows = weapon_table.find_all("tr")[1:]
            
            for row in rows:
                price = self._extract_price_from_row(row)
                if price is not None:
                    prices.append(price)
            
            logger.info(f"Extracted {len(prices)} prices from {self.name}")
            
            # Generate verification report if available
            if VERIFICATION_AVAILABLE:
                try:
                    report = generate_verification_report(str(soup))
                    logger.info("Skin verification report generated")
                    logger.debug(report)
                except Exception as e:
                    logger.warning(f"Could not generate verification report: {e}")
            
        except Exception as e:
            logger.error(f"Error extracting prices from {self.name}: {e}")
            raise
        
        return prices
    
    def _extract_price_from_row(self, row) -> Optional[int]:
        """Extract price from a table row."""
        try:
            td_element = row.find("td", {"data-sort-value": True})
            if td_element:
                import re
                price_text = re.sub(r"[\xa0\n,]", "", td_element.text.strip())
                price = int(price_text)
                return price
        except (ValueError, AttributeError) as e:
            logger.debug(f"Could not extract price from row: {e}")
            return None
        
        return None


class DataSourceManager:
    """Manages multiple data sources with fallback mechanisms."""
    
    def __init__(self):
        sources = []
        
        if PLAYWRIGHT_AVAILABLE:
            sources.append(FandomWikiSource())
            logger.info("Playwright scraper available - using enhanced scraping")
        else:
            sources.append(FandomWikiRequestsSource())
            logger.info("Playwright not available - using requests fallback")
        
        self.sources = sources
    
    def get_prices(self) -> List[int]:
        """Get prices from the first available source."""
        for source in self.sources:
            if not source.is_available():
                continue
            
            try:
                logger.info(f"Trying data source: {source.name}")
                prices = source.fetch_prices()
                
                if prices and len(prices) > 0:
                    logger.info(f"Successfully fetched {len(prices)} prices from {source.name}")
                    return prices
                    
            except Exception as e:
                logger.warning(f"Source {source.name} failed: {e}")
                continue
        
        raise Exception("All data sources failed")
    
    def get_total_price(self) -> int:
        """Get the total price of all skins."""
        prices = self.get_prices()
        return sum(prices)
    
    def get_price_statistics(self) -> Dict[str, Any]:
        """Get statistics about the fetched prices."""
        prices = self.get_prices()
        
        if not prices:
            return {}
        
        return {
            "total_skins": len(prices),
            "total_price": sum(prices),
            "average_price": sum(prices) / len(prices),
            "min_price": min(prices),
            "max_price": max(prices),
            "price_range": max(prices) - min(prices)
        }


# Global data source manager
_data_source_manager = DataSourceManager()


def get_data_source_manager() -> DataSourceManager:
    """Get the global data source manager instance."""
    return _data_source_manager


def get_prices_from_best_source() -> List[int]:
    """Get prices from the best available source."""
    return _data_source_manager.get_prices()


def get_total_price_from_best_source() -> int:
    """Get total price from the best available source."""
    return _data_source_manager.get_total_price() 