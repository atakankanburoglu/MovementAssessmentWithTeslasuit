import pickle
import os


class Feedback:
    def __init__(self, model_path):
        # Überprüfen, ob der angegebene Pfad existiert
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Das Modell unter {model_path} konnte nicht gefunden werden.")
        print(f"Versuche, Modell von {model_path} zu laden...")
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        try:
            # Modell mit pickle laden
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
                print(f"Modell erfolgreich geladen: {type(model)}")
            return model
        except Exception as e:
            print(f"Fehler beim Laden des Modells: {str(e)}")
            raise e

    def detect_misalignment(self, imu_data):
        """
        Überprüft die IMU-Daten auf Fehlstellungen im Vergleich zu einem Standardmodell.
        """
        print("Erkenne Fehlstellung...")
        misalignment_detected = False
        misaligned_joints = []

        for joint, position in imu_data['replayPosition'].items():
            # Beispiel für korrekte Standardpositionen (können angepasst werden)
            correct_position = {'x': 0.0, 'y': 1.0, 'z': 0.0}

            # Überprüfung der Abweichung
            deviation = {axis: abs(position[axis] - correct_position[axis]) for axis in ['x', 'y', 'z']}
            threshold = 0.05  # Schwellenwert definieren

            if any(deviation[axis] > threshold for axis in deviation):
                print(f"Fehlstellung bei {joint}: x={position['x']}, y={position['y']}, z={position['z']} "
                      f"(Abweichung: {deviation})")
                misalignment_detected = True
                misaligned_joints.append(joint)
            else:
                print(f"Position für {joint} ist korrekt: x={position['x']}, y={position['y']}, z={position['z']}")

        return misalignment_detected, misaligned_joints

    def generate_feedback_message(self, misaligned_joints):
        """
        Erzeugt eine Feedback-Nachricht basierend auf den Fehlstellungen.
        """
        if misaligned_joints:
            return f"Fehlstellung erkannt bei: {', '.join(misaligned_joints)}"
        return "Keine Fehlstellung erkannt"
