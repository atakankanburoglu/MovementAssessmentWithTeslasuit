import os
import json
import numpy as np
import random

# Dynamische Pfade basierend auf der aktuellen Position der Datei
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../UnityProject_MovementAssessmentWithTeslasuit/Assets/JsonAttempts")

# Verhältnis von synthetischen zu echten Dateien
SYNTHETIC_RATIO = 0.5  # Beispiel: Maximal 50 % synthetische Dateien im Vergleich zu den echten Dateien

# Funktion zum Hinzufügen von Rauschen, Skalierung, Rotation und Verzerrung
def add_advanced_noise_and_transform(data, noise_level=0.05, scale_range=(0.8, 1.2), rotation_range=(-15, 15)):
    noisy_data = []
    for frame in data:
        noisy_frame = {}
        for key, value in frame.items():
            if isinstance(value, dict) and all(coord in value for coord in ['x', 'y', 'z']):
                coords = np.array([value['x'], value['y'], value['z']])

                # Hinzufügen von Rauschen
                noise = np.random.uniform(-noise_level, noise_level, size=3)
                noisy_coords = coords + noise

                # Zufällige Rotation um alle Achsen
                angles = np.radians(np.random.uniform(*rotation_range, size=3))
                rotation_x = np.array([[1, 0, 0],
                                       [0, np.cos(angles[0]), -np.sin(angles[0])],
                                       [0, np.sin(angles[0]), np.cos(angles[0])]])
                rotation_y = np.array([[np.cos(angles[1]), 0, np.sin(angles[1])],
                                       [0, 1, 0],
                                       [-np.sin(angles[1]), 0, np.cos(angles[1])]])
                rotation_z = np.array([[np.cos(angles[2]), -np.sin(angles[2]), 0],
                                       [np.sin(angles[2]), np.cos(angles[2]), 0],
                                       [0, 0, 1]])

                noisy_coords = np.dot(rotation_x, noisy_coords)
                noisy_coords = np.dot(rotation_y, noisy_coords)
                noisy_coords = np.dot(rotation_z, noisy_coords)

                # Verzerrung und Skalierung
                distortion = np.random.uniform(0.9, 1.1, size=3)
                noisy_coords *= distortion

                scale_factor = np.random.uniform(*scale_range)
                noisy_coords *= scale_factor

                noisy_frame[key] = {'x': noisy_coords[0], 'y': noisy_coords[1], 'z': noisy_coords[2]}
            else:
                noisy_frame[key] = value  # Unveränderte Daten beibehalten
        noisy_data.append(noisy_frame)
    return noisy_data

# Funktion zur Spiegelung der Daten
def advanced_mirror_data(data):
    mirrored_data = []
    joint_map = {
        'LeftUpperLeg': 'RightUpperLeg',
        'RightUpperLeg': 'LeftUpperLeg',
        'LeftLowerLeg': 'RightLowerLeg',
        'RightLowerLeg': 'LeftLowerLeg',
        'LeftFoot': 'RightFoot',
        'RightFoot': 'LeftFoot',
        'LeftShoulder': 'RightShoulder',
        'RightShoulder': 'LeftShoulder',
        'LeftUpperArm': 'RightUpperArm',
        'RightUpperArm': 'LeftUpperArm',
        'LeftLowerArm': 'RightLowerArm',
        'RightLowerArm': 'LeftLowerArm',
        'LeftHand': 'RightHand',
        'RightHand': 'LeftHand'
    }

    for frame in data:
        mirrored_frame = {}
        for joint, coords in frame.items():
            if joint in joint_map:
                mirrored_frame[joint_map[joint]] = {
                    'x': -coords['x'],  # Spiegelung entlang der X-Achse
                    'y': coords['y'],
                    'z': coords['z']
                }
            else:
                mirrored_frame[joint] = coords
        mirrored_data.append(mirrored_frame)
    return mirrored_data

# Funktion zur zeitlichen Verzerrung
def temporal_warping(data, max_shift=2):
    warped_data = []
    for i in range(len(data)):
        shift = random.randint(-max_shift, max_shift)
        if 0 <= i + shift < len(data):
            warped_data.append(data[i + shift])
        else:
            warped_data.append(data[i])  # Behalte unveränderte Daten, wenn Index außerhalb des Bereichs ist
    return warped_data

# Funktion zur Kombination mehrerer Augmentierungstechniken
def combine_augmentations(data):
    augmented_data = temporal_warping(data)
    augmented_data = advanced_mirror_data(augmented_data)
    augmented_data = add_advanced_noise_and_transform(augmented_data)
    return augmented_data

# Funktion zum Erstellen einer Meta-Datei
def create_meta_file(file_path):
    guid = os.urandom(16).hex()
    meta_content = f"""fileFormatVersion: 2
guid: {guid}
TextScriptImporter:
  externalObjects: {{}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""
    meta_file_path = f"{file_path}.meta"
    with open(meta_file_path, 'w') as meta_file:
        meta_file.write(meta_content)
    print(f"Meta-Datei erstellt: {meta_file_path}")

# JSON-Dateien sammeln und höchste Nummer finden
json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
real_files = [f for f in json_files if "Synthetic" not in f]
synthetic_files = [f for f in json_files if "Synthetic" in f]

# Maximal erlaubte synthetische Dateien
max_synthetic_files = int(len(real_files) * SYNTHETIC_RATIO)
current_synthetic_count = len(synthetic_files)
remaining_synthetic_files = max_synthetic_files - current_synthetic_count

if remaining_synthetic_files <= 0:
    print("Die Anzahl synthetischer Dateien hat bereits das maximale Verhältnis erreicht.")
    exit()

print(f"Erlaubte zusätzliche synthetische Dateien: {remaining_synthetic_files}")

# Erweiterte Daten generieren
new_number = max(
    int(f.split('_')[0]) for f in json_files if f.split('_')[0].isdigit()
) + 1

for idx, json_file in enumerate(real_files, 1):
    if remaining_synthetic_files <= 0:
        break

    print(f"Verarbeite Datei {idx}/{len(real_files)}: {json_file}")

    file_path = os.path.join(DATA_DIR, json_file)
    with open(file_path, 'r') as file:
        data = json.load(file)

    print(f"Originaldaten geladen: {len(data)} Frames.")

    # Kombination der Augmentierungstechniken
    augmented_data = combine_augmentations(data)

    # Neuer Dateiname mit gewünschtem Format
    parts = json_file.split('_')
    exercise_name = parts[1]
    exercise_type = parts[2].split('.')[0]
    new_file_name = f"{new_number}_{exercise_name}_{exercise_type}_Synthetic.json"
    new_file_path = os.path.join(DATA_DIR, new_file_name)

    # Synthetische Daten speichern
    with open(new_file_path, 'w') as new_file:
        json.dump(augmented_data, new_file)
    print(f"Erweiterte Daten gespeichert: {new_file_name}")

    # Meta-Datei erstellen
    create_meta_file(new_file_path)

    # Hochzählen und verbleibende Anzahl aktualisieren
    new_number += 1
    remaining_synthetic_files -= 1
    print(f"Verbleibende synthetische Dateien: {remaining_synthetic_files}")

print("Alle synthetischen Dateien wurden erfolgreich generiert.")
