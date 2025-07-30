import csv
import os
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import random

# ---- CONFIG ----
YEAR = 2025
CSV_FILE = f"berlin_polizei_{YEAR}.csv"
BASE_URL = "https://www.berlin.de"
START_URL = f"{BASE_URL}/polizei/polizeimeldungen/archiv/{YEAR}/?page_at_1_0="

# ---- Load latest saved date ----
def get_latest_saved_datetime():
    if not os.path.exists(CSV_FILE):
        return None
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            return None
        latest_row = rows[0]  # newest is first if file sorted
        return parse_date(latest_row["date"])

def parse_date(date_str):
    # "13.07.2025 13:31 Uhr"
    return datetime.strptime(date_str.replace(" Uhr", ""), "%d.%m.%Y %H:%M")

# ---- Setup browser ----
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

latest_saved = get_latest_saved_datetime()
print(f"📌 Latest saved report: {latest_saved.strftime('%Y-%m-%d %H:%M') if latest_saved else 'None — full scrape'}")

new_entries = []
page = 1
found_all = False

while not found_all:
    url = START_URL + str(page)
    driver.get(url)
    time.sleep(random.uniform(1.5, 3.0))
    soup = BeautifulSoup(driver.page_source, "html.parser")

    list_items = soup.select("ul.list--tablelist > li")
    if not list_items:
        break

    for li in list_items:
        try:
            date_str = li.select_one(".cell.nowrap.date").get_text(strip=True)
            date_dt = parse_date(date_str)

            if latest_saved and date_dt <= latest_saved:
                found_all = True
                break  # all remaining are already saved

            a_tag = li.select_one(".cell.text a")
            title = a_tag.get_text(strip=True)
            link = BASE_URL + a_tag["href"]
            location = li.select_one(".category").get_text(strip=True).replace("Ereignisort: ", "")

            new_entries.append({
                "date": date_str,
                "title": title,
                "link": link,
                "location": location
            })

        except Exception as e:
            print(f"[Page {page}] Skipped one item due to error: {e}")
            continue

    print(f"🔎 Checked page {page}, found {len(list_items)} entries.")
    page += 1

driver.quit()

# ---- Write new entries (prepend to file) ----
if new_entries:
    print(f"\n🆕 Found {len(new_entries)} new entries. Updating {CSV_FILE}...")

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            existing = f.read()

        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link", "location"])
            writer.writeheader()
            writer.writerows(new_entries)
            f.write(existing.split('\n', 1)[-1])  # skip duplicate header
    else:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["date", "title", "link", "location"])
            writer.writeheader()
            writer.writerows(new_entries)

    print(f"✅ Appended new reports to {CSV_FILE}")
else:
    print("✅ No new reports to add.")
