# Valorant Skin Prices

A Python application that fetches and displays Valorant skin prices in various currencies with real-time exchange rates.

## Features

- **Real-time Price Fetching**: Scrapes current Valorant skin prices from the Fandom wiki
- **Multi-Currency Support**: Converts VP prices to USD, EUR, GBP, and other currencies using live exchange rates
- **Caching System**: Implements intelligent caching for both prices and exchange rates to reduce Scraping
- **Robust Web Scraping**: Uses Playwright for reliable browser-based scraping with fallback to requests
- **Comprehensive Verification**: Validates that all purchasable skins (496+) are correctly scraped
- **Modern GUI**: Clean, responsive interface built with Tkinter

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Valorant-Skin-Prices
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup Playwright (recommended):
```bash
python scripts/setup_playwright.py
```

4. Run the application:
```bash
python main.py
```

## Usage

1. Launch the application: `python main.py`
2. Select your preferred currency from the dropdown
3. View the current total price for all Valorant skins
4. Click "Refresh Prices & Rates" to update data

## Data Sources

- **Fandom Wiki (Playwright)**: Primary source with browser-based scraping
- **Fandom Wiki (Requests)**: Fallback using HTTP requests

## Configuration

- `config.py`: Main settings
- `utils/currencyMap.py`: Currency conversion
- `utils/data_sources.py`: Data source management
- `utils/playwright_scraper.py`: Browser-based scraping

## Cache Management

Cache files are stored in `cache/`:
- `skin_prices.json`: Cached skin prices (6 hours)
- `exchange_rates.json`: Cached exchange rates (24 hours)

## Testing

### Run All Tests
```bash
python tests/test_skin_verification.py
python tests/test_conversion.py
```

### Debug Tools
```bash
python scripts/debug_table_structure.py
```

## Troubleshooting

### Common Issues

1. **No prices displayed**: Check internet connection and refresh
2. **Playwright issues**: Run `python scripts/setup_playwright.py`
3. **Cache problems**: Delete the `cache/` directory
4. **Incorrect USD prices**: Clear cache and restart the application

## Project Structure

```
Valorant-Skin-Prices/
├── main.py                 # Main application
├── utils/                  # Core modules
├── tests/                  # Test suite
├── scripts/                # Utility scripts
├── docs/                   # Documentation
└── cache/                  # Cached data
```

## License

MIT License - see LICENSE file for details.
