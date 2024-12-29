import os
import json
import random
import numpy as np
from scipy.spatial.transform import Rotation as R

# Dynamische Pfaddefinitionen
script_dir = os.path.dirname(os.path.abspath(__file__))
testdata_folder = os.path.join(script_dir, '../../UnityProject_MovementAssessmentWithTeslasuit/Assets/JsonAttempts')  # Testdatenordner
output_folder = os.path.join(script_dir, '../../PythonFiles__MovementAssessmentWithTeslasuit/synthetic')  # Zielordner

# Funktion zum Einlesen der Originaldaten
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Funktion zur Augmentierung der Daten
def augment_data(data, angle_range=(-10, 10), translation_range=(-0.1, 0.1), scale_range=(0.9, 1.1)):
    augmented_data = []

    for frame in data:
        augmented_frame = {
            'replayPosition': {},
            'replayRotation': {}
        }

        for joint in frame['replayPosition']:
            pos = frame['replayPosition'][joint]
            rot = frame['replayRotation'][joint]

            # Zufällige Translation
            pos_x = pos['x'] + random.uniform(*translation_range)
            pos_y = pos['y'] + random.uniform(*translation_range)
            pos_z = pos['z'] + random.uniform(*translation_range)

            # Zufällige Rotation um alle drei Achsen
            rotation_x = random.uniform(*angle_range)
            rotation_y = random.uniform(*angle_range)
            rotation_z = random.uniform(*angle_range)
            rotation = R.from_euler('xyz', [rotation_x, rotation_y, rotation_z], degrees=True)

            rotated_pos = rotation.apply([pos_x, pos_y, pos_z])

            augmented_frame['replayPosition'][joint] = {
                'x': rotated_pos[0],
                'y': rotated_pos[1],
                'z': rotated_pos[2]
            }

            # Optional: Skalierung der Position für noch mehr Variation
            scale_factor = random.uniform(*scale_range)
            augmented_frame['replayPosition'][joint] = {
                'x': augmented_frame['replayPosition'][joint]['x'] * scale_factor,
                'y': augmented_frame['replayPosition'][joint]['y'] * scale_factor,
                'z': augmented_frame['replayPosition'][joint]['z'] * scale_factor
            }

            augmented_frame['replayRotation'][joint] = rot  # Rotation unverändert

        augmented_data.append(augmented_frame)

    return augmented_data

# Funktion zum Speichern der synthetischen Daten
def save_synthetic_data(augmented_data, original_file_name):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    base_name = os.path.basename(original_file_name).replace('.json', '_synthetic.json')
    output_file = os.path.join(output_folder, base_name)

    with open(output_file, 'w') as file:
        json.dump(augmented_data, file, indent=4)
    print(f"Synthetische Daten gespeichert unter: {output_file}")

# Hauptfunktion zur Generierung und Speicherung synthetischer Daten
def generate_and_save_synthetic_data(num_samples=20):
    json_files = [f for f in os.listdir(testdata_folder) if f.endswith('.json')]

    for json_file in json_files:
        file_path = os.path.join(testdata_folder, json_file)
        original_data = load_json_data(file_path)

        all_augmented_data = []
        for _ in range(num_samples):
            augmented_data = augment_data(original_data)
            all_augmented_data.extend(augmented_data)

        save_synthetic_data(all_augmented_data, json_file)

# Ausführung der Generierung
generate_and_save_synthetic_data(num_samples=20)
