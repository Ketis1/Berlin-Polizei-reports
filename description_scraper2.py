import os
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIG ===
DATA_FOLDER = "berlin_reports_yearly"  # folder where CSV files are stored
YEARS = list(range(2014, 2026))  # adjust as needed
COLUMN_NAMES = ["date", "title", "link", "location", "description", "en_title"]

# === Setup headless Selenium ===
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

def scrape_description(url):
    try:
        # driver.get(url)
        # time.sleep(random.uniform(1.5, 2.5))
        # soup = BeautifulSoup(driver.page_source, "html.parser")
        #
        # # Find all <div class="textile"> blocks
        # textile_divs = soup.select("div.textile")

        driver.get(url)

        # Waiting for div.textile
        start_wait = time.time()
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.textile"))
            )
            wait_time = time.time() - start_wait
            print(f"⏱️ Waited {wait_time:.2f} seconds for div.textile")
        except:
            wait_time = time.time() - start_wait
            print(f"⚠️ Timeout after {wait_time:.2f} seconds waiting for div.textile")

        soup = BeautifulSoup(driver.page_source, "html.parser")
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

# === Process all CSVs ===
for year in YEARS:
    filename = os.path.join(DATA_FOLDER, f"berlin_polizei_{year}.csv")
    if not os.path.exists(filename):
        print(f"⏭️ Skipping missing file: {filename}")
        continue

    print(f"\n📂 Processing {filename}...")

    # Read existing data
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Ensure 'description' column exists
    if 'description' not in reader.fieldnames:
        for row in rows:
            row['description'] = ""
    else:
        for row in rows:
            if 'description' not in row:
                row['description'] = ""

    # Scrape only missing descriptions
    updated = False
    for i, row in enumerate(rows):
        if not row["description"].strip():
            print(f"[{year}] Scraping ({i+1}/{len(rows)}): {row['title']}")
            row["description"] = scrape_description(row["link"])
            updated = True
        else:
            print(f"[{year}] Skipping ({i+1}/{len(rows)}): already has description")

    if updated:
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMN_NAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Updated {filename} with new descriptions.")
    else:
        print(f"✅ No missing descriptions in {filename}.")

driver.quit()
print("\n🎉 All CSVs processed.")
