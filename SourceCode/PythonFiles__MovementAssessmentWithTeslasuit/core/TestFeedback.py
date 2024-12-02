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
        'replayRotation': {joint: {'x': 0.0, 'y': 0.0, 'z': 0.0} for joint in [
            'Hips', 'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg',
            'LeftFoot', 'RightFoot', 'Spine', 'Chest', 'LeftShoulder', 'RightShoulder',
            'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm', 'LeftHand', 'RightHand'
        ]}
    }
    return imu_data

# Beispiel: IMU-Daten ohne Fehlstellung generieren
def get_correct_imu_data():
    imu_data = {
        'replayPosition': {joint: {'x': 0.0, 'y': 1.0, 'z': 0.0} for joint in [
            'Hips', 'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg',
            'LeftFoot', 'RightFoot', 'Spine', 'Chest', 'LeftShoulder', 'RightShoulder',
            'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm', 'LeftHand', 'RightHand'
        ]},
        'replayRotation': {joint: {'x': 0.0, 'y': 0.0, 'z': 0.0} for joint in [
            'Hips', 'LeftUpperLeg', 'RightUpperLeg', 'LeftLowerLeg', 'RightLowerLeg',
            'LeftFoot', 'RightFoot', 'Spine', 'Chest', 'LeftShoulder', 'RightShoulder',
            'LeftUpperArm', 'RightUpperArm', 'LeftLowerArm', 'RightLowerArm', 'LeftHand', 'RightHand'
        ]}
    }
    return imu_data

def test_feedback_system():
    model_path = "/Users/mac113/Desktop/Personal/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles__MovementAssessmentWithTeslasuit/model/SVM_model.pkl"
    feedback_system = Feedback(model_path=model_path)

    # Test 1: Mit Fehlstellung
    print("\n--- Test 1: Fehlstellung ---")
    imu_data_with_misalignment = get_imu_data_with_misalignment()
    misalignment_detected = feedback_system.detect_misalignment(imu_data_with_misalignment)
    print("Fehlstellung erkannt:", misalignment_detected)

    # Test 2: Ohne Fehlstellung
    print("\n--- Test 2: Keine Fehlstellung ---")
    correct_imu_data = get_correct_imu_data()
    misalignment_detected = feedback_system.detect_misalignment(correct_imu_data)
    print("Fehlstellung erkannt:", misalignment_detected)

# Die Funktion test_feedback_system ausführen
if __name__ == "__main__":
    test_feedback_system()
