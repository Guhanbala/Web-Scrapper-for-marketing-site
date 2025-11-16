# utils/scraper_utils.py
from crawl4ai import BrowserConfig

def get_browser_config():
    return BrowserConfig(
        headless=False,
        verbose=False
    )