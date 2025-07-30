import requests
from bs4 import BeautifulSoup

base_url = "https://www.berlin.de"
list_url = "https://www.berlin.de/polizei/polizeimeldungen/archiv/2025/?page_at_1_0={page}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def scrape_page(page=1):
    url = list_url.format(page=page)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = soup.select("li")
    results = []

    for article in articles:
        date_tag = article.select_one("div.cell.nowrap.date")
        date_time = date_tag.get_text(strip=True) if date_tag else ""

        link_tag = article.select_one("div.cell.text a")
        title = link_tag.get_text(strip=True) if link_tag else ""
        link = base_url + link_tag["href"] if link_tag else ""

        location_tag = article.select_one("span.category")
        location = location_tag.get_text(strip=True) if location_tag else ""

        results.append({
            "date_time": date_time,
            "location": location,
            "title": title,
            "link": link
        })

    return results

# Scrapowanie przykładowych stron
all_data = []
for i in range(1, 4):
    print(f"Scraping page {i}...")
    all_data.extend(scrape_page(i))

if all_data:
    print(all_data[0])
else:
    print("Brak danych — możliwa zmiana struktury strony.")
