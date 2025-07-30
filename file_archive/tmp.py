import os
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random

# === CONFIG ===
DATA_FOLDER = "."  # folder where CSV files are stored
YEARS = list(range(2014, 2019))  # adjust as needed
COLUMN_NAMES = ["date", "title", "link", "location", "description"]

# === Setup headless Selenium ===
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

def scrape_description(url):
    try:
        driver.get(url)
        time.sleep(random.uniform(1.5, 2.5))
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all <div class="textile"> blocks
        textile_divs = soup.select("div.textile")

        for div in textile_divs:
            parent_classes = div.find_parent().get("class", [])
            if "text" in parent_classes and "emergency-box" not in parent_classes:
                text = div.get_text(separator="\n", strip=True)

                # Optional: skip if it's still the known generic content
                if "Durchsuchungsbeschlüsse bei drei Polizeibeamten" in text:
                    return "[warning_placeholder]"

                return text

        return ""
    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return ""







print(scrape_description("https://www.berlin.de/polizei/polizeimeldungen/2025/pressemitteilung.1572449.php"))
print(scrape_description("https://www.berlin.de/polizei/polizeimeldungen/2025/pressemitteilung.1572439.php"))


driver.quit()