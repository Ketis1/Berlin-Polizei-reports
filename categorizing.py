import os
import csv
from transformers import pipeline, AutoTokenizer
from transformers import XLMRobertaTokenizer

# === CONFIG ===
DATA_FOLDER = "berlin_reports_yearly"
YEARS = list(range(2014, 2016))
COLUMN_NAMES = ["date", "title", "link", "location", "description", "en_title", "category"]
print(1)
# === Zero-shot classifier setup ===
# tokenizer = AutoTokenizer.from_pretrained("joeddav/xlm-roberta-large-xnli", use_fast=False)
# classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli", tokenizer=tokenizer)


tokenizer = XLMRobertaTokenizer.from_pretrained("joeddav/xlm-roberta-large-xnli")
classifier = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli", tokenizer=tokenizer)

result = classifier("Deutscher Polizeibericht", candidate_labels=["Theft", "Assault", "Accident"])
print(result)

# Category labels (in English)
CATEGORIES = [
    "Theft",
    "Violence",
    "Traffic Incident",
    "Drugs",
    "Weapons",
    "Fraud",
    "Fire/Explosion",
    "Sexual Offense",
    "Protest/Demonstration",
    "Vandalism",
    "Other"
]
print(2)
def categorize_bert(description):
    if not description.strip():
        return "Other"
    try:
        result = classifier(description, CATEGORIES, multi_label=False)
        return result["labels"][0]
    except Exception as e:
        print(f"❌ Error categorizing description: {e}")
        return "Other"
print(3)
print(categorize_bert("Ein Mann wurde beim Diebstahl eines Fahrrads erwischt."))
print(4)
# === Process CSV files ===
for year in YEARS:
    filename = os.path.join(DATA_FOLDER, f"berlin_polizei_{year}.csv")
    if not os.path.exists(filename):
        print(f"⏭️ Skipping missing file: {filename}")
        continue

    print(f"\n📂 Processing {filename}...")

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Ensure all columns exist
    for row in rows:
        row.setdefault("description", "")
        row.setdefault("en_title", "")
        row.setdefault("category", "")

    updated = False

    for i, row in enumerate(rows):
        desc = row.get("description", "").strip()
        if desc and not row.get("category"):
            print(f"[{year}] Classifying ({i+1}/{len(rows)}): {desc[:60]}...")
            category = categorize_bert(desc)
            row["category"] = category
            updated = True
        else:
            print(f"[{year}] Skipping ({i+1}/{len(rows)}): already has category")

    if updated:
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMN_NAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Updated {filename} with new categories.")
    else:
        print(f"📎 No changes needed for {filename}.")
