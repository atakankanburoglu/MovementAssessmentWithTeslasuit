import time
import numpy as np
import csv
import pandas as pd
import os
import Config
from PerformanceAnalyzer import PerformanceAnalyzer
from core.DataRecorder import DataRecorder
from core.DataRetriever import DataRetriever
from core.DataPreprocessor import DataPreprocessor
from core.DataDenoiser import DataDenoiser
from core.ModelTester import ModelTester
from core.PoseClassifier import PoseClassifier
from core.RepEvaluator import RepEvaluator
from core.StreamSegmentor import StreamSegmentor
from data.DataAccess import DataAccess
from core.ModelTrainer import ModelTrainer
from core.ModelEvaluator import ModelEvaluator
from core.ModelValidator import ModelValidator
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
           suit_data = DataDenoiser.denoise_df_index(suit_data)
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

    def on_create_feedback_model(self, subject_ids, training_type, algorithm, validate):
        id_training_dict = DataRetriever.get_data_from_csv_for_feedback_model(subject_ids, training_type)
        if validate == "True":
            score_dict = {}
            for leave_one_out_id, df in id_training_dict.items():
                training_dict, validation_dict = DataPreprocessor.preprocess_data_for_feedback_model(id_training_dict, leave_one_out_id)
                t, model_creation_dict = ModelTrainer.train_feedback_model(training_dict, subject_ids + "-" + str(leave_one_out_id), training_type, algorithm) 
                score_dict = ModelValidator.validate_feedback_model(validation_dict, subject_ids + "-" + str(leave_one_out_id), training_type, algorithm, t, score_dict, leave_one_out_id, model_creation_dict)
            ModelValidator.plot_score_dict(score_dict, training_type, algorithm)
        else:
            training_dict, validation_dict = DataPreprocessor.preprocess_data_for_feedback_model(id_training_dict, 0)
            ModelTrainer.train_feedback_model(training_dict, subject_ids, training_type, algorithm, [])      

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
        testing_df = pd.read_csv(thisdir + "/core/samples/" + recorded_file_name)
        if new_recognition_model == "True":
            training_data = DataRetriever.get_data_from_csv_for_exercise_recognition()
            training_data = DataDenoiser.denoise_df_column_for_exercise_recognition_model(training_data)
            ModelTrainer.train_exercise_recognition_model(training_data)
        self.modelTester = ModelTester(subject_ids, algorithm, testing_df.columns)
        t = time.time()
        rows = 500
        for i in range(rows):
            self.on_imu_data_stream(testing_df.loc[i], ApplicationMode.TESTING)
        print("File tested for (in min):" + str((time.time() - t)/60))    
        ModelEvaluator.plot_feedback_result_heatmaps(self.modelTester.relative_errors, subject_ids, recorded_file_name.split("_")[1], algorithm, t)
        #self.modelTester.plot_feedback_result_barcharts(self.modelTester.relative_errors, recorded_file_name, rows)
        return self.modelTester.relative_errors

    def on_testing_recorded_all(self):
        thisdir = os.getcwd()
        model_list = []
        training_type_list = ["PLANKHOLD", "FULLSQUAT", "SIDEPLANKRIGHT", "SIDEPLANKLEFT"]
        for training_type in training_type_list:
            axis_list = ["all_ax", "no_magn_", "no_magn9x"]
            for ax in axis_list:
                model_list.extend([(training_type, ax, f) for f in os.listdir(thisdir + "/core/ml_models/" + training_type + "/best/" + ax + "/") if f.startswith("1-14")])
        id_list = list(dict.fromkeys([(t[2].split("_")[0]).split("-")[2] + "_" for t in model_list]))
        for id in id_list:
            sample_list = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and id in f and training_type in f][:2]
            models_for_samples_list = [m for m in model_list if id in m[2]]
            for sample in sample_list:
                result = {}
                sample_df = pd.read_csv(thisdir + "/core/samples/" + sample)
                self.modelTester = ModelTester(id, "NN", sample_df.columns)
                t = time.time()
                result = self.modelTester.test_feedback_models_on_df(models_for_samples_list, sample_df, sample, result)
                print("File tested for (in min):" + str((time.time() - t)/60))    
                f = open(thisdir + "/core/analysis/relative_errors/" + sample + "_best_models.txt", "w") 
                f.write(str(result) + "\n")
                f.write("Time taken: " + str((time.time() - t)/60))
                f.close()
                        #ModelEvaluator.plot_feedback_result_heatmaps(self.modelTester.relative_errors, subject_ids, training_type, algorithm, t)
        #self.modelTester.plot_feedback_result_barcharts(self.modelTester.relative_errors, recorded_file_name, rows)
        return self.modelTester.relative_errors

    def get_recorded_data(self):
        return self.dataRecorder.dataToDataframe()

    def get_error_data(self):
        return self.dataRecorder.errorToDataframe()