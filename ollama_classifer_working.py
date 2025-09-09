import os
import pandas as pd
from ollama_classifier import OllamaPoliceClassifier  # classifier module
from tqdm import tqdm
import time

# Folder containing yearly CSVs
DATA_FOLDER = "berlin_reports_yearly"
OUTPUT_FOLDER = "berlin_reports_yearly_classified"

# Make sure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize classifier
classifier = OllamaPoliceClassifier(model_name="llama3.1:8b")


def needs_classification(value):
    """Check if a category value is missing or empty"""
    # Handle NaN/None
    if pd.isna(value):
        return True

    # Convert to string and clean
    str_val = str(value).strip()

    # Check for completely empty values
    if str_val in ['', 'nan', 'None', 'null', 'NA']:
        return True

    # Define your exact valid categories (from your OllamaPoliceClassifier)
    valid_categories = [
        'Gewaltverbrechen',
        'Eigentumsdelikte',
        'Verkehrsdelikte',
        'Betäubungsmittel',
        'Brandstiftung',
        'Öffentliche Ordnung',
        'Sonstiges'
    ]

    # If it matches one of your valid categories, don't reclassify
    if str_val in valid_categories:
        return False

    # For debugging - show what existing categories we found
    if str_val != '':
        print(f"Found existing category: '{str_val}' - preserving it")
        return False  # Preserve any existing non-empty category

    return True  # Only classify if truly empty


# Iterate over years starting from 2014
for year in range(2014, 2026):  # adjust end year if needed
    input_file = os.path.join(DATA_FOLDER, f"berlin_polizei_{year}.csv")
    output_file = os.path.join(OUTPUT_FOLDER, f"berlin_polizei_{year}_classified.csv")

    if not os.path.exists(input_file):
        print(f"⚠️ File not found: {input_file}, skipping...")
        continue

    print(f"\n📂 Processing {year}...")

    # Load CSV - try output file first if it exists
    df = None
    if os.path.exists(output_file):
        try:
            df = pd.read_csv(output_file)
            print(f"📂 Loaded existing output file")
        except:
            pass

    if df is None:
        try:
            df = pd.read_csv(input_file)
            print(f"📂 Loaded original input file")
        except Exception as e:
            print(f"❌ Error loading {input_file}: {e}")
            continue

    # Ensure required columns exist
    if "title" not in df.columns or "description" not in df.columns:
        print(f"⚠️ Required columns 'title' or 'description' not found in {input_file}")
        continue

    # Add kategorie column if it doesn't exist
    if "kategorie" not in df.columns:
        df["kategorie"] = None
        print(f"📝 Added 'kategorie' column")

    # Find rows that need classification
    mask = df['kategorie'].apply(needs_classification)
    rows_to_classify = mask.sum()
    total_rows = len(df)
    already_classified = total_rows - rows_to_classify

    print(f"📊 Total rows: {total_rows}")
    print(f"✅ Already classified: {already_classified}")
    print(f"🔄 Need classification: {rows_to_classify}")

    if rows_to_classify == 0:
        print(f"✨ All rows already classified for {year}, copying file...")
        df.to_csv(output_file, index=False)
        continue

    # Classify ONLY the rows that need it
    classified_count = 0

    # Create progress bar for only the rows that need classification
    pbar = tqdm(total=rows_to_classify, desc=f"Classifying {year}", unit="row")

    for idx in df.index:
        if mask[idx]:  # Only process rows that need classification
            try:
                title = str(df.at[idx, "title"])
                description = str(df.at[idx, "description"])

                # Classify the event
                category = classifier.classify_event(title, description)
                df.at[idx, "kategorie"] = category

                classified_count += 1
                pbar.update(1)

                # Add small delay to prevent overwhelming the model
                time.sleep(0.1)

            except Exception as e:
                print(f"\n❌ Error classifying row {idx}: {e}")
                df.at[idx, "kategorie"] = "Sonstiges"  # fallback
                pbar.update(1)

    pbar.close()

    # Verify results
    final_mask = df['kategorie'].apply(needs_classification)
    remaining_unclassified = final_mask.sum()

    if remaining_unclassified > 0:
        print(f"⚠️ Warning: {remaining_unclassified} rows still unclassified")

    # Save output
    try:
        df.to_csv(output_file, index=False)
        print(f"✅ Saved classified file: {output_file}")
        print(f"📈 Classified {classified_count} new rows")

        # Show category distribution for newly classified rows
        if classified_count > 0:
            new_categories = df[mask]['kategorie'].value_counts()
            print(f"📊 New classifications:")
            for cat, count in new_categories.head().items():
                print(f"   {cat}: {count}")

    except Exception as e:
        print(f"❌ Error saving {output_file}: {e}")

print(f"\n🎉 Batch classification complete!")


# Optional: Summary statistics
def print_summary():
    """Print summary of all processed files"""
    print(f"\n📋 SUMMARY:")
    print("=" * 50)

    total_files = 0
    total_rows = 0

    for year in range(2014, 2026):
        output_file = os.path.join(OUTPUT_FOLDER, f"berlin_polizei_{year}_classified.csv")
        if os.path.exists(output_file):
            df = pd.read_csv(output_file)
            total_files += 1
            total_rows += len(df)

            # Check completion
            unclassified = df['kategorie'].apply(needs_classification).sum()
            completion = ((len(df) - unclassified) / len(df)) * 100

            print(f"{year}: {len(df):>5} rows ({completion:>5.1f}% classified)")

    print("=" * 50)
    print(f"Total: {total_files} files, {total_rows:,} rows processed")

# Uncomment to see summary
# print_summary()