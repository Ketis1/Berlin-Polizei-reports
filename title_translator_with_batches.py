# 350 rows translated

import os
import csv
import time
from deep_translator import MyMemoryTranslator

# === CONFIG ===
DATA_FOLDER = "berlin_reports_yearly"
YEARS = list(range(2014, 2026))
COLUMN_NAMES = ["date", "title", "link", "location", "description", "en_title"]
BATCH_SIZE = 50  # Max safe batch size (MyMemory may reject very large batches)
WAIT_TIME = 2  # Seconds to wait between batches to avoid rate-limiting

# === Translator Setup ===
translator = MyMemoryTranslator(source='de-DE', target='en-GB')

def translate_titles_batch(titles):
    try:
        return translator.translate_batch(titles)
    except Exception as e:
        print(f"❌ Error in batch translation: {e}")
        raise e

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

    # Ensure required columns exist
    for row in rows:
        row.setdefault("description", "")
        row.setdefault("en_title", "")

    untranslated_rows = []
    untranslated_titles = []

    for i, row in enumerate(rows):
        title = row.get("title", "").strip()
        en_title = row.get("en_title", "").strip()

        if title and not en_title:
            untranslated_rows.append((i, row))
            untranslated_titles.append(title)
        else:
            print(f"[{year}] Skipping ({i+1}/{len(rows)}): already has en_title")

    if untranslated_titles:
        updated = True
        print(f"🌐 Translating {len(untranslated_titles)} titles in batches of {BATCH_SIZE}...")

        for i in range(0, len(untranslated_titles), BATCH_SIZE):
            chunk = untranslated_titles[i:i + BATCH_SIZE]
            chunk_rows = untranslated_rows[i:i + BATCH_SIZE]

            try:
                translations = translate_titles_batch(chunk)
                for (row_idx, row), translation in zip(chunk_rows, translations):
                    print(f"[{year}] ✅ ({row_idx+1}) {row['title']} -> {translation}")
                    row["en_title"] = translation

                time.sleep(WAIT_TIME)  # wait between batches
            except Exception as e:
                print("🔒 Stopping due to error:", e)
                if e.__class__.__name__ == "TooManyRequests":
                    print("⚠️ Too many requests. Try again later.")
                break
    else:
        updated = False

    # Write back changes
    if updated:
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMN_NAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Updated {filename} with new translations.")
    else:
        print(f"📎 No new changes have been made to {filename}.")
