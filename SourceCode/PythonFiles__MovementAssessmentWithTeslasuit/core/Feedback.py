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
        print("Erkenne Fehlstellung...")
        posture = self.predict_posture(imu_data)  # Hier könnte das Modell oder eine andere Methode zur Vorhersage aufgerufen werden
        # Beispiel einer einfachen Fehlstellungserkennung basierend auf Schwellenwerten:
        misalignment_detected = False

        # Hier kannst du Schwellenwerte setzen, um eine Fehlstellung zu erkennen
        for joint in imu_data['replayPosition']:
            x, y, z = imu_data['replayPosition'][joint].values()
            # Beispielhafte Berechnung von Fehlstellungen
            if abs(x) > 0.1 or abs(y) > 0.1 or abs(z) > 0.1:
                misalignment_detected = True
                print(f"Fehlstellung bei {joint}: x={x}, y={y}, z={z}")

        print(f"Erkannte Körperhaltung: {posture}")
        return misalignment_detected


    def predict_posture(self, imu_data):
        # Hier könnte eine Vorhersage basierend auf dem Modell gemacht werden.
        # Aktuell gibt es keine Vorhersagefunktion, also geben wir einen Dummy-Wert zurück
        print("Berechne die Körperhaltung...")
        return "Korrekt"  # Dummy-Wert
