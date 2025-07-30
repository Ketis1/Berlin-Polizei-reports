from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv
import random
from datetime import datetime

# --- Setup headless browser ---
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# --- Base URL ---
base_url = "https://www.berlin.de"

# --- Loop over years ---
current_year = datetime.now().year
for year in range(2014, current_year + 1):
    print(f"\n Starting year {year}...")
    year_results = []
    page_num = 1

    while True:
        url = f"https://www.berlin.de/polizei/polizeimeldungen/archiv/{year}/?page_at_1_0={page_num}"
        driver.get(url)
        time.sleep(random.uniform(1.5, 3.0))  # polite delay

        soup = BeautifulSoup(driver.page_source, "html.parser")
        list_items = soup.select("ul.list--tablelist > li")

        if not list_items:
            print(f"✅ Finished year {year} with {page_num - 1} pages.")
            break

        for li in list_items:
            try:
                date = li.select_one(".cell.nowrap.date").get_text(strip=True)
                a_tag = li.select_one(".cell.text a")
                title = a_tag.get_text(strip=True)
                link = base_url + a_tag["href"]
                location = li.select_one(".category").get_text(strip=True).replace("Ereignisort: ", "")

                year_results.append({
                    "date": date,
                    "title": title,
                    "link": link,
                    "location": location
                })
            except Exception as e:
                print(f"[{year} - Page {page_num}] Skipped entry due to error: {e}")
                continue

        print(f"Scraped {len(list_items)} entries from year {year}, page {page_num}")
        page_num += 1

    # --- Save year's data ---
    filename = f"berlin_polizei_{year}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "title", "link", "location"])
        writer.writeheader()
        writer.writerows(year_results)

    print(f"📁 Saved {len(year_results)} entries to {filename}")

# --- Cleanup ---
driver.quit()
print("\n All years processed and saved.")
