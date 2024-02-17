import time
import numpy as np
import csv

import Config
from PerformanceAnalyzer import PerformanceAnalyzer
from core.DataRecorder import DataRecorder
from core.ModelTester import ModelTester
from core.DenoiseProxy import DenoiseProxy
from core.PoseClassifier import PoseClassifier
from core.RepEvaluator import RepEvaluator
from core.StreamSegmentor import StreamSegmentor
from data.DataAccess import DataAccess
from core.ModelTrainer import ModelTrainer
from enums.ApplicationMode import ApplicationMode

class DataGateway:
    def __init__(self):
        self.streamSegmentor = StreamSegmentor()
        #self.classifier = PoseClassifier()
        #self.dataRecorder = DataRecorder()
        #self.denoiseProxy = DenoiseProxy()
        #self.repEvaluator = RepEvaluator()

    def on_training_init(self, init):
         data = init.split("_")
         self.dataRecorder = DataRecorder(data[0], data[1]);
        

    def on_imu_data_stream(self, suitData, application_mode):
        t = time.process_time()
        
        if application_mode == ApplicationMode.TRAINING:
            #Write to DataRecorder
            self.dataRecorder.log_data(suitData)
        if application_mode == ApplicationMode.TESTING:
           #Send to ModelTester
           exerciseRecognition = ModelTester.train_exercise_recognition_model(suitData)
           if exerciseRecognition != "":
               error = ModelTester.get_feedback_from_model(exerciseRecognition)
               return exerciseRecognition + "_" + error
           else: 
            return exerciseRecognition
       
        
        ##denoisedData = self.denoiseProxy.denoise(DataAccess.get_data_without_timesamp(suitData))
        #PerformanceAnalyzer.add_denoise_time_measurement(time.process_time() - t)

        #nodeData = DataAccess.get_node_data(denoisedData)
        #jointData = DataAccess.get_joint_data(denoisedData)

        #t = time.process_time()
        #exercise, _type = self.classifier.predict(nodeData)
        #PerformanceAnalyzer.add_classify_time_measurement(time.process_time() - t)

        #t = time.process_time()
        #segmentDetected = self.streamSegmentor.onNewStreamData(nodeData, exercise, _type)
        #PerformanceAnalyzer.add_segment_time_measurement(time.process_time() - t)

        #t = time.process_time()
        #if segmentDetected == "START":
        #    self.repEvaluator.repStarted(exercise, timestamp)
        #error, repEnded = self.repEvaluator.evaluate(timestamp, jointData, exercise, _type)
        #if repEnded:
        #    segmentDetected = "END"
        #error = np.insert(error, 0, suitData[0]).tolist()
        #PerformanceAnalyzer.add_evaluate_time_measurement(time.process_time() - t)

        #t = time.process_time()
        #PerformanceAnalyzer.add_log_time_measurement(time.process_time() - t)

        #return [exercise.name, error]

    def on_training_finished(self, sampleType):
        self.dataRecorder.save_data_to_csv(sampleType)
        t = time.process_time()

    def on_create_feedback_model(self, init):
        data = init.split("_")
        #TODO! retrieve training data from csv depoending on subject Ids (using regex)
        #training_data = self.dataRecorder.get_data_from_csv()
        training_data = data[0]
        ModelTrainer.train_feedback_model(training_data, data[0, data[1], data[2]])
        t = time.process_time()

    def on_testing_init(self, init):
        data = init.split("_")
        #TODO: is it "true" or "1" or 1?
        if data[1] == "true":
            self.on_create_exercise_recognition_model()
        self.modelTester = ModelTester(data[0])
        t = time.process_time()

    def on_create_exercise_recognition_model(self):
        #TODO! retrieve training data from csv depoending on (most recent?) model
        #training_data = self.dataRecorder.get_data_from_csv()
        ModelTrainer.train_feedback_model(training_data, data[0, data[1], data[2]])


    def get_recorded_data(self):
        return self.dataRecorder.dataToDataframe()

    def get_error_data(self):
        return self.dataRecorder.errorToDataframe()