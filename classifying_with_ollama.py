import os
import pandas as pd
from ollama_classifier import OllamaPoliceClassifier  #classifier module
from tqdm import tqdm

# Folder containing yearly CSVs
DATA_FOLDER = "berlin_reports_yearly"
OUTPUT_FOLDER = "berlin_reports_yearly_classified"

# Make sure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize classifier
classifier = OllamaPoliceClassifier(model_name="llama3.1:8b")

# Iterate over years starting from 2014
for year in range(2014, 2026):  # adjust end year if needed
    input_file = os.path.join(DATA_FOLDER, f"berlin_polizei_{year}.csv")
    output_file = os.path.join(OUTPUT_FOLDER, f"berlin_polizei_{year}_classified.csv")

    if not os.path.exists(input_file):
        print(f"⚠️ File not found: {input_file}, skipping...")
        continue

    # Load CSV
    df = pd.read_csv(input_file)

    # Ensure required columns exist
    if "title" not in df.columns or "description" not in df.columns:
        print(f"⚠️ Columns 'title' or 'description' not found in {input_file}, skipping...")
        continue

    # If 'kategorie' exists, only classify rows where it is empty/NaN
    if "kategorie" in df.columns:
        mask = df['kategorie'].isna() | (df['kategorie'].astype(str).str.strip() == '')
        print(f"{year}: {mask.sum()} rows need classification")
    else:
        mask = pd.Series([True] * len(df))
        df["kategorie"] = None
        print(f"{year}: {len(df)} rows to classify")

    # Classify rows with progress bar
    for idx in tqdm(df[mask].index, desc=f"Classifying {year}", unit="row"):
        title = df.at[idx, "title"]
        description = df.at[idx, "description"]
        df.at[idx, "kategorie"] = classifier.classify_event(title, description)

    # Save output
    df.to_csv(output_file, index=False)
    print(f"✅ Saved classified file: {output_file}")
