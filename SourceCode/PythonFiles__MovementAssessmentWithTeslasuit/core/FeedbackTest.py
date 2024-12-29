import pandas as pd
import json
import os
from sklearn.metrics import classification_report
import joblib

# Dynamische Pfaddefinitionen
script_dir = os.path.dirname(os.path.abspath(__file__))  # Verzeichnis des aktuellen Skripts
models_folder_path = os.path.join(script_dir, '../../PythonFiles__MovementAssessmentWithTeslasuit/model')  # Pfad für Modelle
test_data_folder = os.path.join(script_dir, '../../PythonFiles__MovementAssessmentWithTeslasuit/synthetic')  # Pfad für Testdaten
result_folder = os.path.join(script_dir, "../result")

os.makedirs(result_folder, exist_ok=True)

# Funktion zum Extrahieren der Merkmale aus den Positionen und Rotationen
def extract_features(data):
    features = []
    for frame in data:
        feature_vector = []

        # Extrahiere Positionen und Rotationen für jedes Gelenk
        for joint in ['Hips', 'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg',
                      'LeftFoot', 'RightFoot', 'Spine', 'Chest', 'LeftShoulder', 'RightShoulder',
                      'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm', 'LeftHand', 'RightHand']:
            try:
                # Extrahiere Position
                position = frame['replayPosition'][joint]
                feature_vector.extend([position['x'], position['y'], position['z']])

                # Extrahiere Rotation
                rotation = frame['replayRotation'][joint]
                feature_vector.extend([rotation['x'], rotation['y'], rotation['z']])
            except KeyError:
                # Falls ein Joint fehlt, auffüllen mit Nullwerten
                feature_vector.extend([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        features.append(feature_vector)
    return features

# Testdaten und Modelle laden
model_files = [f for f in os.listdir(models_folder_path) if f.endswith('.pkl')]
test_files = [f for f in os.listdir(test_data_folder) if f.endswith('.json')]

# Ergebnisse speichern
results = {}

# Testdaten vorbereiten
all_test_features = []
all_test_labels = []

for test_file in test_files:
    test_file_path = os.path.join(test_data_folder, test_file)

    with open(test_file_path, 'r') as file:
        data = json.load(file)

    # Extrahiere Merkmale aus den Testdaten
    features = extract_features(data)
    all_test_features.extend(features)

    # Labels aus dem Dateinamen ableiten
    if '_Positive' in test_file:
        all_test_labels.extend(['korrekt'] * len(features))
    elif '_Negative' in test_file:
        all_test_labels.extend(['fehlerhaft'] * len(features))

# Überprüfen der Datenkonsistenz
print(f"Länge von test_df: {len(all_test_features)}")
print(f"Länge von test_labels: {len(all_test_labels)}")

if len(all_test_features) != len(all_test_labels):
    raise ValueError("Die Anzahl der Testmerkmale stimmt nicht mit der Anzahl der Testlabels überein.")

# DataFrame für Testdaten erstellen
columns = []
for joint in ['Hips', 'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg',
              'LeftFoot', 'RightFoot', 'Spine', 'Chest', 'LeftShoulder', 'RightShoulder',
              'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm', 'LeftHand', 'RightHand']:
    columns.extend([f'{joint}_pos_x', f'{joint}_pos_y', f'{joint}_pos_z',
                    f'{joint}_rot_x', f'{joint}_rot_y', f'{joint}_rot_z'])

test_df = pd.DataFrame(all_test_features, columns=columns)
test_labels = pd.Series(all_test_labels, name='label')

# Alle Modelle laden und testen
for model_file in model_files:
    model_path = os.path.join(models_folder_path, model_file)

    # Modell laden
    model = joblib.load(model_path)
    print(f"\nTesting Model: {model_file}")

    # Vorhersagen machen
    y_pred = model.predict(test_df)
    print(f"Länge der Vorhersagen (y_pred): {len(y_pred)}")

    if len(y_pred) != len(test_labels):
        raise ValueError("Die Anzahl der Vorhersagen stimmt nicht mit der Anzahl der Testlabels überein.")

    # Bewertung
    report = classification_report(test_labels, y_pred, output_dict=True, zero_division=1)
    results[model_file] = report

    # Ergebnisse ausgeben
    print(f"Ergebnisse für {model_file}:")
    print(classification_report(test_labels, y_pred))

# Zusammenfassung der Ergebnisse speichern
results_summary = pd.DataFrame({
    model_file: {
        "Accuracy": report["accuracy"],
        "F1-Score (korrekt)": report["korrekt"]["f1-score"],
        "F1-Score (fehlerhaft)": report["fehlerhaft"]["f1-score"]
    }
    for model_file, report in results.items()
}).T

# Speichern der Ergebnisse in eine CSV-Datei
results_summary_path = os.path.join(result_folder, "TestFeedback_Results.csv")
results_summary.to_csv(results_summary_path, index=True)
print(f"\nZusammenfassung der Ergebnisse wurde gespeichert: {results_summary_path}")
