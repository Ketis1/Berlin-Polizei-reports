import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from datasets import Dataset
import numpy as np
from sklearn.metrics import accuracy_score

print("init")

# Load data
df = pd.read_csv("berlin_reports_yearly/berlin_polizei_2020.csv")
df = df.dropna(subset=["title"]).copy()

# Unsupervised clustering to simulate categories
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(df["title"])
kmeans = KMeans(n_clusters=10, random_state=42)
df["category"] = kmeans.fit_predict(X)

# German category names
category_names = {
    0: "Körperverletzung",
    1: "Diebstahl",
    2: "Verkehrsunfall",
    3: "Brandstiftung",
    4: "Betrug",
    5: "Drogenvergehen",
    6: "Raub",
    7: "Sachbeschädigung",
    8: "Festnahme",
    9: "Bedrohung"
}
df["category"] = df["category"].map(category_names)

# Encode labels
print("encoding labels...")
le = LabelEncoder()
df["label"] = le.fit_transform(df["category"])

# Split
print("split")
train_texts, val_texts, train_labels, val_labels = train_test_split(
    df["title"].tolist(), df["label"].tolist(), test_size=0.2, random_state=42
)

# Tokenization
print("tokenizing texts...")
tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=128)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=128)

# Dataset class
class PolizeiDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item
    def __len__(self):
        return len(self.labels)

train_dataset = PolizeiDataset(train_encodings, train_labels)
val_dataset = PolizeiDataset(val_encodings, val_labels)

# Model
model = AutoModelForSequenceClassification.from_pretrained("xlm-roberta-base", num_labels=len(le.classes_))

# Training setup
training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs"
)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    return {"accuracy": accuracy_score(labels, preds)}

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
    tokenizer=tokenizer
)
print("train")
trainer.train()

# Predict
print("predict")
all_encodings = tokenizer(df["title"].tolist(), truncation=True, padding=True, max_length=128, return_tensors="pt")
with torch.no_grad():
    outputs = model(**all_encodings)
    preds = torch.argmax(outputs.logits, dim=1).numpy()

df["predicted_category"] = le.inverse_transform(preds)
df[["title", "predicted_category"]].to_csv("berlin_polizei_classified.csv", index=False)
