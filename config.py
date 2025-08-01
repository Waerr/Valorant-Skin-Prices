"""
Configuration settings.
"""

# Window Configuration
WINDOW_CONFIG = {
    "width": 300,
    "height": 170,
    "title": "Valorant Skin Prices",
    "resizable": False
}

# UI Colors
UI_COLORS = {
    "background": "#333333",
    "button": "#555555",
    "active_button": "#666666",
    "text": "#FFFFFF",
    "menu_background": "#444444",
    "menu_active_background": "#555555"
}

# Network Configuration
NETWORK_CONFIG = {
    "timeout": 10,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Application URLs
URLS = {
    "valorant_skins": "https://valorant.fandom.com/wiki/Weapon_Skins"
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
} 