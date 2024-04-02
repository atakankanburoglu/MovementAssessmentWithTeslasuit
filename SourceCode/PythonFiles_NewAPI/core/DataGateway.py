import time
import numpy as np
import csv
import pandas as pd
import os
import Config
from PerformanceAnalyzer import PerformanceAnalyzer
from core.DataRecorder import DataRecorder
from core.DataRetriever import DataRetriever
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
        #self.denoiseProxy = DenoiseProxy()
        #self.repEvaluator = RepEvaluator()

    def on_training_init(self, init):
         data = init.split("_")
         self.dataRecorder = DataRecorder(data[0], data[1]);
        

    def on_imu_data_stream(self, suit_data, application_mode):
        t = time.process_time()
        
        if application_mode == ApplicationMode.TRAINING:
            #Write to DataRecorder
            self.dataRecorder.log_data(suit_data)
        if application_mode == ApplicationMode.TESTING:
           #Send to ModelTester
           exercise_recognition = self.modelTester.get_exercise_recognition(suit_data)
           if exercise_recognition != None:
               error = self.modelTester.get_feedback_from_model(exercise_recognition, suit_data)
               return exercise_recognition, error
           else: 
            return exercise_recognition
       
        
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
        subject_ids = data[0].split(",");
        training_type = data[1]
        algorithm = data[2]
        training_data = DataRetriever.get_data_from_csv_for_feedback_model(subject_ids, training_type)
        feature_names = init.split(",")
        ModelTrainer.train_feedback_model(training_data, algorithm, feature_names)
        t = time.process_time()

    def on_get_exercise_list(self):
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/samples/")]
        return files

    def on_testing_init(self, init, header):
        data = init.split("_")
        if data[2] == "True":
            training_data = DataRetriever.get_data_from_csv_for_exercise_recognition()
            ModelTrainer.train_exercise_recognition_model(training_data)
        self.modelTester = ModelTester(data[0], data[1], header)
        t = time.process_time()

    def on_testing_recorded(self, subject_ids, algorithm, recorded_file_name, new_recognition_model):
        thisdir = os.getcwd()
        testing_df = pd.read_csv(thisdir + "/core/samples/" + recorded_file_name)
        if new_recognition_model == "True":
            training_data = DataRetriever.get_data_from_csv_for_exercise_recognition()
            ModelTrainer.train_exercise_recognition_model(training_data)
        self.modelTester = ModelTester(subject_ids, algorithm, testing_df.columns)
        for i in range(len(testing_df)):
            exercise_recognition, error = self.on_imu_data_stream(testing_df.loc[i], ApplicationMode.TESTING)

    def get_recorded_data(self):
        return self.dataRecorder.dataToDataframe()

    def get_error_data(self):
        return self.dataRecorder.errorToDataframe()