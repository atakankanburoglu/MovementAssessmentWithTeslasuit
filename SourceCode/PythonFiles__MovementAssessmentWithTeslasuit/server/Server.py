import threading
import time
import zmq


class Server:
    def __init__(self, dataGateway):
        self.dataGateway = dataGateway
        self.context = zmq.Context()
        self.receive_socket = self.context.socket(zmq.SUB)
        self.receive_socket.connect("tcp://localhost:5556")
        self.receive_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.receive_socket.setsockopt(zmq.CONFLATE, 1)
        self.send_socket = self.context.socket(zmq.PUB)
        self.send_socket.bind("tcp://*:6667")

        self.queue = []
        self.thread1 = None
        self.thread2 = None
        self.threadsRunning = False

    def receive_thread(self):
        """
        Empfangsthread: Verarbeitet eingehende Nachrichten.
        """
        print("Receive Thread Started")
        while self.threadsRunning:
            # Warten auf die nächste Nachricht vom Client
            try:
                message = self.receive_socket.recv(copy=True)
                topic, payload = message.split()
                string_topic = topic.decode("utf-8")
                string_payload = payload.decode("utf-8")

                print(f"Nachricht empfangen: Topic={string_topic}, Payload={string_payload}")

                # Aufteilen der Payload und Verarbeiten der Nachricht
                string_payload_split = string_payload.split(";")
                send_data = self.dataGateway.process_received_frame(string_topic, string_payload_split[0],
                                                                    string_payload_split[1:])

                # Daten in die Warteschlange legen
                if send_data is not None:
                    self.queue.append(send_data)

            except Exception as e:
                print(f"Fehler beim Empfang der Nachricht: {e}")

        print("Receive Thread Stopped")

    def send_thread(self):
        """
        Sende-Thread: Senden von Nachrichten an den Client.
        """
        print("Send Thread Started")
        while self.threadsRunning:
            try:
                if len(self.queue) > 0:
                    result = self.queue.pop(0)
                    self.send_socket.send_string(result)
                    print(f"Daten gesendet: {result}")
                time.sleep(0.001)
            except Exception as e:
                print(f"Fehler beim Senden der Nachricht: {e}")

        print("Send Thread Stopped")

    def start(self):
        """
        Startet die Threads zum Empfangen und Senden von Nachrichten.
        """
        self.threadsRunning = True
        self.thread1 = threading.Thread(target=self.receive_thread)
        self.thread1.start()
        self.thread2 = threading.Thread(target=self.send_thread)
        self.thread2.start()

    def stop(self):
        """
        Beendet die Threads.
        """
        self.threadsRunning = False
        if self.thread1:
            self.thread1.join()
        if self.thread2:
            self.thread2.join()
