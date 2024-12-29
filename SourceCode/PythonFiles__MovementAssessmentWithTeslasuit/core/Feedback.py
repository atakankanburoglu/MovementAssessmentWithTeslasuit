import joblib
import numpy as np

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
        return "Fehlhaltung erkannt" if prediction[0] == 'fehlerhaft' else "Keine Fehlhaltung"