# Simple Web Scraper

A small, clean Python script that collects product information from a public test website.

---

## What It Does

- Visits: [https://webscraper.io/test-sites/e-commerce/static](https://webscraper.io/test-sites/e-commerce/static)  
- Finds product categories (Computers, Phones)  
- Extracts: **title**, **description**, **price**, and **URL**  
- Saves everything to `demo_content.json`

---

## Why Use It?

- Learn how web scraping works  
- Get structured data without manual copy-paste  
- Use as a starting point for your own projects  

---

## How to Use

```bash
# 1. Clone the project
git clone https://github.com/YOUR_USERNAME/web-scraper-demo.git
cd web-scraper-demo

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install browser
playwright install

# 4. Run
python main.py
