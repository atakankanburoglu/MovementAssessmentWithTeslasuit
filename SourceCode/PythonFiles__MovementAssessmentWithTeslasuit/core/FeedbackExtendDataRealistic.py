import os
import json
import numpy as np
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../../UnityProject_MovementAssessmentWithTeslasuit/Assets/JsonAttempts")

SYNTHETIC_RATIO = 0.5

# Beispiel für "große Gelenke" wie gehabt
LARGE_JOINTS = {
    "Hips", "Spine", "Chest", "LeftUpperLeg", "RightUpperLeg",
    "LeftLowerLeg", "RightLowerLeg", "LeftShoulder", "RightShoulder"
}
SMALL_JOINT_NOISE_FACTOR = 0.5  # Nur halbes Noise-Level bei kleineren Gelenken

# -------------------------------------------------------------------
# NEUE FUNKTION (Beispiel):
# Optional: Anatomische "Klippen" für Gelenkpositionen/Rotationen,
# um zu große Abweichungen zu verhindern.
# Hier nur Dummy-Beispiel: Begrenze x,y,z auf +/- 2.0 (o.Ä.)
# -------------------------------------------------------------------
def clip_joint_angles(coords, limit=2.0):
    """
    Clipt (x,y,z) auf [-limit, limit].
    Hier könntest du anatomisch klippen oder komplexere Checks machen.
    """
    return np.clip(coords, -limit, limit)

# -------------------------------------------------------------------
# Beispiel-Funktion: Parameter pro Übungstyp
# (Hier nur minimal angedeutet, du könntest es ausbauen.)
# -------------------------------------------------------------------
def get_exercise_params(exercise_type, is_positive):
    """
    Gibt unterschiedliche Augmentierungswerte je nach Übung und Label zurück.
    z.B. Für 'Plank' kleine Rotationen, für 'SidePlank' etwas größere usw.
    is_positive: wenn True -> Geringere Variation (damit Pose nicht "zu" falsch wird)
    """
    if exercise_type.lower() == "plank":
        # Plank: Weniger Variation
        if is_positive:
            return {
                "base_noise_level": 0.03,
                "rotation_range_frame": (-5, 5),
                "scale_range": (0.95, 1.05)
            }
        else:
            # Negative Plank darf etwas mehr Variation haben
            return {
                "base_noise_level": 0.05,
                "rotation_range_frame": (-10, 10),
                "scale_range": (0.9, 1.1)
            }
    elif exercise_type.lower() == "sideplank":
        # Etwas größere Variationen, nur Beispiel
        return {
            "base_noise_level": 0.06,
            "rotation_range_frame": (-15, 15),
            "scale_range": (0.9, 1.15)
        }
    else:
        # Default
        return {
            "base_noise_level": 0.05,
            "rotation_range_frame": (-10, 10),
            "scale_range": (0.9, 1.1)
        }


def rotate_entire_dataset(data, rotation_range=(-10, 10)):
    """
    Rotiert die gesamte Pose um EINEN Zufallswinkel (pro Achse).
    """
    rx = np.radians(random.uniform(*rotation_range))
    ry = np.radians(random.uniform(*rotation_range))
    rz = np.radians(random.uniform(*rotation_range))

    rotation_x = np.array([
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx),  np.cos(rx)]
    ])
    rotation_y = np.array([
        [np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry), 0, np.cos(ry)]
    ])
    rotation_z = np.array([
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz),  np.cos(rz), 0],
        [0, 0, 1]
    ])
    full_rot = rotation_x @ rotation_y @ rotation_z

    rotated = []
    for frame in data:
        new_frame = {}
        for key, value in frame.items():
            if (isinstance(value, dict) and 
                all(coord in value for coord in ['x','y','z'])):
                vec = np.array([value['x'], value['y'], value['z']])
                vec = full_rot @ vec
                # OPTIONAL: anatomisch clippen
                vec = clip_joint_angles(vec)
                new_frame[key] = {'x': vec[0], 'y': vec[1], 'z': vec[2]}
            else:
                new_frame[key] = value
        rotated.append(new_frame)
    return rotated

# -------------------------------------------------------------------
# ÄNDERUNG: Nutzt Normalverteilung statt Uniform
# -------------------------------------------------------------------
def add_advanced_noise_and_transform(
    data,
    base_noise_level=0.05,
    scale_range=(0.8, 1.2),
    rotation_range=(-15, 15),
    per_frame_rotation=True
):
    """
    Fügt Positionsrauschen, Skalierung und Rotation hinzu.
    """
    noisy_data = []
    
    for frame in data:
        noisy_frame = {}
        for key, value in frame.items():
            if isinstance(value, dict) and all(coord in value for coord in ['x','y','z']):
                coords = np.array([value['x'], value['y'], value['z']])
                
                # Großes / kleines Gelenk -> unterschiedliches Rauschen
                if key in LARGE_JOINTS:
                    noise_level = base_noise_level
                else:
                    noise_level = base_noise_level * SMALL_JOINT_NOISE_FACTOR

                # NEU: Normalverteilung (mean=0, std=noise_level)
                noise = np.random.normal(0, noise_level, size=3)
                coords += noise

                if per_frame_rotation:
                    angles = np.radians(np.random.uniform(*rotation_range, size=3))
                    rotation_x = np.array([
                        [1, 0, 0],
                        [0, np.cos(angles[0]), -np.sin(angles[0])],
                        [0, np.sin(angles[0]),  np.cos(angles[0])]
                    ])
                    rotation_y = np.array([
                        [np.cos(angles[1]), 0, np.sin(angles[1])],
                        [0, 1, 0],
                        [-np.sin(angles[1]), 0, np.cos(angles[1])]
                    ])
                    rotation_z = np.array([
                        [np.cos(angles[2]), -np.sin(angles[2]), 0],
                        [np.sin(angles[2]),  np.cos(angles[2]), 0],
                        [0, 0, 1]
                    ])
                    coords = rotation_x @ coords
                    coords = rotation_y @ coords
                    coords = rotation_z @ coords

                # Leichte anisotrope Verzerrung
                distortion = np.random.uniform(0.95, 1.05, size=3)
                coords *= distortion

                # Gleichmäßige Gesamt-Skalierung
                scale_factor = np.random.uniform(*scale_range)
                coords *= scale_factor

                # OPTIONAL: anatomisch clippen
                coords = clip_joint_angles(coords)

                noisy_frame[key] = {'x': coords[0], 'y': coords[1], 'z': coords[2]}
            else:
                noisy_frame[key] = value
        noisy_data.append(noisy_frame)

    return noisy_data

def advanced_mirror_data(data):
    """
    Spiegelt den Datensatz an der X-Achse (links <-> rechts).
    """
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
            if isinstance(coords, dict) and all(k in coords for k in ['x','y','z']):
                new_joint = joint_map[joint] if joint in joint_map else joint
                mirrored_frame[new_joint] = {
                    'x': -coords['x'],  # Spiegelung an x-Achse
                    'y': coords['y'],
                    'z': coords['z']
                }
            else:
                mirrored_frame[joint] = coords
        mirrored_data.append(mirrored_frame)
    return mirrored_data

def temporal_warping(data, max_shift=2):
    """
    Verschiebt einzelne Frames in der Zeit (Index).
    """
    warped_data = []
    length = len(data)
    for i in range(length):
        shift = random.randint(-max_shift, max_shift)
        idx = i + shift
        if 0 <= idx < length:
            warped_data.append(data[idx])
        else:
            warped_data.append(data[i])
    return warped_data

def combine_augmentations(data, exercise_type="Unknown", is_positive=True):
    """
    Führt Augmentierung mit Zufallswahrscheinlichkeiten aus,
    um mehr Variation zu bekommen.
    """
    # Kopie
    aug_data = data[:]

    # Hole je nach Übung/Label die Parameter
    params = get_exercise_params(exercise_type, is_positive)

    # Zeitverzerrung mit 50 % Chance
    if random.random() < 0.5:
        aug_data = temporal_warping(aug_data, max_shift=2)
    
    # Spiegeln mit 70 % Chance
    if random.random() < 0.7:
        aug_data = advanced_mirror_data(aug_data)
    
    # 50 % Chance, dataset-weit zu rotieren
    dataset_rotate = (random.random() < 0.5)
    
    if dataset_rotate:
        # Erst dataset-weit rotieren
        aug_data = rotate_entire_dataset(aug_data, rotation_range=(-10,10))
        # Dann Noise/Skalierung pro Frame, ohne per-frame Rotation
        aug_data = add_advanced_noise_and_transform(
            aug_data,
            base_noise_level=params["base_noise_level"],
            scale_range=params["scale_range"],
            rotation_range=(-5,5),
            per_frame_rotation=False
        )
    else:
        # Kompletter Weg: Rauschen + pro Frame Rotation
        aug_data = add_advanced_noise_and_transform(
            aug_data,
            base_noise_level=params["base_noise_level"],
            scale_range=params["scale_range"],
            rotation_range=params["rotation_range_frame"],
            per_frame_rotation=True
        )
    
    return aug_data

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

def main():
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    real_files = [f for f in json_files if "Synthetic" not in f]
    synthetic_files = [f for f in json_files if "Synthetic" in f]

    max_synthetic_files = int(len(real_files) * SYNTHETIC_RATIO)
    current_synthetic_count = len(synthetic_files)
    remaining_synthetic_files = max_synthetic_files - current_synthetic_count

    if remaining_synthetic_files <= 0:
        print("Max. Anzahl synthetischer Dateien bereits erreicht.")
        return

    max_number = 0
    for f in json_files:
        parts = f.split('_')
        if parts[0].isdigit():
            val = int(parts[0])
            if val > max_number:
                max_number = val
    new_number = max_number + 1

    for idx, json_file in enumerate(real_files, 1):
        if remaining_synthetic_files <= 0:
            break

        file_path = os.path.join(DATA_DIR, json_file)
        with open(file_path, 'r') as file:
            data = json.load(file)

        parts = json_file.split('_')
        if len(parts) < 3:
            exercise_name = "EXERCISE"
            exercise_type = "Positive"
        else:
            exercise_name = parts[1]
            exercise_type = parts[2].replace(".json","")

        # Einfacher Check: Ist es "Positive" oder "Negative"?
        is_pos = (exercise_type.lower() == "positive")

        print(f"[{idx}/{len(real_files)}] {json_file} -> Erzeuge Synthetic...")
        augmented_data = combine_augmentations(
            data,
            exercise_type=exercise_name,
            is_positive=is_pos
        )

        new_file_name = f"{new_number}_{exercise_name}_{exercise_type}_Synthetic.json"
        new_file_path = os.path.join(DATA_DIR, new_file_name)

        with open(new_file_path, 'w') as new_file:
            json.dump(augmented_data, new_file)
        create_meta_file(new_file_path)

        new_number += 1
        remaining_synthetic_files -= 1
        print(f"  -> Synthetische Datei: {new_file_name}")
        print(f"  -> Noch erlaubt: {remaining_synthetic_files}")

    print("Fertig - alle synthetischen Dateien erzeugt.")

if __name__ == "__main__":
    main()
