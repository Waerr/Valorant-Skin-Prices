import logging
from typing import Optional
from tkinter import Tk, Frame, Label, Button, StringVar, OptionMenu, BOTH, TOP, BOTTOM
from utils.currencyMap import CURRENCY_MAP, calculate_currency_amount, get_currency_converter
from utils.getSkins import getPrice, SkinPriceFetcher

from config import WINDOW_CONFIG, UI_COLORS, LOGGING_CONFIG

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"]
)
logger = logging.getLogger(__name__)


class SkinPriceCalculator:
    """Enhanced skin price calculator with improved fetching and conversion."""
    
    def __init__(self):
        self.amount = 0
        self.price_fetcher = SkinPriceFetcher()
        self.currency_converter = get_currency_converter()
        self._load_prices()
    
    def _load_prices(self) -> None:
        """Load current skin prices from the API with improved error handling."""
        try:
            self.amount = self.price_fetcher.get_price()
            logger.info(f"Successfully loaded skin prices: {self.amount} VP")
        except Exception as e:
            self.amount = 0
            logger.error(f"Error getting skin price: {e}")
    
    def calculate_currency_amount(self, currency_key: str) -> str:
        """Calculate and format currency amount for a given currency."""
        try:
            return self.currency_converter.convert_vp_to_currency(self.amount, currency_key)
        except Exception as e:
            logger.error(f"Error calculating currency amount: {e}")
            return "Error calculating amount"
    
    def refresh_prices(self) -> None:
        """Refresh skin prices from the API with cache clearing."""
        try:
            self.price_fetcher.refresh_cache()
            self.currency_converter.refresh_rates()
            
            self._load_prices()
            logger.info("Prices and exchange rates refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing prices: {e}")
            raise


class Window(Frame):
    """
    Main application window for displaying Valorant skin prices.
    
    Displays current skin prices in various currencies with a dropdown
    to switch between different currency options.
    """
    
    def __init__(self, master: Optional[Tk] = None):
        """Initialize the window with improved structure and error handling."""
        super().__init__(master, bg=UI_COLORS["background"])
        self.master = master
        self.pack(fill=BOTH, expand=1)
        
        # Initialize price calculator
        self.calculator = SkinPriceCalculator()
        
        # Create UI components
        self._create_currency_menu()
        self._create_price_label()
        self._create_buttons()
        self._pack_components()
    
    def _create_currency_menu(self) -> None:
        """Create the currency selection dropdown menu."""
        self.menu = StringVar()
        self.menu.set("United States Dollar ($)")
        self.menu.trace_add("write", self._update_label)
        
        options = list(CURRENCY_MAP.keys())
        self.currency_menu = OptionMenu(
            self, 
            self.menu, 
            *options
        )
        self.currency_menu.config(
            width=25, 
            bg=UI_COLORS["menu_background"], 
            fg=UI_COLORS["text"], 
            activebackground=UI_COLORS["menu_active_background"], 
            activeforeground=UI_COLORS["text"], 
            highlightthickness=0
        )
        self.currency_menu["menu"].config(bg=UI_COLORS["menu_background"], fg=UI_COLORS["text"])
    
    def _create_price_label(self) -> None:
        """Create the label displaying the currency amount."""
        self.text = Label(
            self, 
            text=f"Current Amount for Skins: {self.calculator.calculate_currency_amount(self.menu.get())}", 
            font=("Arial", 12), 
            bg=UI_COLORS["background"], 
            fg=UI_COLORS["text"]
        )
    
    def _create_buttons(self) -> None:
        """Create the action buttons."""
        self.refresh_button = Button(
            self, 
            text="Refresh Prices & Rates", 
            command=self._refresh_prices,
            bg=UI_COLORS["button"], 
            fg=UI_COLORS["text"], 
            activebackground=UI_COLORS["active_button"], 
            activeforeground=UI_COLORS["text"], 
            highlightthickness=0
        )
        
        self.quit_button = Button(
            self, 
            text="Quit", 
            command=self.master.destroy,
            bg=UI_COLORS["button"], 
            fg=UI_COLORS["text"], 
            activebackground=UI_COLORS["active_button"], 
            activeforeground=UI_COLORS["text"], 
            highlightthickness=0
        )
    
    def _pack_components(self) -> None:
        """Pack all UI components onto the screen."""
        self.text.pack(side=TOP, pady=10)
        self.currency_menu.pack(side=TOP, pady=10)
        self.refresh_button.pack(side=TOP, pady=5)
        self.quit_button.pack(side=TOP, pady=5)
    
    def _update_label(self, *args: str) -> None:
        """Update the label when a new currency is selected."""
        self.text.config(
            text=f"Current Amount for Skins: {self.calculator.calculate_currency_amount(self.menu.get())}"
        )
    
    def _refresh_prices(self) -> None:
        """Refresh skin prices and exchange rates with loading indicator."""
        self.text.config(text="Loading prices and exchange rates...")
        self.master.update()
        
        try:
            self.calculator.refresh_prices()
            self._update_label()
            logger.info("Prices and rates refreshed successfully")
        except Exception as e:
            self.text.config(text=f"Error refreshing data: {e}")
            logger.error(f"Error refreshing data: {e}")
    
    def show_error_message(self, message: str) -> None:
        """Display error message to the user."""
        self.text.config(text=f"Error: {message}")
        logger.error(message)


def main() -> None:
    """Main application entry point."""
    root = Tk()
    root.configure(bg=UI_COLORS["background"])
    
    app = Window(root)
    root.wm_title(WINDOW_CONFIG["title"])
    root.geometry(f"{WINDOW_CONFIG['width']}x{WINDOW_CONFIG['height']}")
    root.resizable(WINDOW_CONFIG["resizable"], WINDOW_CONFIG["resizable"])
    
    root.mainloop()


if __name__ == "__main__":
    main()
