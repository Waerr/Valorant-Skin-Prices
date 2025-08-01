"""
Playwright-based scraper for Valorant skin prices.
This provides more robust scraping capabilities than BeautifulSoup + requests.
"""

import logging
import asyncio
import re
from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """Advanced scraper using Playwright for better reliability."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,  # Run in headless mode
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        self.page = await self.browser.new_page()
        
        # Set viewport and other browser-like properties
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        await self.page.set_extra_http_headers({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def scrape_fandom_wiki(self) -> List[int]:
        """Scrape skin prices from Fandom wiki using Playwright."""
        try:
            url = "https://valorant.fandom.com/wiki/Weapon_Skins"
            logger.info(f"Scraping {url} with Playwright")
            
            # Navigate to the page
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for the content to load
            await self.page.wait_for_selector("table.wikitable.sortable", timeout=10000)
            
            # Get the page content
            content = await self.page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, "lxml")
            return self._extract_prices_from_soup(soup)
            
        except Exception as e:
            logger.error(f"Error scraping Fandom wiki with Playwright: {e}")
            raise
    
    async def scrape_with_screenshots(self, url: str, screenshot_path: str = None) -> List[int]:
        """Scrape with optional screenshot for debugging."""
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Take screenshot if path provided
            if screenshot_path:
                await self.page.screenshot(path=screenshot_path, full_page=True)
                logger.info(f"Screenshot saved to {screenshot_path}")
            
            # Wait for tables to load
            await self.page.wait_for_selector("table.wikitable.sortable", timeout=10000)
            
            content = await self.page.content()
            soup = BeautifulSoup(content, "lxml")
            return self._extract_prices_from_soup(soup)
            
        except Exception as e:
            logger.error(f"Error scraping with screenshots: {e}")
            raise
    
    async def scrape_with_retry(self, url: str, max_retries: int = 3) -> List[int]:
        """Scrape with retry logic for better reliability."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Scraping attempt {attempt + 1}/{max_retries}")
                
                # Clear cookies and cache for fresh start
                await self.page.context.clear_cookies()
                
                # Navigate to page
                await self.page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Wait for content
                await self.page.wait_for_selector("table.wikitable.sortable", timeout=10000)
                
                # Get content
                content = await self.page.content()
                soup = BeautifulSoup(content, "lxml")
                prices = self._extract_prices_from_soup(soup)
                
                if prices and len(prices) > 0:
                    logger.info(f"Successfully scraped {len(prices)} prices on attempt {attempt + 1}")
                    return prices
                else:
                    logger.warning(f"No prices found on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("All scraping attempts failed")
    
    def _extract_prices_from_soup(self, soup: BeautifulSoup) -> List[int]:
        """Extract prices from BeautifulSoup object."""
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
            
            logger.info(f"Extracted {len(prices)} prices from HTML")
            
        except Exception as e:
            logger.error(f"Error extracting prices from HTML: {e}")
            raise
        
        return prices
    
    def _extract_price_from_row(self, row) -> Optional[int]:
        """Extract price from a table row."""
        try:
            # First try to find td element with data-sort-value attribute
            td_element = row.find("td", {"data-sort-value": True})
            if td_element:
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
    
    async def get_page_info(self, url: str) -> Dict[str, Any]:
        """Get detailed information about a page for debugging."""
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Get page title
            title = await self.page.title()
            
            # Get page URL (in case of redirects)
            current_url = self.page.url
            
            # Get page content length
            content = await self.page.content()
            content_length = len(content)
            
            # Check for specific elements
            has_tables = await self.page.query_selector("table.wikitable.sortable") is not None
            table_count = len(await self.page.query_selector_all("table.wikitable.sortable"))
            
            return {
                "title": title,
                "url": current_url,
                "content_length": content_length,
                "has_tables": has_tables,
                "table_count": table_count,
                "user_agent": await self.page.evaluate("() => navigator.userAgent")
            }
            
        except Exception as e:
            logger.error(f"Error getting page info: {e}")
            return {"error": str(e)}


# Async wrapper functions for easy use
async def scrape_fandom_wiki_async() -> List[int]:
    """Async function to scrape Fandom wiki."""
    async with PlaywrightScraper() as scraper:
        return await scraper.scrape_fandom_wiki()


async def scrape_with_retry_async(url: str, max_retries: int = 3) -> List[int]:
    """Async function to scrape with retry logic."""
    async with PlaywrightScraper() as scraper:
        return await scraper.scrape_with_retry(url, max_retries)


def scrape_fandom_wiki_sync() -> List[int]:
    """Synchronous wrapper for scraping Fandom wiki."""
    return asyncio.run(scrape_fandom_wiki_async())


def scrape_with_retry_sync(url: str, max_retries: int = 3) -> List[int]:
    """Synchronous wrapper for scraping with retry."""
    return asyncio.run(scrape_with_retry_async(url, max_retries)) 