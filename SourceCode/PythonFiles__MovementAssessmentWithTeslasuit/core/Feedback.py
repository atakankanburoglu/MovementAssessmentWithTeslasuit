import numpy as np
import joblib

class Feedback:
    def __init__(self, model_path):
        self.model = self.load_model(model_path)

    def load_model(self, model_path):
        with open(model_path, 'rb') as f:
            return joblib.load(f)

    def detect_misalignment(self, data):
        input_vector = []
        for joint, values in data["replayPosition"].items():
            input_vector.extend([values["x"], values["y"], values["z"]])
        for joint, values in data["replayRotation"].items():
            input_vector.extend([values["x"], values["y"], values["z"]])

        input_array = np.array([input_vector])
        prediction = self.model.predict(input_array)
        result = "Fehlhaltung erkannt" if prediction[0] == 'fehlerhaft' else "Keine Fehlhaltung"
        return result

    def detect_deviations(self, data):
        deviations = {}

        for joint, values in data["replayPosition"].items():
            # Simulierte Abweichungen für jedes Gelenk (Beispielwerte)
            deviation_vector = np.array([0.1, 0.0, -0.1])  # Abweichung in x, y, z
            intensity = np.linalg.norm(deviation_vector)  # Intensität der Abweichung

            deviations[joint] = {
                "vector": deviation_vector.tolist(),
                "intensity": float(intensity)
            }

        return deviations
