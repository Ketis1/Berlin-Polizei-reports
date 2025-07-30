from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv

# Headless browser setup
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Setup
base_url = "https://www.berlin.de"
start_url = "https://www.berlin.de/polizei/polizeimeldungen/archiv/2025/?page_at_1_0="
results = []

page_num = 1
while True:
    url = start_url + str(page_num)
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    list_items = soup.select("ul.list--tablelist > li")

    # Stop if no more entries found
    if not list_items:
        break

    for li in list_items:
        try:
            date = li.select_one(".cell.nowrap.date").get_text(strip=True)
            a_tag = li.select_one(".cell.text a")
            title = a_tag.get_text(strip=True)
            link = base_url + a_tag["href"]
            location = li.select_one(".category").get_text(strip=True).replace("Ereignisort: ", "")

            results.append({
                "date": date,
                "title": title,
                "link": link,
                "location": location
            })
        except Exception as e:
            print(f"[Page {page_num}] Skipped an entry due to error: {e}")
            print(f"Problematic HTML:\n{li.prettify()}")
            continue

    print(f"Scraped page {page_num} with {len(list_items)} entries.")
    page_num += 1

driver.quit()

# Save to CSV
with open("berlin_polizei_2025_full.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "title", "link", "location"])
    writer.writeheader()
    writer.writerows(results)

print(f"Total entries scraped: {len(results)}")
