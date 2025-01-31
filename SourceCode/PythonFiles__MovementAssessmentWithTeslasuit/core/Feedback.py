import os
import json
import numpy as np
import joblib
from collections import deque

class Feedback:
    def __init__(self, exercise_type, model_name, model_base_dir, data_dir):
        """
        ML-Modell + z-Score-Analyse mit Stabilisierung durch gleitenden Mittelwert.
        """
        self.exercise_type = exercise_type
        self.model_name = model_name
        self.model_base_dir = model_base_dir
        self.data_dir = data_dir

        self.model = None
        self.stats_distribution = {}
        self.last_deviation_values = deque(maxlen=5)  # Speichert die letzten 5 Frames zur Mittelung

        self.load_model()
        self.load_or_compute_stats_distribution()

    def load_model(self):
        """Lädt das trainierte ML-Modell."""
        model_file = f"{self.model_name}_model.pkl"
        model_path = os.path.join(self.model_base_dir, self.exercise_type, model_file)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modell nicht gefunden: {model_path}")

        with open(model_path, 'rb') as f:
            self.model = joblib.load(f)

    def load_or_compute_stats_distribution(self):
        """Lädt oder berechnet die statistische Verteilung für Gelenkpositionen."""
        stats_file_path = os.path.join(self.model_base_dir, self.exercise_type, "stats_distribution.json")

        if os.path.exists(stats_file_path):
            with open(stats_file_path, 'r') as f:
                self.stats_distribution = json.load(f)
        else:
            print(f"[INFO] Keine Statistik gefunden für {self.exercise_type}. Berechne on-the-fly...")
            self.stats_distribution = self.compute_stats_distribution_for_exercise(self.exercise_type)

            if not self.stats_distribution:
                print(f"[WARN] Keine Statistik generiert (evtl. keine korrekten Daten?).")
                return

            os.makedirs(os.path.join(self.model_base_dir, self.exercise_type), exist_ok=True)
            with open(stats_file_path, 'w') as f:
                json.dump(self.stats_distribution, f, indent=4)
            print(f"[OK] stats_distribution.json gespeichert unter {stats_file_path}")

    def compute_stats_distribution_for_exercise(self, exercise_type):
        """Berechnet Mean & Std aus positiven Beispieldaten."""
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        positive_files = [os.path.join(self.data_dir, f) for f in json_files if f"{exercise_type}_Positive" in f]

        if not positive_files:
            print(f"[WARN] Keine Positiv-Beispiele für {exercise_type} gefunden.")
            return {}

        all_positions = {}
        for file_path in positive_files:
            with open(file_path, 'r') as f:
                frames = json.load(f)

            for frame in frames:
                if "replayPosition" not in frame:
                    continue
                for joint, coords in frame["replayPosition"].items():
                    if joint not in all_positions:
                        all_positions[joint] = []
                    all_positions[joint].append([coords["x"], coords["y"], coords["z"]])

        stats_distribution = {}
        for joint, vectors in all_positions.items():
            arr = np.array(vectors)
            mean_pos = arr.mean(axis=0)
            std_pos = arr.std(axis=0)
            std_pos = np.where(std_pos < 0.01, 0.01, std_pos)  # Kleine Std-Werte korrigieren

            stats_distribution[joint] = {
                "mean_pos": mean_pos.tolist(),
                "std_pos": std_pos.tolist()
            }

        return stats_distribution

    def detect_misalignment(self, data):
        """ML-Klassifikation kombiniert mit z-Score-Analyse und gleitendem Mittelwert."""
        input_vector = []
        for joint, values in data["replayPosition"].items():
            input_vector.extend([values["x"], values["y"], values["z"]])
        for joint, values in data["replayRotation"].items():
            input_vector.extend([values["x"], values["y"], values["z"]])

        input_array = np.array([input_vector])
        predicted_label = self.model.predict(input_array)[0]

        # Abweichungen berechnen
        deviations = self.detect_deviations(data)
        self.last_deviation_values.append(deviations)

        # Gleitender Mittelwert der letzten Frames
        avg_deviation = np.mean([sum(d["intensity"] for d in frame.values()) / len(frame) for frame in self.last_deviation_values])

        # Adaptive Schwellenwerte
        exercise_thresholds = {
            "WALLSIT": 0.03,
            "GLUTEBRIDGE": 0.09,
            "PLANKHOLD": 0.04,
            "SIDEPLANKRIGHT": 0.06,
        }
        threshold = exercise_thresholds.get(self.exercise_type, 0.04)

        # Falls ML-Modell 'fehlerhaft' erkennt, aber z-Score-Analyse stabil ist
        if predicted_label == 'fehlerhaft' and avg_deviation < threshold:
            return "Keine Fehlhaltung"

        return "Fehlhaltung erkannt" if predicted_label == 'fehlerhaft' else "Keine Fehlhaltung"

    def detect_deviations(self, data):
        """Berechnet z-Score Abweichungen mit Gelenk-Gewichtung."""
        deviations = {}

        if not self.stats_distribution:
            return {joint: {"vector": [0, 0, 0], "intensity": 0} for joint in data["replayPosition"]}

        # Kritische Gelenke haben höhere Gewichtung
        critical_joints = {"Spine": 2.0, "Chest": 1.8, "Hips": 1.5, "Knees": 1.3, "Feet": 0.2, "Arms": 0.1, "Hands": 0.1}

        for joint, live_coords in data["replayPosition"].items():
            if joint not in self.stats_distribution:
                deviations[joint] = {"vector": [0, 0, 0], "intensity": 0}
                continue

            mean_pos = np.array(self.stats_distribution[joint]["mean_pos"])
            std_pos = np.array(self.stats_distribution[joint]["std_pos"])
            live_vec = np.array([live_coords["x"], live_coords["y"], live_coords["z"]])

            z_vec = (live_vec - mean_pos) / std_pos
            intensity = float(np.linalg.norm(z_vec)) * critical_joints.get(joint, 1.0)

            deviations[joint] = {
                "vector": z_vec.tolist(),
                "intensity": intensity
            }

        return deviations
