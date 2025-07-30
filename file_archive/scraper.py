from bs4 import BeautifulSoup

# Load your HTML file
with open("polizei.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

base_url = "https://www.berlin.de"
results = []

# Find all <li> entries in the report list
for li in soup.select("ul.list--tablelist > li"):
    date = li.select_one(".cell.nowrap.date").get_text(strip=True)
    a_tag = li.select_one(".cell.text a")
    title = a_tag.get_text(strip=True)
    link = base_url + a_tag["href"]
    location_span = li.select_one(".category")
    location = location_span.get_text(strip=True).replace("Ereignisort: ", "")

    results.append({
        "date": date,
        "title": title,
        "link": link,
        "location": location
    })

# Example output
for item in results:
    print(item)
