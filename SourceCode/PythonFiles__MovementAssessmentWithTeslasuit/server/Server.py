import socket
import threading
import json
import time
from core.Feedback import Feedback
import os

class Server:
    def __init__(self, dataGateway, host='127.0.0.1', port=6667, model_base_path='SourceCode/PythonFiles__MovementAssessmentWithTeslasuit/model'):
        self.dataGateway = dataGateway
        self.host = host
        self.port = port
        self.model_base_path = model_base_path
        self.feedback = None  # Feedback wird dynamisch initialisiert
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server gestartet auf {self.host}:{self.port}")
        self.threadsRunning = True

    def handle_client(self, client_socket, addr):
        print(f"Verbindung hergestellt mit {addr}")
        buffer = ""
        last_processed_time = time.time()
        processing_interval = 0.1  # 10 Hz

        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                buffer += data.decode("utf-8")

                if "\nEND_OF_JSON\n" in buffer:
                    json_data, buffer = buffer.split("\nEND_OF_JSON\n", 1)
                    data_list = json.loads(json_data)

                    for data in data_list:
                        if time.time() - last_processed_time >= processing_interval:
                            self.process_data(data, client_socket)
                            last_processed_time = time.time()
        except Exception as e:
            print(f"Fehler: {e}")
        finally:
            client_socket.close()

    def process_data(self, data, client_socket):
        try:
            exercise_type = data.get("exerciseType", "")
            model_name = data.get("model", "")

            # Dynamischen Modellpfad bestimmen
            model_path = os.path.join(self.model_base_path, exercise_type, f"{model_name}_model.pkl")

            if not os.path.exists(model_path):
                error_message = f"Modell nicht gefunden: {model_path}"
                print(error_message)
                client_socket.sendall(error_message.encode("utf-8"))
                return

            # Feedback-Instanz mit dem richtigen Modell initialisieren
            self.feedback = Feedback(model_path)
            misalignment_status = self.feedback.detect_misalignment(data)  # Fehlstellung prüfen
            deviations = self.feedback.detect_deviations(data)  # Liefert detaillierte Abweichungen

            # Deviation-Daten zusammenstellen
            deviation_messages = []
            for joint, deviation in deviations.items():
                deviation_messages.append({
                    "joint": joint,
                    "deviation": deviation["vector"],
                    "intensity": deviation["intensity"]
                })

            # Rückmeldung erstellen
            response = {
                "misalignmentStatus": misalignment_status,
                "deviations": deviation_messages
            }
            client_socket.sendall((json.dumps(response) + "\nEND_OF_JSON\n").encode("utf-8"))
        except Exception as e:
            error_message = f"Fehler beim Verarbeiten der Daten: {e}"
            print(error_message)
            client_socket.sendall(error_message.encode("utf-8"))

    def start(self):
        while self.threadsRunning:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()
            except Exception as e:
                print(f"Fehler beim Akzeptieren der Verbindung: {e}")

    def stop(self):
        self.threadsRunning = False
        self.server_socket.close()
        print("Server gestoppt.")
