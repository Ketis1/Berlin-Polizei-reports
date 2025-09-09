import pandas as pd
import ollama
from tqdm import tqdm
import time
import logging


class OllamaPoliceClassifier:
    def __init__(self, model_name="llama3.1:8b"):
        self.model_name = model_name
        self.categories = {
            "Gewaltverbrechen": "Körperverletzung, Raub, Überfall, sexuelle Belästigung, Bedrohung, Angriffe mit Waffen",
            "Eigentumsdelikte": "Diebstahl, Betrug, Einbruch, Urkundenfälschung, Sachbeschädigung, Trickbetrug",
            "Verkehrsdelikte": "Verkehrsunfälle, Fahrerflucht, Fahren ohne Fahrerlaubnis, Verkehrsverstöße",
            "Betäubungsmittel": "Drogenhandel, Rauschgiftdelikte, Verstöße gegen das Betäubungsmittelgesetz",
            "Brandstiftung": "Brandstiftung, Explosionen, Sprengstoffdelikte, Feuer legen",
            "Öffentliche Ordnung": "Demonstrationen, Versammlungen, Störung der öffentlichen Ordnung",
            "Sonstiges": "Vermisste Personen, sonstige Delikte"
        }

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test if Ollama is running and model is available"""
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': 'Hallo'}]
            )
            print(f"✅ Ollama connection successful with {self.model_name}")
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("Make sure Ollama is running and model is downloaded:")
            print(f"  ollama run {self.model_name}")
            raise

    def classify_event(self, title, description):
        """Classify a single police event"""

        categories_text = "\n".join([
            f"- {cat}: {desc}" for cat, desc in self.categories.items()
        ])

        prompt = f"""Du bist Experte für deutsche Polizeimeldungen. 

Kategorisiere diese Meldung in GENAU EINE Kategorie:

{categories_text}

REGELN:
1. Antworte nur mit dem Kategorienamen (z.B. "Gewaltverbrechen")
2. Keine Erklärungen oder zusätzlicher Text
3. Bei Unsicherheit: "Sonstiges"

MELDUNG:
Titel: {title}
Beschreibung: {(description or "")[:800]}

KATEGORIE:"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )

            result = response['message']['content'].strip()

            # Validate and clean result
            for category in self.categories.keys():
                if category.lower() in result.lower():
                    return category

            return "Sonstiges"

        except Exception as e:
            logging.error(f"Classification error: {e}")
            return "Sonstiges"

    def process_dataframe(self, df):
        """Process entire dataframe"""

        print(f"Verarbeite {len(df)} Polizeimeldungen mit {self.model_name}...")

        categories = []

        for idx, row in tqdm(df.iterrows(), total=len(df)):
            category = self.classify_event(row['title'], row['description'])
            categories.append(category)

            # Small delay to prevent overwhelming the model
            time.sleep(0.1)

        df['kategorie'] = categories
        return df


# Quick test function
def quick_test():
    """Test with sample data"""

    classifier = OllamaPoliceClassifier()

    test_cases = [
        ("Raub in der Innenstadt", "Ein Mann wurde mit Gewalt beraubt und verletzt"),
        ("Verkehrsunfall", "Zwei Autos kollidierten auf der Autobahn"),
        ("Drogenfund", "Polizei stellt Kokain sicher")
    ]

    print("\n🔍 Teste Klassifizierung:")
    print("-" * 40)

    for title, desc in test_cases:
        category = classifier.classify_event(title, desc)
        print(f"'{title}' → {category}")


if __name__ == "__main__":
    quick_test()