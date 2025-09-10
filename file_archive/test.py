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

classifier = pipeline(
    "zero-shot-classification",
    model="joeddav/xlm-roberta-large-xnli",
    tokenizer=tokenizer
)


# examples = [
#     "Deutscher Polizeibericht über einen Diebstahl in Berlin.",
#     "Ein bewaffneter Überfall wurde gestern in der Innenstadt gemeldet.",
#     "Am Sonntag gab es einen Verkehrsunfall mit mehreren Verletzten.",
#     "Ein Fahrrad wurde aus dem Hinterhof gestohlen.",
#     "Die Polizei sucht Zeugen eines Einbruchdiebstahls in Kreuzberg.",
#     "Person wurde wegen Körperverletzung verhaftet.",
#     "Brand in einer Wohnung verursacht erhebliche Schäden.",
#     "Verdächtige Aktivitäten wurden in einem Park gemeldet.",
#     "Autounfall an der Kreuzung mit hohem Sachschaden.",
#     "Ein Raubüberfall auf einen Supermarkt ereignete sich am Abend.",
#     "Verkehrskontrolle führte zur Festnahme eines betrunkenen Fahrers.",
#     "Hausfriedensbruch wurde bei einer Privatparty festgestellt.",
#     "Ein Streifenwagen wurde bei einer Verfolgungsjagd beschädigt.",
#     "Person festgenommen wegen illegalen Drogenhandels.",
#     "Die Polizei stellte eine Waffe bei einer Personenkontrolle sicher.",
#     "Zeuge meldete eine Körperverletzung in der U-Bahn.",
#     "Unbekannte zündeten Mülltonnen in der Nacht an.",
#     "Hundebiss führte zu einer Anzeige wegen gefährlicher Körperverletzung.",
#     "Die Polizei ermittelt wegen eines sexuellen Übergriffs.",
#     "Fahrraddiebstahl vor einem Einkaufszentrum.",
#     "Am Bahnhof wurde ein Taschendieb festgenommen.",
#     "Ein vermisster Jugendlicher wurde wohlbehalten gefunden.",
#     "Verkehrsunfall mit Fahrerflucht auf der Autobahn.",
#     "Polizeihubschrauber unterstützte die Suche nach einem Verdächtigen.",
#     "Eine Explosion beschädigte mehrere Autos in einer Tiefgarage.",
#     "Kampf unter mehreren Personen in einer Diskothek.",
#     "Verdacht auf Betrug bei einer Online-Transaktion.",
#     "Mehrere Fahrzeuge wurden bei einer Schießerei beschädigt.",
#     "Die Polizei nahm einen Verdächtigen wegen Brandstiftung fest.",
#     "Ein Passant meldete eine hilflose Person am Straßenrand.",
# ]
# for text in examples:
#     result = classifier(text, candidate_labels=["Theft", "Assault", "Accident", "Burglary", "Arson", "Drug-related", "Vandalism", "Other"])
#     print(f"Text: {text}")
#     print(f"Labels: {result['labels']}")
#     print(f"Scores: {result['scores']}")
#     print("-" * 40)
#
#
# result = classifier("Deutscher Polizeibericht", candidate_labels=["Theft", "Assault", "Accident"])
# print(result)

candidate_labels = [
    "Diebstahl",  # theft
    "Raub",       # robbery
    "Bewaffneter Raub",  # armed robbery
    "Einbruch",   # burglary
    "Vandalismus",
    "Hausfriedensbruch",  # trespassing
    "Verkehrsunfall",
    "Verkehrsverstoß",
    "Alkoholfahrt",  # drunk driving
    "Körperverletzung",
    "Sexuelle Belästigung",
    "Brandstiftung",
    "Drogendelikte",
    "Vermisste Person",
    "Öffentliche Ruhestörung",
    "Verdächtige Aktivität",
    "Betrug",
    "Schießerei",
    "Sonstiges"
]
def remap_label(label):
    mapping = {
        "diebstahl": "Theft & Robbery",
        "raub": "Theft & Robbery",
        "bewaffneter raub": "Theft & Robbery",
        "einbruch": "Theft & Robbery",
        "körperverletzung": "Assault & Violent Crime",
        "sexuelle belästigung": "Assault & Violent Crime",
        "verkehrsunfall": "Traffic-related Incidents",
        "alkoholfahrt": "Traffic-related Incidents",
        "drogendelikte": "Drug-related Crime",
        "vandalismus": "Property Damage & Arson",
        "brandstiftung": "Property Damage & Arson",
        "verdächtige aktivität": "Suspicious Activity & Other",
        "betrug": "Suspicious Activity & Other",
        "hausfriedensbruch": "Suspicious Activity & Other",
        "vermisste person": "Missing Persons & Rescue",
        "schießerei": "Assault & Violent Crime",
        "öffentliche ruhestörung": "Suspicious Activity & Other",
        "verkehrsverstoß": "Traffic-related Incidents",
        "sonstiges": "Suspicious Activity & Other"
    }
    return mapping.get(label.lower(), "Suspicious Activity & Other")


candidate_labels = [
    "Diebstahl oder Raub",
    "Körperverletzung",
    "Verkehrsunfall",
    "Brandstiftung",
    "Drogendelikte",
    "Vermisste Person",
    "Verdächtige Aktivität",
    "Betrug",
    "Schießerei",
    "Sonstiges"
]
def remap_label(label):
    mapping = {
        "diebstahl oder raub": "Theft & Robbery",
        "körperverletzung": "Assault & Violent Crime",
        "verkehrsunfall": "Traffic-related Incidents",
        "brandstiftung": "Property Damage & Arson",
        "drogendelikte": "Drug-related Crime",
        "vermisste person": "Missing Persons & Rescue",
        "verdächtige aktivität": "Suspicious Activity & Other",
        "betrug": "Suspicious Activity & Other",
        "schießerei": "Assault & Violent Crime",
        "sonstiges": "Suspicious Activity & Other"
    }
    return mapping.get(label.lower(), "Suspicious Activity & Other")


def classify_text(text, classifier, labels, threshold=0.5):
    result = classifier(
        text,
        candidate_labels=labels,
        hypothesis_template="Dieser Bericht handelt von {}."
    )
    best_label = result['labels'][0]
    best_score = result['scores'][0]
    print(f"Top 3 predicted raw labels: {result['labels'][:3]}")
    print(f"Scores: {result['scores'][:3]}")
    if best_score < threshold:
        return "Uncertain", best_score
    return best_label, best_score






texts = [
    "Deutscher Polizeibericht über einen Diebstahl in Berlin.",
    "Ein bewaffneter Überfall wurde gestern in der Innenstadt gemeldet.",
    "Am Sonntag gab es einen Verkehrsunfall mit mehreren Verletzten.",
    "Person wurde wegen Körperverletzung verhaftet.",
    "Brand in einer Wohnung verursacht erhebliche Schäden.",
    "Verdächtige Aktivitäten wurden in einem Park gemeldet.",
    "Verkehrskontrolle führte zur Festnahme eines betrunkenen Fahrers.",
    "Hausfriedensbruch wurde bei einer Privatparty festgestellt.",
    "Person festgenommen wegen illegalen Drogenhandels.",
    "Die Polizei ermittelt wegen eines sexuellen Übergriffs.",
    "Fahrraddiebstahl vor einem Einkaufszentrum.",
    "Ein vermisster Jugendlicher wurde wohlbehalten gefunden.",
    "Verdacht auf Betrug bei einer Online-Transaktion.",
    "Mehrere Fahrzeuge wurden bei einer Schießerei beschädigt."
]

for text in texts:
    label, score = classify_text(text, classifier, candidate_labels, threshold=0.5)
    print(f"Text: {text}")
    print(f"Predicted label: {remap_label(label)} (score: {score:.3f})")
    print("-" * 40)


