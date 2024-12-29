import os
import json
import random

# Dynamische Pfade basierend auf der aktuellen Position der Datei
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../UnityProject_MovementAssessmentWithTeslasuit/Assets/JsonAttempts")

# Funktion zum Hinzufügen von Rauschen zu den Features
def add_noise(data, noise_level=0.01):
    noisy_data = []
    for frame in data:
        noisy_frame = {}
        for key, value in frame.items():
            if isinstance(value, dict) and all(coord in value for coord in ['x', 'y', 'z']):
                noisy_frame[key] = {
                    'x': value['x'] + random.uniform(-noise_level, noise_level),
                    'y': value['y'] + random.uniform(-noise_level, noise_level),
                    'z': value['z'] + random.uniform(-noise_level, noise_level)
                }
            else:
                noisy_frame[key] = value  # Unveränderte Daten beibehalten
        noisy_data.append(noisy_frame)
    return noisy_data

# Funktion zum Spiegeln der Daten (z. B. links/rechts tauschen)
def mirror_data(data):
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
                mirrored_frame[joint_map[joint]] = coords
            else:
                mirrored_frame[joint] = coords
        mirrored_data.append(mirrored_frame)
    return mirrored_data

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
max_number = max(
    int(f.split('_')[0]) for f in json_files if f.split('_')[0].isdigit()
)
print(f"Gefundene JSON-Dateien: {len(json_files)} (Höchste Nummer: {max_number})\n")

# Erweiterte Daten generieren
new_number = max_number + 1
for idx, json_file in enumerate(json_files, 1):
    print(f"Verarbeite Datei {idx}/{len(json_files)}: {json_file}")

    file_path = os.path.join(DATA_DIR, json_file)
    with open(file_path, 'r') as file:
        data = json.load(file)

    print(f"Originaldaten geladen: {len(data)} Frames.")

    # Erweiterte Daten erzeugen (nur eine Art von Erweiterung pro Durchlauf)
    noisy_mirrored_data = add_noise(mirror_data(data))
    new_file_name = f"{new_number}_{'_'.join(json_file.split('_')[1:])}"
    new_file_path = os.path.join(DATA_DIR, new_file_name)

    with open(new_file_path, 'w') as new_file:
        json.dump(noisy_mirrored_data, new_file)
    print(f"Erweiterte Daten gespeichert: {new_file_name}")

    # Meta-Datei erstellen
    create_meta_file(new_file_path)

    # Hochzählen für die nächste Datei
    new_number += 1

print("Alle Dateien wurden erfolgreich verarbeitet und erweitert.")
