import pandas as pd
import json
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import GroupShuffleSplit, RandomizedSearchCV
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.decomposition import PCA
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score, accuracy_score, roc_curve, auc
from imblearn.over_sampling import SMOTE
import numpy as np

# Dynamische Pfade basierend auf der aktuellen Position der Datei
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../UnityProject_MovementAssessmentWithTeslasuit/Assets/JsonAttempts")
MODEL_DIR = os.path.join(BASE_DIR, "../model")
VISUALIZE_DIR = os.path.join(BASE_DIR, "../visualize")

# Ordner erstellen, falls nicht vorhanden
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(VISUALIZE_DIR, exist_ok=True)

# Funktion zur Erstellung von Ordnern für spezifische Übungstypen
def create_exercise_folders(base_path, exercise_type, subfolders=None):
    exercise_path = os.path.join(base_path, exercise_type)
    os.makedirs(exercise_path, exist_ok=True)
    if subfolders:
        for folder in subfolders:
            os.makedirs(os.path.join(exercise_path, folder), exist_ok=True)
    return exercise_path

# Funktion zum Extrahieren der Merkmale aus den Positionen und Rotationen
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

# Funktion zum Parsen des Dateinamens
def parse_filename(file_name):
    try:
        base_name = os.path.basename(file_name).replace('.json', '')
        parts = base_name.split('_')
        if len(parts) < 3:
            raise ValueError(f"Ungültiges Dateinamensformat: {file_name}")
        number, exercise_type, label = parts[:3]
        is_synthetic = "Synthetic" in file_name
        return exercise_type, label, is_synthetic, number
    except Exception as e:
        print(f"Fehler beim Parsen des Dateinamens: {e}")
        return None, None, False, None

# Funktion zur Entfernung von Duplikaten mit Synchronisation der Gruppen
def remove_duplicates_with_groups(data, groups):
    unique_data_with_indices = {tuple(x): i for i, x in enumerate(data)}
    unique_data = [list(k) for k in unique_data_with_indices.keys()]
    unique_indices = list(unique_data_with_indices.values())
    updated_groups = [groups[i] for i in unique_indices]
    print(f"Anzahl Duplikate entfernt: {len(data) - len(unique_data)}")
    return unique_data, updated_groups

# Überprüfung auf Duplikate
def check_duplicates(X_train, X_test):
    duplicates = set(map(tuple, X_train)).intersection(set(map(tuple, X_test)))
    print(f"Anzahl identischer Datenpunkte in Training und Test: {len(duplicates)}")
    return duplicates

# Speichern der Modellmetriken in einer JSON-Datei
def save_metrics(exercise_type, model_name, accuracy, f1, precision, recall):
    metrics_path = os.path.join(MODEL_DIR, "model_accuracies.json")
    if not os.path.exists(metrics_path):
        with open(metrics_path, 'w') as f:
            json.dump({}, f)

    with open(metrics_path, 'r') as f:
        metrics = json.load(f)

    if exercise_type not in metrics:
        metrics[exercise_type] = {}

    metrics[exercise_type][model_name] = {
        "accuracy": accuracy,
        "f1_score": f1,
        "precision": precision,
        "recall": recall
    }

    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)

# Speichern der Confusion Matrix
def save_confusion_matrix(cm, labels, title, path):
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title(title)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig(path)
    plt.close()

# Speichern der ROC-Kurve
def save_roc_curve(y_test, y_pred_prob, labels, title, path):
    plt.figure(figsize=(10, 7))
    y_test_binarized = label_binarize(y_test, classes=labels)
    if y_test_binarized.shape[1] == 1:  # Prüfen, ob nur eine Klasse vorhanden ist
        print("Warnung: ROC-Kurve kann nicht generiert werden, da nur eine Klasse vorhanden ist.")
        return

    for i, label in enumerate(labels):
        if i >= y_pred_prob.shape[1]:
            continue  # Schutz vor Index-Fehlern

        fpr, tpr, _ = roc_curve(y_test_binarized[:, i], y_pred_prob[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"{label} (AUC = {roc_auc:.2f})")

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc="lower right")
    plt.savefig(path)
    plt.close()

# Alle JSON-Dateien im Ordner sammeln
json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]

# Trainingstypen organisieren
training_data = {}
real_groups = []  # Gruppen für echte Daten
synthetic_groups = []  # Gruppen für synthetische Daten

for json_file in json_files:
    exercise_type, label, is_synthetic, group = parse_filename(json_file)
    if exercise_type is None:
        continue

    if exercise_type not in training_data:
        training_data[exercise_type] = {"Positive": [], "Negative": [], "Synthetic": {"Positive": [], "Negative": []}}

    json_file_path = os.path.join(DATA_DIR, json_file)
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    features = extract_features(data)

    # Gruppen erweitern nur für die aktuelle Datei
    if is_synthetic:
        training_data[exercise_type]["Synthetic"][label].extend(features)
        synthetic_groups.extend([group] * len(features))  # Gruppen für synthetische Daten
    else:
        training_data[exercise_type][label].extend(features)
        real_groups.extend([group] * len(features))  # Gruppen für echte Daten

# Training und Evaluierung für jeden Übungstyp
for exercise_type, data in training_data.items():
    print(f"\nStarte Training für: {exercise_type}")

    # Übungsordner erstellen
    exercise_model_dir = create_exercise_folders(MODEL_DIR, exercise_type)
    exercise_visual_dir = create_exercise_folders(
        VISUALIZE_DIR, exercise_type, subfolders=["TrainTestSplit", "PositiveNegative", "ROC", "ConfusionMatrix"]
    )

    # Duplikate entfernen und Gruppen synchronisieren
    positive_samples, real_positive_groups = remove_duplicates_with_groups(
        data["Positive"], real_groups[:len(data["Positive"])]
    )
    negative_samples, real_negative_groups = remove_duplicates_with_groups(
        data["Negative"], real_groups[len(data["Positive"]):len(data["Positive"]) + len(data["Negative"])]
    )
    synthetic_positive_samples, synthetic_positive_groups = remove_duplicates_with_groups(
        data["Synthetic"]["Positive"], synthetic_groups[:len(data["Synthetic"]["Positive"])]
    )
    synthetic_negative_samples, synthetic_negative_groups = remove_duplicates_with_groups(
        data["Synthetic"]["Negative"], synthetic_groups[len(data["Synthetic"]["Positive"]):]
    )

    all_features = (
        positive_samples + negative_samples + synthetic_positive_samples + synthetic_negative_samples
    )
    all_groups = (
        real_positive_groups + real_negative_groups + synthetic_positive_groups + synthetic_negative_groups
    )
    all_labels = (
        ['korrekt'] * len(positive_samples) +
        ['fehlerhaft'] * len(negative_samples) +
        ['korrekt'] * len(synthetic_positive_samples) +
        ['fehlerhaft'] * len(synthetic_negative_samples)
    )

    # Gruppierte Aufteilung mit strikter Trennung
    splitter = GroupShuffleSplit(test_size=0.2, random_state=42)
    for train_idx, test_idx in splitter.split(all_features, all_labels, groups=all_groups):
        train_groups = set([all_groups[i] for i in train_idx])
        test_groups = set([all_groups[i] for i in test_idx])

        if train_groups.isdisjoint(test_groups):
            break

    # Train-Test-Aufteilung
    X_train = [all_features[i] for i in train_idx]
    y_train = [all_labels[i] for i in train_idx]
    X_test = [all_features[i] for i in test_idx]
    y_test = [all_labels[i] for i in test_idx]

    # PCA-Visualisierung: Train-Test-Aufteilung
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train + X_test)
    pca = PCA(n_components=2)
    reduced_features = pca.fit_transform(X_scaled)

    train_test_labels = ['Train'] * len(X_train) + ['Test'] * len(X_test)
    plt.figure(figsize=(10, 7))
    sns.scatterplot(x=reduced_features[:, 0], y=reduced_features[:, 1], hue=train_test_labels, palette="Set1")
    plt.title(f"PCA Train-Test für {exercise_type}")
    train_test_path = os.path.join(exercise_visual_dir, "TrainTestSplit", "pca_train_test.png")
    plt.savefig(train_test_path)
    plt.close()

    # PCA-Visualisierung: Positiv-Negativ-Aufteilung
    pos_neg_labels = y_train + y_test
    plt.figure(figsize=(10, 7))
    sns.scatterplot(x=reduced_features[:, 0], y=reduced_features[:, 1], hue=pos_neg_labels, palette="Set2")
    plt.title(f"PCA Positive-Negative für {exercise_type}")
    pos_neg_path = os.path.join(exercise_visual_dir, "PositiveNegative", "pca_positive_negative.png")
    plt.savefig(pos_neg_path)
    plt.close()

    # Modelle definieren und trainieren
    models = {
        "SVM": SVC(kernel='rbf', C=1, gamma='scale', class_weight='balanced', probability=True),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, class_weight='balanced'),
        "k-NN": KNeighborsClassifier(),
        "Naive Bayes": GaussianNB()
    }

    for model_name, model in models.items():
        print(f"\nTraining {model_name} für {exercise_type}...")
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        cm = confusion_matrix(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        accuracy = accuracy_score(y_test, y_pred)

        model_path = os.path.join(exercise_model_dir, f"{model_name}_model.pkl")
        joblib.dump(model, model_path)

        # Speichern der Confusion Matrix
        cm_path = os.path.join(exercise_visual_dir, "ConfusionMatrix", f"{model_name}_confusion_matrix.png")
        save_confusion_matrix(cm, ['korrekt', 'fehlerhaft'], f"Confusion Matrix für {model_name}", cm_path)

        # ROC-Kurve speichern (falls möglich)
        if hasattr(model, "predict_proba"):
            y_pred_prob = model.predict_proba(X_test)
        elif hasattr(model, "decision_function"):
            y_pred_prob = model.decision_function(X_test)
            y_pred_prob = np.column_stack((1 - y_pred_prob, y_pred_prob))  # Skaliere Werte für binäre Klassifikation
        else:
            y_pred_prob = None

        if y_pred_prob is not None:
            roc_path = os.path.join(exercise_visual_dir, "ROC", f"{model_name}_roc_curve.png")
            save_roc_curve(y_test, y_pred_prob, ['korrekt', 'fehlerhaft'], f"ROC Curve für {model_name}", roc_path)

        # Metriken speichern
        save_metrics(exercise_type, model_name, accuracy, f1, precision, recall)
