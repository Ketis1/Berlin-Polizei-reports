import pandas as pd
from transformers import pipeline
from tqdm import tqdm
import torch

print("CUDA AVAIBLE", torch.cuda.is_available())  # Should print True if u want to use GPU


# Verify GPU
device = 0 if torch.cuda.is_available() else -1
print(f"Device set to: {'GPU' if device == 0 else 'CPU'}")

# Load the dataset
input_file = "../berlin_reports_yearly/berlin_polizei_2020.csv"
df = pd.read_csv(input_file)

# Fill missing text fields
df["title"] = df["title"].fillna("")
df["description"] = df["description"].fillna("")

# Combine title + description
df["full_text"] = df["title"].str.strip() + ". " + df["description"].str.strip()

# German labels (candidate classes)
candidate_labels = [
    "Diebstahl",             # theft
    "Raub",                  # robbery
    "Körperverletzung",      # assault
    "Drogenverstoß",         # drug offense
    "Brandstiftung",         # arson
    "Sachbeschädigung",      # vandalism
    "Betrug",                # fraud
    "Verkehrsunfall",        # traffic accident
    "Häusliche Gewalt",      # domestic violence
    "Verdächtiges Verhalten",# suspicious activity
    "Vermisstenmeldung",     # missing person
    "Ruhestörung",           # public disturbance
    "Waffenbesitz",          # weapon possession
    "Illegale Einwanderung", # illegal immigration
    "Tötungsdelikt"          # homicide
]

# Load multilingual zero-shot classification model
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",device = device)

# Prepare results
predicted_labels = []
confidences = []

# Classify each report
for text in tqdm(df["full_text"], desc="Classifying"):
    if not text.strip():
        predicted_labels.append("")
        confidences.append(0.0)
        continue

    result = classifier(
        text,
        candidate_labels=candidate_labels,
        hypothesis_template="Dieser Vorfall betrifft {}." # German hypothesis template
    )

    predicted_labels.append(result["labels"][0])
    confidences.append(result["scores"][0])

# Add predictions to the dataframe
df["predicted_label"] = predicted_labels
df["label_confidence"] = confidences

# Save to new file
output_file = "berlin_polizei_2020_labeled.csv"
df.to_csv(output_file, index=False)

print(f"\n✅ Done! Labeled file saved to: {output_file}")
