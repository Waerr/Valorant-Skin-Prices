"""
Skin verification system to ensure all Valorant skins are correctly scraped.
"""

import logging
import re
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SkinInfo:
    """Information about a weapon skin."""
    name: str
    weapon: str
    price: int
    edition: str
    source: str
    row_index: int


class SkinVerifier:
    """Verifies that all skins are correctly scraped from the Fandom wiki."""
    
    def __init__(self):
        self.skins_found = []
        self.skin_errors = []
        self.statistics = {}
    
    def verify_skins_from_html(self, html_content: str) -> Dict[str, any]:
        """Verify skins from HTML content and return detailed analysis."""
        try:
            soup = BeautifulSoup(html_content, "lxml")
            return self._analyze_skins_table(soup)
        except Exception as e:
            logger.error(f"Error verifying skins: {e}")
            return {"error": str(e)}
    
    def _analyze_skins_table(self, soup: BeautifulSoup) -> Dict[str, any]:
        """Analyze the skins table for completeness and accuracy."""
        results = {
            "total_skins": 0,
            "total_price": 0,
            "weapon_breakdown": {},
            "edition_breakdown": {},
            "source_breakdown": {},
            "price_ranges": {},
            "missing_data": [],
            "duplicate_skins": [],
            "skin_details": []
        }
        
        try:
            # Find all weapon skins tables
            tables = soup.select("table.wikitable.sortable")
            
            if not tables:
                results["error"] = "No weapon skins tables found"
                return results
            
            logger.info(f"Found {len(tables)} tables with class 'wikitable sortable'")
            
            # Process tables 2 and 3 (index 1 and 2) which contain the weapon skins
            target_tables = []
            if len(tables) > 1:
                target_tables.append(tables[1])  # Table 2
            if len(tables) > 2:
                target_tables.append(tables[2])  # Table 3
            
            if not target_tables:
                results["error"] = "Could not find target tables (2 and 3)"
                return results
            
            # Process each target table
            for table_index, table in enumerate(target_tables):
                logger.info(f"Processing target table {table_index + 1} (index {1 + table_index})")
                table_results = self._process_skins_table(table, table_index)
                
                # Merge results
                results["total_skins"] += table_results["total_skins"]
                results["total_price"] += table_results["total_price"]
                results["skin_details"].extend(table_results["skin_details"])
                
                # Merge breakdowns
                for weapon, count in table_results["weapon_breakdown"].items():
                    results["weapon_breakdown"][weapon] = results["weapon_breakdown"].get(weapon, 0) + count
                
                for edition, count in table_results["edition_breakdown"].items():
                    results["edition_breakdown"][edition] = results["edition_breakdown"].get(edition, 0) + count
                
                for source, count in table_results["source_breakdown"].items():
                    results["source_breakdown"][source] = results["source_breakdown"].get(source, 0) + count
            
            # Analyze for issues
            results.update(self._analyze_data_quality(results["skin_details"]))
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing skins table: {e}")
            results["error"] = str(e)
            return results
    
    def _process_skins_table(self, table, table_index: int) -> Dict[str, any]:
        """Process a single skins table."""
        results = {
            "total_skins": 0,
            "total_price": 0,
            "weapon_breakdown": {},
            "edition_breakdown": {},
            "source_breakdown": {},
            "skin_details": []
        }
        
        rows = table.find_all("tr")[1:]  # Skip header row
        logger.info(f"Processing table {table_index} with {len(rows)} rows")
        
        for row_index, row in enumerate(rows):
            try:
                # First check if this row has a valid price (like the actual scraping does)
                price = self._extract_price_from_row(row)
                if price is None:
                    continue  # Skip rows without valid prices
                
                # Now extract full skin info
                skin_info = self._extract_skin_info(row, row_index, table_index)
                if skin_info:
                    results["total_skins"] += 1
                    results["total_price"] += skin_info.price
                    results["skin_details"].append(skin_info)
                    
                    # Update breakdowns
                    results["weapon_breakdown"][skin_info.weapon] = results["weapon_breakdown"].get(skin_info.weapon, 0) + 1
                    results["edition_breakdown"][skin_info.edition] = results["edition_breakdown"].get(skin_info.edition, 0) + 1
                    results["source_breakdown"][skin_info.source] = results["source_breakdown"].get(skin_info.source, 0) + 1
                    
                    # Debug logging for first few skins
                    if results["total_skins"] <= 5:
                        logger.debug(f"Found skin: {skin_info.name} - {skin_info.weapon} - {skin_info.price} VP")
                    
            except Exception as e:
                logger.warning(f"Error processing row {row_index}: {e}")
                continue
        
        logger.info(f"Extracted {results['total_skins']} skins from table {table_index}")
        return results
    
    def _extract_price_from_row(self, row) -> Optional[int]:
        """Extract price from a table row (matching the actual scraping logic)."""
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
    
    def _extract_skin_info(self, row, row_index: int, table_index: int) -> Optional[SkinInfo]:
        """Extract detailed skin information from a table row."""
        try:
            cells = row.find_all("td")
            if len(cells) < 1:
                return None
            
            # Get the price that was already extracted
            price = self._extract_price_from_row(row)
            if price is None or price <= 0:
                return None
            
            # Extract skin name (usually first column)
            name_cell = cells[0]
            skin_name = name_cell.get_text(strip=True)
            if not skin_name or skin_name == "—" or skin_name == "-":
                skin_name = f"Skin_{row_index}"  # Fallback name
            
            # Extract weapon type (usually second column if available)
            weapon = "Unknown"
            if len(cells) > 1:
                weapon_cell = cells[1]
                weapon_text = weapon_cell.get_text(strip=True)
                if weapon_text and weapon_text not in ["—", "-"]:
                    weapon = weapon_text
            
            # Extract edition (look for edition indicators)
            edition = self._extract_edition(row)
            
            # Extract source (Store, Battle Pass, etc.)
            source = self._extract_source(row)
            
            return SkinInfo(
                name=skin_name,
                weapon=weapon,
                price=price,
                edition=edition,
                source=source,
                row_index=row_index
            )
            
        except Exception as e:
            logger.debug(f"Error extracting skin info from row {row_index}: {e}")
            return None
    
    def _extract_edition(self, row) -> str:
        """Extract the skin edition from the row."""
        row_text = row.get_text().lower()
        
        if "ultra" in row_text:
            return "Ultra"
        elif "exclusive" in row_text:
            return "Exclusive"
        elif "premium" in row_text:
            return "Premium"
        elif "deluxe" in row_text:
            return "Deluxe"
        elif "select" in row_text:
            return "Select"
        else:
            return "Unknown"
    
    def _extract_source(self, row) -> str:
        """Extract the skin source from the row."""
        row_text = row.get_text().lower()
        
        if "battle pass" in row_text or "battlepass" in row_text:
            return "Battle Pass"
        elif "agent gear" in row_text:
            return "Agent Gear"
        elif "store" in row_text or "night market" in row_text:
            return "Store"
        else:
            return "Unknown"
    
    def _analyze_data_quality(self, skin_details: List[SkinInfo]) -> Dict[str, any]:
        """Analyze the quality of scraped data."""
        analysis = {
            "missing_data": [],
            "duplicate_skins": [],
            "price_ranges": {},
            "data_quality_score": 0
        }
        
        # Check for missing data
        for skin in skin_details:
            if not skin.name or skin.name == "Unknown":
                analysis["missing_data"].append(f"Row {skin.row_index}: Missing skin name")
            if not skin.weapon or skin.weapon == "Unknown":
                analysis["missing_data"].append(f"Row {skin.row_index}: Missing weapon type")
            if skin.price <= 0:
                analysis["missing_data"].append(f"Row {skin.row_index}: Invalid price ({skin.price})")
        
        # Check for duplicates
        names = [skin.name for skin in skin_details]
        duplicates = set([name for name in names if names.count(name) > 1])
        if duplicates:
            analysis["duplicate_skins"] = list(duplicates)
        
        # Analyze price ranges
        prices = [skin.price for skin in skin_details]
        if prices:
            analysis["price_ranges"] = {
                "min": min(prices),
                "max": max(prices),
                "average": sum(prices) / len(prices),
                "total": sum(prices)
            }
        
        # Calculate data quality score
        total_skins = len(skin_details)
        if total_skins > 0:
            valid_skins = sum(1 for skin in skin_details 
                            if skin.name and skin.weapon and skin.price > 0)
            analysis["data_quality_score"] = (valid_skins / total_skins) * 100
        
        return analysis
    
    def generate_report(self, analysis: Dict[str, any]) -> str:
        """Generate a comprehensive report of the skin verification."""
        report = []
        report.append("=" * 60)
        report.append("VALORANT SKIN VERIFICATION REPORT")
        report.append("=" * 60)
        
        if "error" in analysis:
            report.append(f"❌ ERROR: {analysis['error']}")
            return "\n".join(report)
        
        # Summary
        report.append(f"📊 SUMMARY:")
        report.append(f"   Total Skins Found: {analysis['total_skins']:,}")
        report.append(f"   Total Price: {analysis['total_price']:,} VP")
        report.append(f"   Data Quality Score: {analysis.get('data_quality_score', 0):.1f}%")
        
        # Weapon breakdown
        if analysis.get('weapon_breakdown'):
            report.append(f"\n🔫 WEAPON BREAKDOWN:")
            for weapon, count in sorted(analysis['weapon_breakdown'].items()):
                report.append(f"   {weapon}: {count:,}")
        
        # Edition breakdown
        if analysis.get('edition_breakdown'):
            report.append(f"\n⭐ EDITION BREAKDOWN:")
            for edition, count in sorted(analysis['edition_breakdown'].items()):
                report.append(f"   {edition}: {count:,}")
        
        # Source breakdown
        if analysis.get('source_breakdown'):
            report.append(f"\n🏪 SOURCE BREAKDOWN:")
            for source, count in sorted(analysis['source_breakdown'].items()):
                report.append(f"   {source}: {count:,}")
        
        # Price analysis
        if analysis.get('price_ranges'):
            price_ranges = analysis['price_ranges']
            report.append(f"\n💰 PRICE ANALYSIS:")
            report.append(f"   Min Price: {price_ranges['min']:,} VP")
            report.append(f"   Max Price: {price_ranges['max']:,} VP")
            report.append(f"   Average Price: {price_ranges['average']:,.0f} VP")
        
        # Issues
        if analysis.get('missing_data'):
            report.append(f"\n⚠️  MISSING DATA ({len(analysis['missing_data'])} issues):")
            for issue in analysis['missing_data'][:10]:  # Show first 10
                report.append(f"   • {issue}")
            if len(analysis['missing_data']) > 10:
                report.append(f"   ... and {len(analysis['missing_data']) - 10} more")
        
        if analysis.get('duplicate_skins'):
            report.append(f"\n🔄 DUPLICATE SKINS ({len(analysis['duplicate_skins'])} found):")
            for duplicate in analysis['duplicate_skins'][:5]:  # Show first 5
                report.append(f"   • {duplicate}")
            if len(analysis['duplicate_skins']) > 5:
                report.append(f"   ... and {len(analysis['duplicate_skins']) - 5} more")
        
        # Expected vs Actual
        expected_total = 496  # Current number of purchasable skins as of 2025-08-02
        actual_total = analysis['total_skins']
        
        # Calculate coverage based on the ratio of found to expected
        if actual_total > 0:
            coverage = (actual_total / expected_total) * 100
        else:
            coverage = 0
        
        report.append(f"\n📈 COVERAGE ANALYSIS:")
        report.append(f"   Expected Total: {expected_total:,} purchasable skins")
        report.append(f"   Actual Found: {actual_total:,} purchasable skins")
        report.append(f"   Coverage: {coverage:.1f}%")
        
        # Coverage thresholds for purchasable skins
        if coverage >= 95:  # If we get at least 95% of expected purchasable skins
            report.append(f"   ✅ Coverage is excellent (found {actual_total:,} purchasable skins)")
        elif coverage >= 80:
            report.append(f"   ✅ Coverage is good (found {actual_total:,} purchasable skins)")
        elif coverage >= 60:
            report.append(f"   ⚠️  Coverage is acceptable (found {actual_total:,} purchasable skins)")
        else:
            report.append(f"   ❌ Coverage is poor - some purchasable skins may be missing")
        
        report.append("=" * 60)
        return "\n".join(report)


# Utility functions
def verify_skins_from_html(html_content: str) -> Dict[str, any]:
    """Verify skins from HTML content."""
    verifier = SkinVerifier()
    return verifier.verify_skins_from_html(html_content)


def generate_verification_report(html_content: str) -> str:
    """Generate a verification report from HTML content."""
    verifier = SkinVerifier()
    analysis = verifier.verify_skins_from_html(html_content)
    return verifier.generate_report(analysis) 