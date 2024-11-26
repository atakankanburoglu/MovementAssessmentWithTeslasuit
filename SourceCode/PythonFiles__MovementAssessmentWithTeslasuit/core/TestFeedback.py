from Feedback import Feedback  # Importiere die Feedback-Klasse

# Beispiel: IMU-Daten mit Fehlstellung generieren
def get_imu_data_with_misalignment():
    imu_data = {
        'replayPosition': {
            'Hips': {'x': 0.0, 'y': 1.0, 'z': 0.0},
            'LeftUpperLeg': {'x': 0.1, 'y': 0.9, 'z': 0.0},
            'RightUpperLeg': {'x': -0.1, 'y': 0.9, 'z': 0.0},
            'LeftLowerLeg': {'x': 0.1, 'y': 0.8, 'z': 0.0},
            'RightLowerLeg': {'x': -0.1, 'y': 0.8, 'z': 0.0},
            'LeftFoot': {'x': 0.1, 'y': 0.7, 'z': 0.0},
            'RightFoot': {'x': -0.1, 'y': 0.7, 'z': 0.0},
            'Spine': {'x': 0.0, 'y': 1.1, 'z': 0.0},
            'Chest': {'x': 0.0, 'y': 1.2, 'z': 0.0},
            'LeftShoulder': {'x': 0.2, 'y': 1.3, 'z': 0.0},
            'RightShoulder': {'x': -0.2, 'y': 1.3, 'z': 0.0},
            'LeftUpperArm': {'x': 0.3, 'y': 1.4, 'z': 0.0},
            'RightUpperArm': {'x': -0.3, 'y': 1.4, 'z': 0.0},
            'LeftLowerArm': {'x': 0.4, 'y': 1.5, 'z': 0.0},
            'RightLowerArm': {'x': -0.4, 'y': 1.5, 'z': 0.0},
            'LeftHand': {'x': 0.5, 'y': 1.6, 'z': 0.0},
            'RightHand': {'x': -0.5, 'y': 1.6, 'z': 0.0}
        },
        'replayRotation': {
            'Hips': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'LeftUpperLeg': {'x': 0.1, 'y': 0.1, 'z': 0.1},
            'RightUpperLeg': {'x': -0.1, 'y': 0.1, 'z': 0.1},
            'LeftLowerLeg': {'x': 0.2, 'y': 0.2, 'z': 0.2},
            'RightLowerLeg': {'x': -0.2, 'y': 0.2, 'z': 0.2},
            'LeftFoot': {'x': 0.3, 'y': 0.3, 'z': 0.3},
            'RightFoot': {'x': -0.3, 'y': 0.3, 'z': 0.3},
            'Spine': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'Chest': {'x': 0.1, 'y': 0.1, 'z': 0.1},
            'LeftShoulder': {'x': 0.2, 'y': 0.2, 'z': 0.2},
            'RightShoulder': {'x': -0.2, 'y': 0.2, 'z': 0.2},
            'LeftUpperArm': {'x': 0.3, 'y': 0.3, 'z': 0.3},
            'RightUpperArm': {'x': -0.3, 'y': 0.3, 'z': 0.3},
            'LeftLowerArm': {'x': 0.4, 'y': 0.4, 'z': 0.4},
            'RightLowerArm': {'x': -0.4, 'y': 0.4, 'z': 0.4},
            'LeftHand': {'x': 0.5, 'y': 0.5, 'z': 0.5},
            'RightHand': {'x': -0.5, 'y': 0.5, 'z': 0.5}
        }
    }

    imu_data['replayRotation']['Hips'] = {'x': 0.2, 'y': 0.0, 'z': 0.0}  # Fehlstellung hinzufügen

    return imu_data

def test_feedback_system():
    model_path = "/Users/mac113/Desktop/Personal/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles__MovementAssessmentWithTeslasuit/model/SVM_model.pkl"
    try:
        feedback_system = Feedback(model_path=model_path)
        print("Feedback-System wurde erstellt")
    except Exception as e:
        print(f"Fehler beim Erstellen des Feedback-Systems: {e}")
        return

    # IMU-Daten mit Fehlstellung generieren
    imu_data_with_misalignment = get_imu_data_with_misalignment()

    try:
        # Fehlstellung erkennen
        misalignment_detected = feedback_system.detect_misalignment(imu_data_with_misalignment)
        print(f"Fehlstellung erkannt: {misalignment_detected}")
    except Exception as e:
        print(f"Fehler bei der Fehlstellungserkennung: {e}")

# Die Funktion test_feedback_system ausführen
if __name__ == "__main__":
    test_feedback_system()
