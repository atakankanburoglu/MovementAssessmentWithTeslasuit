import pandas as pd
import json
import os
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report
import joblib

# Funktion zum Extrahieren der Merkmale aus den Positionen und Rotationen
def extract_features(data):
    features = []
    labels = []  # Hier speichern wir die Labels (z.B. 'korrekt' oder 'fehlerhaft')
    for frame in data:
        feature_vector = []

        # Extrahiere Positionen und Rotationen für jedes Gelenk
        for joint in ['Hips', 'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg',
                      'LeftFoot', 'RightFoot', 'Spine', 'Chest', 'LeftShoulder', 'RightShoulder',
                      'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm', 'LeftHand', 'RightHand']:
            # Extrahiere Position
            position = frame['replayPosition'][joint]
            feature_vector.extend([position['x'], position['y'], position['z']])

            # Extrahiere Rotation
            rotation = frame['replayRotation'][joint]
            feature_vector.extend([rotation['x'], rotation['y'], rotation['z']])

        features.append(feature_vector)

    return features

# Pfad zum Ordner mit den JSON-Dateien
folder_path = "SourceCode/UnityProject_MovementAssessmentWithTeslasuit/Assets/JsonAttempts"

# Alle JSON-Dateien im Ordner sammeln, nur positive und negative Dateien
json_files = [f for f in os.listdir(folder_path) if f.endswith('.json') and ('_Positive.json' in f or '_Negative.json' in f)]

# DataFrame für alle extrahierten Daten erstellen
all_features = []
all_labels = []

# Alle JSON-Dateien durchgehen und Merkmale extrahieren
for json_file in json_files:
    json_file_path = os.path.join(folder_path, json_file)

    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Extrahiere Merkmale aus den JSON-Dateien
    features = extract_features(data)
    all_features.extend(features)

    # Bestimme das Label basierend auf dem Dateinamen
    if '_Positive' in json_file:
        all_labels.extend(['korrekt'] * len(features))
    elif '_Negative' in json_file:
        all_labels.extend(['fehlerhaft'] * len(features))

# Erstelle einen pandas DataFrame aus den extrahierten Merkmalen
columns = []
# Füge Positionen und Rotationen als Spaltennamen hinzu
for joint in ['Hips', 'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg',
              'LeftFoot', 'RightFoot', 'Spine', 'Chest', 'LeftShoulder', 'RightShoulder',
              'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm', 'LeftHand', 'RightHand']:
    columns.extend([f'{joint}_pos_x', f'{joint}_pos_y', f'{joint}_pos_z',
                    f'{joint}_rot_x', f'{joint}_rot_y', f'{joint}_rot_z'])

# Erstelle den DataFrame
df = pd.DataFrame(all_features, columns=columns)
df['label'] = all_labels  # Füge das Label als letzte Spalte hinzu

# Überprüfen der Verteilung der Klassen
print("Verteilung der Klassen:", df['label'].value_counts())

# Wenn es nur eine Klasse gibt, dann ist das Modell nicht trainierbar
if len(df['label'].unique()) == 1:
    raise ValueError("Es gibt nur eine Klasse im Datensatz. Das Modell kann nicht trainiert werden.")

# Aufteilen der Daten in Trainings- und Testdaten (80% Training, 20% Test)
X = df.drop('label', axis=1)
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Definieren der Modelle
models = {
    "SVM": SVC(),
    "Random Forest": RandomForestClassifier(),
    "k-NN": KNeighborsClassifier(n_neighbors=5),
    "Naive Bayes": GaussianNB()
}

# Trainieren und Evaluieren der Modelle
results = {}

for model_name, model in models.items():
    print(f"\nTraining {model_name}...")

    # Trainiere das Modell
    model.fit(X_train, y_train)

    # Vorhersagen und Modellbewertung
    y_pred = model.predict(X_test)

    # Bewertung
    report = classification_report(y_test, y_pred, output_dict=True)
    results[model_name] = report

    # Modell speichern als PKL-Datei
    model_filename = f'{model_name}_model.pkl'
    joblib.dump(model, model_filename)

    # Ausgabe der Ergebnisse
    print(f"{model_name} Bewertung:")
    print(classification_report(y_test, y_pred))

# Ergebnisse der Modelle ausgeben
print("\nZusammenfassung der Modellbewertungen:")
for model_name, report in results.items():
    print(f"\n{model_name} - F1-Score (korrekt/fehlerhaft):")
    print(report['accuracy'])
