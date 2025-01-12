import os
import json
import numpy as np
import joblib

class Feedback:
    def __init__(self, exercise_type, model_name, model_base_dir, data_dir):
        """
        Parameters:
        -----------
        exercise_type: str
            z.B. "GLUTEBRIDGE", "SQUAT", ...
        model_name: str
            Basename des Modells, z. B. "k-NN", "Random Forest" etc. (ohne '_model.pkl')
        model_base_dir: str
            Pfad zum Modell-Root (z. B. ../model ).
        data_dir: str
            Pfad zum Ordner, in dem deine JSON-Trainingsdaten liegen (z. B. ../Assets/JsonAttempts ).
        """
        self.exercise_type = exercise_type
        self.model_name = model_name
        self.model_base_dir = model_base_dir
        self.data_dir = data_dir

        self.model = None
        self.reference_pose = {}

        # 1) Modell laden
        self.load_model()

        # 2) Referenzpose laden (bzw. on-the-fly erzeugen, falls nicht vorhanden)
        self.load_reference_pose()

    def load_model(self):
        """
        Lädt das Modell: model_base_dir/exercise_type/<model_name>_model.pkl
        """
        model_file = f"{self.model_name}_model.pkl"
        model_path = os.path.join(self.model_base_dir, self.exercise_type, model_file)

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modell nicht gefunden: {model_path}")

        with open(model_path, 'rb') as f:
            self.model = joblib.load(f)

    def load_reference_pose(self):
        """
        Lädt (oder berechnet bei Bedarf) eine reference_pose.json im Ordner:
            model_base_dir/exercise_type/reference_pose.json
        Falls es sie nicht gibt, wird sie aus den Positiv-Dateien (exercise_type + _Positive.json) in data_dir berechnet.
        """
        ref_pose_path = os.path.join(self.model_base_dir, self.exercise_type, "reference_pose.json")

        if os.path.exists(ref_pose_path):
            # Vorhanden -> einfach laden
            with open(ref_pose_path, 'r') as f:
                self.reference_pose = json.load(f)
        else:
            # Noch nicht vorhanden -> berechnen
            print(f"[INFO] reference_pose.json für {self.exercise_type} nicht gefunden. Erzeuge sie on-the-fly...")
            self.reference_pose = self.compute_reference_pose_for_exercise(self.exercise_type)
            
            if not self.reference_pose:
                # Falls auch keine Positivdaten da sind oder etwas schiefging, bleibts leer
                print(f"[WARN] Keine Referenzpose für {self.exercise_type} erstellt (keine Daten?). Abweichungen = 0.")
                return

            # Erstellten Dict speichern
            os.makedirs(os.path.join(self.model_base_dir, self.exercise_type), exist_ok=True)
            with open(ref_pose_path, 'w') as f:
                json.dump(self.reference_pose, f, indent=4)
            print(f"[OK] reference_pose.json unter {ref_pose_path} gespeichert.")

    def compute_reference_pose_for_exercise(self, exercise_type):
        """
        Sucht im data_dir nach *Positiv*-Dateien zu diesem exercise_type (z. B. GLUTEBRIDGE_Positive.json).
        Berechnet den Mittelwert aller x,y,z Koordinaten (und optional Rotation) und gibt ein Dictionary im
        Format:
          {
            "replayPosition": { "Hips": {"x":..., "y":..., "z":...}, ... },
            "replayRotation": {...}
          }
        zurück. Gibt {} (leer) zurück, wenn keine Daten gefunden werden.
        """
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        positive_files = []

        # 1) Herausfiltern: exercise_type + "_Positive.json"
        #    z.B. "123_GLUTEBRIDGE_Positive.json"
        for file_name in json_files:
            base, _ = os.path.splitext(file_name)
            parts = base.split('_')
            if len(parts) < 3:
                continue
            # parts[0] = "123", parts[1] = "GLUTEBRIDGE", parts[2] = "Positive"
            if parts[1].lower() == exercise_type.lower() and parts[2].lower() == "positive":
                positive_files.append(os.path.join(self.data_dir, file_name))

        if not positive_files:
            print(f"[WARN] Keine Positiv-Dateien gefunden für {exercise_type}.")
            return {}

        print(f"[INFO] Berechne reference_pose aus {len(positive_files)} Positiv-Dateien für {exercise_type}...")
        
        # 2) Mittelwertbildung
        position_sum = {}
        rotation_sum = {}
        count_position = {}
        count_rotation = {}

        total_frames = 0

        for file_path in positive_files:
            with open(file_path, 'r') as f:
                frames = json.load(f)  # Liste von Frame-Dictionaries

            for frame in frames:
                total_frames += 1

                # Positionen
                for joint, coords in frame["replayPosition"].items():
                    if joint not in position_sum:
                        position_sum[joint] = np.array([0.0, 0.0, 0.0])
                        count_position[joint] = 0
                    position_sum[joint] += np.array([coords["x"], coords["y"], coords["z"]])
                    count_position[joint] += 1

                # Rotationen (optional)
                for joint, coords in frame["replayRotation"].items():
                    if joint not in rotation_sum:
                        rotation_sum[joint] = np.array([0.0, 0.0, 0.0])
                        count_rotation[joint] = 0
                    rotation_sum[joint] += np.array([coords["x"], coords["y"], coords["z"]])
                    count_rotation[joint] += 1

        if total_frames == 0:
            print("[WARN] In den Positiv-Dateien waren keine Frames oder sie sind leer.")
            return {}

        # Referenzpose-Dict anlegen
        reference_pose = {
            "replayPosition": {},
            "replayRotation": {}
        }

        for joint, sum_vec in position_sum.items():
            c = count_position[joint]
            mean_vec = sum_vec / c
            reference_pose["replayPosition"][joint] = {
                "x": float(mean_vec[0]),
                "y": float(mean_vec[1]),
                "z": float(mean_vec[2])
            }

        for joint, sum_vec in rotation_sum.items():
            c = count_rotation[joint]
            mean_vec = sum_vec / c
            reference_pose["replayRotation"][joint] = {
                "x": float(mean_vec[0]),
                "y": float(mean_vec[1]),
                "z": float(mean_vec[2])
            }

        print(f"[INFO] -> {len(positive_files)} Dateien, {total_frames} Frames verarbeitet. Fertig.")
        return reference_pose

    def detect_misalignment(self, data):
        """
        Klassifiziert die Pose mit dem gelernten Modell.
        Gibt einen String zurück: 'Fehlhaltung erkannt' oder 'Keine Fehlhaltung'.
        """
        input_vector = []

        # Positionen
        for joint, values in data["replayPosition"].items():
            input_vector.extend([values["x"], values["y"], values["z"]])

        # Rotationen
        for joint, values in data["replayRotation"].items():
            input_vector.extend([values["x"], values["y"], values["z"]])

        input_array = np.array([input_vector])
        prediction = self.model.predict(input_array)
        result = "Fehlhaltung erkannt" if prediction[0] == 'fehlerhaft' else "Keine Fehlhaltung"
        return result

    def detect_deviations(self, data):
        """
        Berechnet echte Abweichungen (Positionsdifferenzen) zur geladenen Referenzpose.
        Falls self.reference_pose leer ist, => Abweichungen = 0.
        """
        deviations = {}

        if not self.reference_pose or "replayPosition" not in self.reference_pose:
            # Keine Referenzpose -> alles 0
            for joint in data["replayPosition"].keys():
                deviations[joint] = {
                    "vector": [0.0, 0.0, 0.0],
                    "intensity": 0.0
                }
            return deviations

        # Positionsabweichungen
        for joint, live_coords in data["replayPosition"].items():
            if joint not in self.reference_pose["replayPosition"]:
                deviation_vec = np.array([0.0, 0.0, 0.0])
            else:
                ref_coords = self.reference_pose["replayPosition"][joint]
                deviation_vec = np.array([
                    live_coords["x"] - ref_coords["x"],
                    live_coords["y"] - ref_coords["y"],
                    live_coords["z"] - ref_coords["z"]
                ])
            intensity = float(np.linalg.norm(deviation_vec))
            deviations[joint] = {
                "vector": deviation_vec.tolist(),
                "intensity": intensity
            }

        # Optional: Rotationsabweichungen
        # (Wenn du rotation mit einbeziehen willst)
        # for joint, live_rot in data["replayRotation"].items():
        #     if joint in self.reference_pose["replayRotation"]:
        #         ref_rot = self.reference_pose["replayRotation"][joint]
        #         # Euler-Diff oder Quaternions etc.
        #         # store extra info in deviations[joint]["rotation_intensity"] = ...
        return deviations
