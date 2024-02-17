import threading
import time
import numpy as np
import zmq

from PerformanceAnalyzer import PerformanceAnalyzer
from enums.ApplicationMode import ApplicationMode

class Server:
    def __init__(self, dataGateway):
        self.dataGateway = dataGateway
        self.context = zmq.Context()
        self.receive_socket = self.context.socket(zmq.SUB)
        self.receive_socket.connect("tcp://localhost:5555")
        self.receive_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.receive_socket.setsockopt(zmq.CONFLATE, 1)
        self.send_socket = self.context.socket(zmq.PUB)
        self.send_socket.bind("tcp://*:6666")

        self.queue = []
        self.thread1 = None
        self.thread2 = None
        self.threadsRunning = False

        self.applicationMode = ApplicationMode.IDLE

    def receive_thread(self):
        print("Receive Thread Started")
        while self.threadsRunning:
            #  Wait for next request from client
            message = self.receive_socket.recv(copy=True)
            t = time.process_time()
            topic, payload = message.split()
            
            string_topic = str(topic, "utf-8")

            print(string_topic + " received")

            if(string_topic == "ImuDataStream" and (self.applicationMode == ApplicationMode.TRAINING or self.applicationMode == ApplicationMode.TESTING)):
                stringPayload = str(payload, "utf-8")
                data = stringPayload.split(";")
                try:
                    row = np.array(data)
                    self.dataGateway.on_imu_data_stream(row, self.applicationMode)
                except:
                    print("Count not process ImuDataStream: ", data)
            if(string_topic == "TrainingMode"):
                stringPayload = str(payload, "utf-8")
                data = stringPayload.split(";")
                if(data[0] == "INIT"):
                    self.dataGateway.on_training_init(data[1])
                    self.applicationMode = ApplicationMode.TRAINING                
                if(data[0] == "FINISHED"):
                    self.dataGateway.on_training_finished(data[1])
                    self.applicationMode = ApplicationMode.IDLE  
            if(string_topic == "CreateModel"):
                stringPayload = str(payload, "utf-8")
                data = stringPayload.split(";")
                self.dataGateway.on_create_feedback_model(data)
                self.applicationMode = ApplicationMode.MODELCREATION            
            if(string_topic == "TestingMode"):
                stringPayload = str(payload, "utf-8")
                data = stringPayload.split(";")
                if(data[0] == "INIT"):
                    self.thread2 = threading.Thread(target=self.send_thread)
                    self.thread2.start()
                    self.dataGateway.on_testing_init(data[1], )
                    self.applicationMode = ApplicationMode.TESTING                
                if(data[0] == "FINISHED"):
                    self.thread2.stop();
                    self.applicationMode = ApplicationMode.IDLE  

            
            #self.send_socket.send_string("ErrorResponseStream true")
           # 
                #
#                print("ImuDataStream received")
               # self.pushResult(self, "Data sent back")
           # except:
               # print("Count not process: ", message)
            PerformanceAnalyzer.add_read_data_time_measurement(time.process_time() - t)

            #error = 





            #name = error[0]
            #errorData = error[1]
            #csvString = ",".join(["%f" % num for num in errorData])
            #csvString = name + "," + csvString
            #self.send_socket.send_string("ErrorResponseStream " + csvString)




            # self.pushResult(error)
            PerformanceAnalyzer.add_total_time_measurement(time.process_time() - t)
            # time.sleep(0.001)
        print("Receive Thread Stopped")

    def send_thread(self):
        print("Send Thread Started")
        while self.threadsRunning:
            if len(self.queue) > 0:
                name_error = self.queue.pop(0)
                #name = name_error[0]
                #errorData = name_error[1]
                #csvString = ",".join(["%f" % num for num in errorData])
                #csvString = name + ","+csvString
                self.send_socket.send_string("ErrorResponseStream " + name_error)
            time.sleep(0.001)
        print("Send Thread Stopped")

    def start(self):
        self.threadsRunning = True
        self.thread1 = threading.Thread(target=self.receive_thread)
        self.thread1.start()

        

    def stop(self):
        self.threadsRunning = False
        self.thread1.join()
        self.thread2.join()

    def pushResult(self, name_error):
        self.queue.append(name_error)





