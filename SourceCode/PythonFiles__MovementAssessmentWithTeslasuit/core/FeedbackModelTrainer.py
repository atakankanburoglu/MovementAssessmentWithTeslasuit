import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import (
    GroupShuffleSplit,
    GroupKFold,
    RandomizedSearchCV
)
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.decomposition import PCA
from sklearn.metrics import (
    confusion_matrix, f1_score, precision_score, recall_score, accuracy_score,
    roc_curve, auc, balanced_accuracy_score
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from imblearn.pipeline import Pipeline
from imblearn.pipeline import make_pipeline
from imblearn.over_sampling import SMOTE

from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.simplefilter("ignore", FutureWarning)

import matplotlib
matplotlib.use('Agg')  # Kein GUI-Fenster, z.B. auf Servern

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../UnityProject_MovementAssessmentWithTeslasuit/Assets/JsonAttempts")
MODEL_DIR = os.path.join(BASE_DIR, "../model")
VISUALIZE_DIR = os.path.join(BASE_DIR, "../visualize")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(VISUALIZE_DIR, exist_ok=True)

##################################################
# 1) Beispiel: Relative Koordinaten (Feature Engineering)
##################################################
def extract_features_relative(data):
    """
    Beispiel, wie man relative Koordinaten herausholt:
    - Hips als Ursprung (0, 0, 0)
    - Rotationen hier nur exemplarisch unverändert
    - Du kannst weitere Ansätze integrieren, z. B. Gelenkwinkel
    """
    features = []
    for frame in data:
        # Hips als Referenz
        hips_x = frame["replayPosition"]["Hips"]["x"]
        hips_y = frame["replayPosition"]["Hips"]["y"]
        hips_z = frame["replayPosition"]["Hips"]["z"]

        # Baue das Feature für alle relevanten Joints
        joints = [
            'Hips','LeftUpperLeg','RightUpperLeg','LeftLowerLeg','RightLowerLeg',
            'LeftFoot','RightFoot','Spine','Chest','LeftShoulder','RightShoulder',
            'LeftUpperArm','RightUpperArm','LeftLowerArm','RightLowerArm',
            'LeftHand','RightHand'
        ]
        feature_vector = []
        for joint in joints:
            # Relative Position
            x = frame["replayPosition"][joint]["x"] - hips_x
            y = frame["replayPosition"][joint]["y"] - hips_y
            z = frame["replayPosition"][joint]["z"] - hips_z
            # Rotation (hier global beibehalten)
            rx = frame["replayRotation"][joint]["x"]
            ry = frame["replayRotation"][joint]["y"]
            rz = frame["replayRotation"][joint]["z"]

            feature_vector.extend([x, y, z, rx, ry, rz])

        features.append(feature_vector)
    return features


##################################################
# (Optional) Eigene Funktion für mehrfaches GroupKFold,
# falls RepeatedGroupKFold nicht verfügbar ist.
##################################################
def repeated_group_kfold(X, y, groups, n_splits=5, n_repeats=3, random_state=None):
    rng = np.random.RandomState(random_state)
    unique_groups = np.unique(groups)

    for _ in range(n_repeats):
        rng.shuffle(unique_groups)
        # Mapping von Gruppen auf Indizes
        group_to_indices = {g: [] for g in unique_groups}
        for idx, grp in enumerate(groups):
            group_to_indices[grp].append(idx)
        
        # GroupKFold-ähnliche Splits bauen
        chunk_size = int(np.ceil(len(unique_groups)/n_splits))
        group_chunks = [unique_groups[i:i+chunk_size] 
                        for i in range(0, len(unique_groups), chunk_size)]
        
        # Falls mehr Teilmengen als n_splits, letztes mit vorletztem zusammenfügen
        if len(group_chunks) > n_splits:
            group_chunks[-2] = np.concatenate((group_chunks[-2], group_chunks[-1]))
            group_chunks.pop()
        
        for fold_idx in range(n_splits):
            test_groups = group_chunks[fold_idx]
            train_groups = np.concatenate([group_chunks[i] 
                                           for i in range(n_splits) if i != fold_idx])
            
            test_indices = [idx for g in test_groups for idx in group_to_indices[g]]
            train_indices = [idx for g in train_groups for idx in group_to_indices[g]]
            
            yield train_indices, test_indices


##################################################
# 2) Parsing & Daten-Organisation
##################################################
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


def load_data():
    """
    Liest alle JSON-Dateien ein, extrahiert relative Features,
    und trennt echte vs. synthetische in separate Groups.
    """
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]

    training_data = {}
    real_groups = []
    synthetic_groups = []

    for json_file in json_files:
        exercise_type, label, is_synthetic, group = parse_filename(json_file)
        if exercise_type is None:
            continue

        if exercise_type not in training_data:
            training_data[exercise_type] = {
                "Positive": [],
                "Negative": [],
                "Synthetic": {"Positive": [], "Negative": []}
            }

        json_file_path = os.path.join(DATA_DIR, json_file)
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Feature Engineering: relative Koordinaten
        features = extract_features_relative(data)

        if is_synthetic:
            training_data[exercise_type]["Synthetic"][label].extend(features)
            synthetic_groups.extend([group] * len(features))
        else:
            training_data[exercise_type][label].extend(features)
            real_groups.extend([group] * len(features))

    return training_data, real_groups, synthetic_groups


##################################################
# 3) Duplikate entfernen
##################################################
def remove_duplicates_with_groups(data, groups):
    # Remove duplicates but keep group alignment
    unique_data_with_indices = {tuple(x): i for i, x in enumerate(data)}
    unique_data = [list(k) for k in unique_data_with_indices.keys()]
    unique_indices = list(unique_data_with_indices.values())
    updated_groups = [groups[i] for i in unique_indices]
    print(f"Anzahl Duplikate entfernt: {len(data) - len(unique_data)}")
    return unique_data, updated_groups


def check_duplicates(X_train, X_test):
    # Debug-Funktion: Wie viele Duplikate im Train/Test?
    duplicates = set(map(tuple, X_train)).intersection(set(map(tuple, X_test)))
    print(f"Anzahl identischer Datenpunkte in Training und Test: {len(duplicates)}")
    return duplicates


##################################################
# 4) Utils fürs Speichern/Plotten
##################################################
def create_folders_for_exercise(exercise_type):
    from pathlib import Path
    exercise_model_dir = Path(MODEL_DIR) / exercise_type
    exercise_visual_dir = Path(VISUALIZE_DIR) / exercise_type
    exercise_model_dir.mkdir(parents=True, exist_ok=True)
    (exercise_visual_dir / "TrainTestSplit").mkdir(parents=True, exist_ok=True)
    (exercise_visual_dir / "PositiveNegative").mkdir(parents=True, exist_ok=True)
    (exercise_visual_dir / "ROC").mkdir(parents=True, exist_ok=True)
    (exercise_visual_dir / "ConfusionMatrix").mkdir(parents=True, exist_ok=True)

    return str(exercise_model_dir), str(exercise_visual_dir)


def save_confusion_matrix(cm, labels, title, path):
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=labels, yticklabels=labels)
    plt.title(title)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.savefig(path)
    plt.close()


def save_roc_curve(y_test, y_pred_prob, labels, title, path):
    from sklearn.preprocessing import label_binarize
    plt.figure(figsize=(10, 7))
    y_test_binarized = label_binarize(y_test, classes=labels)
    if y_test_binarized.shape[1] == 1:
        print("Warnung: ROC-Kurve kann nicht generiert werden, da nur eine Klasse vorhanden ist.")
        return

    from sklearn.metrics import roc_curve, auc
    for i, label_ in enumerate(labels):
        if i >= y_pred_prob.shape[1]:
            continue

        fpr, tpr, _ = roc_curve(y_test_binarized[:, i], y_pred_prob[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, label=f"{label_} (AUC = {roc_auc:.2f})")

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc="lower right")
    plt.savefig(path)
    plt.close()


def save_metrics_json(exercise_type, model_name, accuracy, f1, precision, recall, balanced_acc):
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
        "balanced_accuracy": balanced_acc,
        "f1_score": f1,
        "precision": precision,
        "recall": recall
    }

    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=4)


##################################################
# 5) Haupt-Trainingsschleife
##################################################
def main():
    training_data, real_groups, synthetic_groups = load_data()

    # Basis-Modelle
    base_models = {
        "SVM": SVC(probability=True, class_weight='balanced'),
        "Random Forest": RandomForestClassifier(class_weight='balanced'),
        "k-NN": KNeighborsClassifier(),
        "Naive Bayes": GaussianNB()
    }

    # Parameterräume für RandomizedSearch
    rf_param_dist = {
        'classifier__n_estimators': [50, 100, 200],
        'classifier__max_depth': [5, 10, 20, None],
        'classifier__min_samples_split': [2, 5, 10],
        'classifier__min_samples_leaf': [1, 2, 5],
        'classifier__max_features': ['sqrt', 'log2', None]
    }

    svm_param_dist = {
        'classifier__C': [0.01, 0.1, 1, 10, 100],
        'classifier__kernel': ['linear', 'rbf'],
        'classifier__gamma': ['scale','auto']
    }

    # Falls 5-Fold zu lange dauert, wähle 3-Fold
    n_splits = 3

    for exercise_type, data_dict in training_data.items():
        print(f"\n=== Training für {exercise_type} ===")

        model_dir, visual_dir = create_folders_for_exercise(exercise_type)

        # (a) Erzeuge finalen Sample-Pool
        pos = data_dict["Positive"]
        neg = data_dict["Negative"]
        syn_pos = data_dict["Synthetic"]["Positive"]
        syn_neg = data_dict["Synthetic"]["Negative"]

        # (b) Duplikate entfernen
        pos, rg_pos = remove_duplicates_with_groups(pos, real_groups[:len(pos)])
        neg, rg_neg = remove_duplicates_with_groups(
            neg, real_groups[len(pos):len(pos)+len(neg)]
        )
        syn_pos, sg_pos = remove_duplicates_with_groups(
            syn_pos, synthetic_groups[:len(syn_pos)]
        )
        syn_neg, sg_neg = remove_duplicates_with_groups(
            syn_neg, synthetic_groups[len(syn_pos):]
        )

        all_features = pos + neg + syn_pos + syn_neg
        all_labels = (
            ['korrekt'] * len(pos) +
            ['fehlerhaft'] * len(neg) +
            ['korrekt'] * len(syn_pos) +
            ['fehlerhaft'] * len(syn_neg)
        )
        all_groups = rg_pos + rg_neg + sg_pos + sg_neg

        # (c) Split per GroupKFold (oder GroupShuffleSplit), hier n_splits=3
        gkf = GroupKFold(n_splits=n_splits)

        # Wir nehmen nur den ersten Split
        train_idx, test_idx = next(gkf.split(all_features, all_labels, groups=all_groups))

        X_train_raw = [all_features[i] for i in train_idx]
        y_train = [all_labels[i] for i in train_idx]
        X_test_raw = [all_features[i] for i in test_idx]
        y_test = [all_labels[i] for i in test_idx]

        # (d) Pipeline definieren + RandomizedSearch
        for model_name, base_model in base_models.items():
            print(f"\nModell: {model_name}")

            # Pipeline mit explizit benanntem letzten Schritt: "classifier"
            pipe = Pipeline([
                ("scaler", StandardScaler()),
                ("smote", SMOTE(random_state=42)),
                ("classifier", base_model)
            ])

            # Passendes Param-Dict
            if model_name == "Random Forest":
                param_dist = rf_param_dist
            elif model_name == "SVM":
                param_dist = svm_param_dist
            else:
                param_dist = {}  # k-NN / Naive Bayes ohne Tuning

            if param_dist:
                random_search = RandomizedSearchCV(
                    estimator=pipe,
                    param_distributions=param_dist,
                    n_iter=8,  # Erhöhe, falls mehr Zeit
                    scoring='balanced_accuracy',
                    cv=2,  # 2-Fold, um Zeit zu sparen
                    random_state=42,
                    verbose=1,
                    n_jobs=-1  # alle Kerne nutzen
                )
                random_search.fit(X_train_raw, y_train)
                best_model = random_search.best_estimator_
                print(f"Best-Params: {random_search.best_params_}")
            else:
                # Kein Tuning
                pipe.fit(X_train_raw, y_train)
                best_model = pipe

            # Evaluate
            y_pred = best_model.predict(X_test_raw)
            cm = confusion_matrix(y_test, y_pred)
            acc = accuracy_score(y_test, y_pred)
            bal_acc = balanced_accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred, average='weighted')
            prec = precision_score(y_test, y_pred, average='weighted')
            rec = recall_score(y_test, y_pred, average='weighted')

            print(f"Ergebnisse - Accuracy: {acc:.3f}, Balanced Acc: {bal_acc:.3f}, F1: {f1:.3f}")

            # Modell speichern
            model_path = os.path.join(model_dir, f"{model_name}_model.pkl")
            joblib.dump(best_model, model_path)

            # Confusion-Matrix speichern
            cm_path = os.path.join(visual_dir, "ConfusionMatrix", f"{model_name}_confusion_matrix.png")
            save_confusion_matrix(cm, ['korrekt','fehlerhaft'], f"Confusion Matrix {model_name}", cm_path)

            # ROC-Kurve (falls möglich)
            try:
                if hasattr(best_model, "predict_proba"):
                    y_pred_prob = best_model.predict_proba(X_test_raw)
                elif hasattr(best_model, "decision_function"):
                    dec = best_model.decision_function(X_test_raw)
                    # 2D proba: [P(neg), P(pos)] via transform
                    y_pred_prob = np.column_stack((1 - dec, dec))
                else:
                    y_pred_prob = None

                if y_pred_prob is not None:
                    roc_path = os.path.join(visual_dir, "ROC", f"{model_name}_roc_curve.png")
                    save_roc_curve(y_test, y_pred_prob, ['korrekt','fehlerhaft'], f"ROC {model_name}", roc_path)
            except Exception as e:
                print(f"Fehler bei ROC-Kurve: {e}")

            # JSON-Metriken speichern
            save_metrics_json(exercise_type, model_name, acc, f1, prec, rec, bal_acc)

        # -- Optional: PCA Plot wie in deinem Beispiel --
        # Hier ausgelassen; könnte man nach dem Skalieren + ggf. SMOTE
        # rein fürs Plotten machen (nur Trainingsdaten oder X_train+X_test)


if __name__ == "__main__":
    main()
