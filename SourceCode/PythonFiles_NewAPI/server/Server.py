import threading
import time
import numpy as np
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
        print("Receive Thread Started")
        while self.threadsRunning:
            #  Wait for next request from client
            message = self.receive_socket.recv(copy=True)
            t = time.process_time()
            topic, payload = message.split()
            string_topic = str(topic, "utf-8")
            string_payload = str(payload, "utf-8")
            print(string_topic + " received")
            string_payload_split = string_payload.split(";")
            send_data = self.dataGateway.process_received_frame(string_topic, string_payload_split[0], string_payload_split[1:])
            if send_data != None:
                self.queue.append(send_data)
        print("Receive Thread Stopped")

    def send_thread(self):
        print("Send Thread Started")
        while self.threadsRunning:
            if len(self.queue) > 0:
                result = self.queue.pop(0)
                self.send_socket.send_string(result)
                print("Send data")
            time.sleep(0.001)
        print("Send Thread Stopped")

    def start(self):
        self.threadsRunning = True
        self.thread1 = threading.Thread(target=self.receive_thread)
        self.thread1.start()
        self.thread2 = threading.Thread(target=self.send_thread)
        self.thread2.start()

    def stop(self):
        self.threadsRunning = False
        self.thread1.join()
        self.thread2.join()

        





