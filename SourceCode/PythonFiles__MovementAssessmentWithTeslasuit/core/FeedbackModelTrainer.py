import pandas as pd
import json
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Dynamische Pfade
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../UnityProject_MovementAssessmentWithTeslasuit/Assets/JsonAttempts")
MODEL_DIR = os.path.join(BASE_DIR, "../model")

os.makedirs(MODEL_DIR, exist_ok=True)

# Funktion zum Extrahieren der Merkmale
def extract_features(data):
    features = []
    for frame in data:
        feature_vector = []
        for joint in ['Hips', 'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg',
                      'LeftFoot', 'RightFoot', 'Spine', 'Chest', 'LeftShoulder', 'RightShoulder',
                      'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm', 'LeftHand', 'RightHand']:
            position = frame['replayPosition'][joint]
            rotation = frame['replayRotation'][joint]
            feature_vector.extend([position['x'], position['y'], position['z'],
                                   rotation['x'], rotation['y'], rotation['z']])
        features.append(feature_vector)
    return features

# Funktion zum Laden und Verarbeiten der Daten
def load_and_process_data():
    data = []
    labels = []

    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json') and ('_Positive.json' in f or '_Negative.json')]
    for json_file in json_files:
        label = 'korrekt' if '_Positive' in json_file else 'fehlerhaft'
        file_path = os.path.join(DATA_DIR, json_file)

        with open(file_path, 'r') as file:
            json_data = json.load(file)
        features = extract_features(json_data)

        data.extend(features)
        labels.extend([label] * len(features))

    return pd.DataFrame(data), pd.Series(labels)

# Hauptfunktion für Training und Evaluation
def train_and_evaluate():
    X, y = load_and_process_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Modellpipeline mit StandardScaler
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', RandomForestClassifier())
    ])

    # Random Forest Parameter
    pipeline.set_params(classifier__n_estimators=100, classifier__max_depth=None)

    # Training und Evaluation
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    print("Klassifikationsbericht:")
    print(classification_report(y_test, y_pred))

    # Speichern des Modells
    model_path = os.path.join(MODEL_DIR, "RandomForest_model.pkl")
    joblib.dump(pipeline, model_path)
    print(f"Modell gespeichert unter: {model_path}")

# Ausführung
train_and_evaluate()
