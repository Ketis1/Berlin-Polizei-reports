import os
import csv

from deep_translator import MyMemoryTranslator

# === CONFIG ===
DATA_FOLDER = "berlin_reports_yearly"  # folder where CSV files are stored
YEARS = list(range(2014, 2026))  # adjust as needed
COLUMN_NAMES = ["date", "title", "link", "location", "description", "en_title"]

# === Translator Setup ===
translator = MyMemoryTranslator(source='de-DE', target='en-GB')
# translated = translator.translate("Guten Tag")
# print(translated)
def translate_title(title):
    try:
        return translator.translate(title)
    except Exception as e:
        print(f"❌ Error translating title '{title}': {e}")
        return ""

total_chars = 0

# === Process all CSVs ===
for year in YEARS:
    filename = os.path.join(DATA_FOLDER, f"berlin_polizei_{year}.csv")
    if not os.path.exists(filename):
        print(f"⏭️ Skipping missing file: {filename}")
        continue

    print(f"\n📂 Processing {filename}...")

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Ensure 'description' and 'en_title' exist
    for row in rows:
        if 'description' not in row:
            row['description'] = ""
        if 'en_title' not in row:
            row['en_title'] = ""

    updated = False
    tooManyRequests = False
    for i, row in enumerate(rows):
        title = row.get("title", "").strip()
        if title and not row.get("en_title", "").strip():
            print(f"[{year}] Translating ({i+1}/{len(rows)}): {title}")

            try:
                row["en_title"] = translator.translate(title)
            except Exception as e:
                print(f"❌ Error translating title '{title}': {e}")
                if e.__class__.__name__ == "TooManyRequests":
                    tooManyRequests = True
                    break

            total_chars += len(title)
            updated = True
        else:
            print(f"[{year}] Skipping ({i+1}/{len(rows)}): already has en_title")

    if updated:
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMN_NAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Updated {filename} with new translations.")
    else:
        print(f"📎 No new changes have been made to {filename}.")

    if tooManyRequests:
        print("🔒 You made too many requests to the server.According to google, you are allowed to make 5 requests per secondand up to 200k requests per day. You can wait and try again later oryou can try the translate_batch function")
        exit(0)
print(f"🔤 Total characters translated: {total_chars}")