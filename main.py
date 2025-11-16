# main.py
import asyncio
import json
from crawl4ai import AsyncWebCrawler
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from config import BASE_URL
from utils.scraper_utils import get_browser_config

VISITED = set()
CONTENT_PATHS = {'computers', 'phones'}   # only these two have products

async def is_content_page(url):
    path = urlparse(url).path.lower()
    return any(x in path for x in CONTENT_PATHS) and len(path.split('/')) >= 3

async def get_links(crawler, url, selector):
    if url in VISITED:
        return []
    VISITED.add(url)

    result = await crawler.arun(url=url, css_selector=selector, cache_mode="bypass")
    if not result.success:
        return []

    soup = BeautifulSoup(result.html, 'html.parser')
    links = []
    for a in soup.select(selector):
        href = a.get('href')
        if href:
            full_url = urljoin(url, href)
            if (full_url.startswith(BASE_URL)
                and full_url not in VISITED
                and await is_content_page(full_url)):
                title = a.get_text(strip=True)
                if title:
                    links.append((title, full_url))
    return links

async def scrape_page(crawler, title, url):
    if url in VISITED:
        return None
    VISITED.add(url)
    print(f"  Scraping: {title}")

    result = await crawler.arun(url=url, css_selector="body", cache_mode="bypass", wait_for="p, h1")
    if not result.success:
        return None

    soup = BeautifulSoup(result.html, 'html.parser')
    h1 = soup.find('h1')
    page_title = h1.get_text(strip=True) if h1 else title

    desc_tag = soup.find('p', class_='description')
    description = desc_tag.get_text(strip=True) if desc_tag else ""

    price_tag = soup.find('h4', class_='pull-right price')
    price = price_tag.get_text(strip=True) if price_tag else "N/A"

    if len(description) < 50:
        paragraphs = soup.find_all('p')
        description = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

    if len(description) < 100:
        return None

    return {
        "title": page_title,
        "url": url,
        "description": description,
        "price": price
    }

async def main():
    global VISITED
    VISITED.clear()
    print("Starting Web Scraper...")

    async with AsyncWebCrawler(config=get_browser_config()) as crawler:
        # ---- 1. Get homepage ----
        home_result = await crawler.arun(url=BASE_URL, css_selector="body", cache_mode="bypass")
        if not home_result.success:
            print("Failed to load homepage")
            return

        # ---- 2. Find CATEGORY links (updated selectors) ----
        category_links = []
        selectors = [
            "ul#side-menu > li > a",           # <li><a href="/test-sites/e-commerce/static/computers">Computers</a></li>
            "a[href*='/computers']",
            "a[href*='/phones']"
        ]
        for sel in selectors:
            links = await get_links(crawler, BASE_URL, sel)
            category_links.extend(links)
            if links:
                break

        # dedupe
        seen = set()
        category_links = [x for x in category_links if x[1] not in seen and not seen.add(x[1])]

        print(f"Found {len(category_links)} categories")

        # ---- 3. Crawl each category → product pages ----
        all_pages = []
        for cat_title, cat_url in category_links:
            print(f"\nCategory: {cat_title}")
            # product thumbnails on category page
            sub_links = await get_links(crawler, cat_url, ".caption a.title")

            for sub_title, sub_url in sub_links:
                page_data = await scrape_page(crawler, sub_title, sub_url)
                if page_data:
                    all_pages.append(page_data)
                    print(f"    Success: {page_data['title']} → {page_data['price']}")

            await asyncio.sleep(1)   # be polite

        # ---- 4. Save ----
        final_data = {
            "site": "WebScraper.io Test Site",
            "address": "Demo Address",
            "total_pages": len(all_pages),
            "pages": all_pages
        }
        with open("demo_content.json", "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
        print(f"\nSUCCESS: Saved {len(all_pages)} pages to 'demo_content.json'")

if __name__ == "__main__":
    asyncio.run(main())