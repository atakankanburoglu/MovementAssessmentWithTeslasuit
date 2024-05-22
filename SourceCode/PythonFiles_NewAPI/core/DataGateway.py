import time
import numpy as np
import csv
import pandas as pd
import os
import ast
import copy
from core.DataRecorder import DataRecorder
from core.DataRetriever import DataRetriever
from core.DataPreprocessor import DataPreprocessor
from core.DataDenoiser import DataDenoiser
from core.ModelTester import ModelTester
from core.ModelTrainer import ModelTrainer
from core.ModelEvaluator import ModelEvaluator
from core.ModelValidator import ModelValidator
from enums.ApplicationMode import ApplicationMode
from core.ImuData import ImuData
from core.SampleData import SampleData
from core.ModelData import ModelData

class DataGateway:
    def process_received_frame(self, topic, state, payload):
        if topic == "Recording":
            if state == "INIT":
                self.dataRecorder = DataRecorder(payload)
            if state == "RUNNING":
                data = payload.split(",")
                imu_data = ImuData(data[1], np.array(data[2:]), data[0])
                self.on_imu_data_stream(self, imu_data, topic)
            if state == "FINISHED":
                sample_data = SampleData(payload[0], payload[1], payload[2])
                self.dataRecorder.save_data_to_csv(sample_data)
        if topic == "Training":
            if payload[1] == "ALL" and payload[2] != "SVM":
                for e in ["SIDEPLANKLEFT"]: #"FULLSQUAT", "PLANKHOLD", "SIDEPLANKRIGHT", 
                    for m in [ "6x,magn", "9x,magn", "magn,Accel", "magn,accel"]: #"magn", "9x", "6x", "accel", "Accel", "accel,Accel",
                        for t_g in [5, 10]:
                            t = time.time()
                            model_data = ModelData(payload[0], e, payload[2], t_g, m, t)
                            self.on_train_model(model_data, payload[4])
            else:
                t = time.time()
                model_data = ModelData(payload[0], payload[1], payload[2], 5, payload[3], t)
                self.on_train_model(model_data, payload[4])
        if topic == "Testing":
            if state == "IDLE":
                return "ExerciseList " + ','.join(DataRetriever.on_get_exercise_list())
            if state == "INIT":
                model_data = ModelData(payload[0], payload[1], payload[2], 5, payload[3], t)
                self.modelTester = ModelTester(model_data, payload[4])
            if state == "RUNNING":
                data = payload.split(",")
                imu_data = ImuData(data[1], np.array(payload[2:]), data[0])
                return "RelativeError " + self.on_imu_data_stream(self, imu_data, topic)
            if state == "RECORDED":
                #self.on_testing_recorded_sideplankleft()
                #self.on_testing_recorded_sideplankright()
                #self.on_testing_recorded_fullsquat()
                #self.on_testing_recorded_plankhold()
                #self.on_testing_recorded_all()#model_data, )
                for e in [("SIDEPLANKLEFT", "7", "NN", 10), ("SIDEPLANKLEFT", "7", "RF", 10)]: #["FULLSQUAT", "PLANKHOLD"]: [("FULLSQUAT", "14", "RF", 5), ("FULLSQUAT", "14", "RF", 10), ("PLANKHOLD", "9", "RF", 10), ("PLANKHOLD", "9", "RF", 5), ("SIDEPLANKLEFT", "14", "NN", 10), ("SIDEPLANKLEFT", "14", "RF", 10), ("SIDEPLANKRIGHT", "7", "NN", 5), ("SIDEPLANKRIGHT", "7", "RF", 5), ("SIDEPLANKRIGHT", "9", "NN", 5), ("SIDEPLANKRIGHT", "10", "NN", 5), ("SIDEPLANKRIGHT", "10", "RF", 5), ("SIDEPLANKRIGHT", "14", "RF", 5)]
                    thisdir = os.getcwd()
                    files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") if e[0] in f and e[1] + "_" in f and "Negative" in f]
                    for f in files:
                        filename = f.split("_")
                        model_data = ModelData("1-14-"+filename[0], "", e[2], e[3], payload[3], 0)
                        self.on_testing_recorded(model_data, f)
                            #model_data = ModelData(payload[0], "", payload[2], t_g, payload[3], 0)
                            #self.on_testing_recorded(model_data, payload[4])
                #for t_g in [5, 10]: 
                #            
        
    def on_imu_data_stream(self, imu_data, application_mode):
        if application_mode == "Recording":
            self.dataRecorder.log_data(imu_data)
        if application_mode == "Testing":
            testing_df = self.modelTester.get_imu_df(imu_data)
            ex_df = DataDenoiser.denoise_df_for_exercise_recognition_model_testing(copy.deepcopy(testing_df))
            exercise_recognition = self.modelTester.get_exercise_recognition(ex_df)
            testing_df = DataDenoiser.denoise_df_column_for_feedback_model_testing(testing_df, self.modelTester.model_data.measurement_sets)
            if exercise_recognition != None:
               error = self.modelTester.get_feedback_from_model(exercise_recognition, testing_df)
               return exercise_recognition, error
            else: 
                return exercise_recognition

    def on_train_model(self, model_data, validate):
        if model_data.algorithm == "SVM":
            training_data = DataRetriever.get_data_from_csv_for_exercise_recognition()
            training_data = DataDenoiser.denoise_df_for_exercise_recognition_model_training(training_data)
            ModelTrainer.train_exercise_recognition_model(training_data)
        else:
            id_training_dict = DataRetriever.get_data_from_csv_for_feedback_model(model_data.subject_ids, model_data.exercise_type)
            if model_data.algorithm == "ALL":
                for a in ["NN", "RF"]:
                    model_data.algorithm = a
                    if validate == "True":
                        self.on_validate(model_data, id_training_dict)
                    else:
                        self.on_train(model_data, id_training_dict) 
            else:
                if validate == "True":
                    self.on_validate(model_data, id_training_dict)
                else:
                    self.on_train(model_data, id_training_dict)      
    
    def on_validate(self, model_data, id_training_dict):
        score_dict = {}
        for leave_one_out_id, df in id_training_dict.items():
            training_dict, validation_dict = DataPreprocessor.preprocess_data_for_feedback_model(id_training_dict, leave_one_out_id, model_data.measurement_sets, model_data.t_gyro)
            ids_split = model_data.subject_ids.split("-")
            if len(ids_split) > 2:
                model_data.subject_ids = "-".join(ids_split[:-1])
            model_data.subject_ids = model_data.subject_ids + "-" + str(leave_one_out_id)
            ModelTrainer.train_feedback_model(training_dict, model_data) 
            score_dict = ModelValidator.validate_feedback_model(validation_dict, model_data, score_dict, leave_one_out_id)
        ModelValidator.plot_score_dict(score_dict, model_data)

    def on_train(self, model_data, id_training_dict):
        training_dict, validation_dict = DataPreprocessor.preprocess_data_for_feedback_model(id_training_dict, 0, model_data.measurement_sets)
        ModelTrainer.train_feedback_model(training_dict, model_data, []) 

    def on_testing_recorded(self, model_data, recorded_file_name):
        testing_df = DataRetriever.get_data_from_recorded_sample(recorded_file_name)
        self.modelTester = ModelTester(model_data, testing_df.columns)
        t = time.time()
        relative_errors = []
        for i in range(500):
            ex_er = self.on_imu_data_stream(testing_df.loc[i], "Testing")
            relative_errors.append((ex_er[0], i, ex_er[1]))
            print("Row " + str(i) + " tested")
        print("File tested for (in min):" + str((time.time() - t)/60))    
        ModelEvaluator.plot_feedback_result_heatmaps(model_data, relative_errors)
        return relative_errors

    def on_testing_recorded_fullsquat(self):
        thisdir = os.getcwd()
        model_list = []
        for exercise_type in ["FULLSQUAT"]:
            time_taken = []
            for id in ["1", "10", "14", "7", "8", "9"]:
                sample_list = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and id + "_" in f and exercise_type in f]
                for m in ["_accel_", "_Accel_"]:
                    models_for_samples_list = [("RF", f) for f in os.listdir(thisdir + "/core/ml_models/" + exercise_type + "/RF/") if "1-14-" + id + "_" in f and m in f and "_1_" in f]
                    for sample in sample_list:
                        result = []
                        sample_name = sample.split("_")[0] + "_" + sample.split("_")[2] + "_" + sample.split("_")[3]
                        sample_df = pd.read_csv(thisdir + "/core/samples/" + sample)
                        model_data = ModelData("", "", "", "", "", 0)
                        self.modelTester = ModelTester(model_data, sample_df.columns)
                        fulllsquat_accel_df = DataDenoiser.denoise_df_column_for_feedback_model_training(sample_df, [m[1:-1]])
                        for std_coeff in [2]:
                            t = time.time()
                            self.modelTester.test_feedback_models_on_df(models_for_samples_list, exercise_type, fulllsquat_accel_df, sample_name, result, std_coeff)
                            print(len(result))
                            print("File tested for (in min):" + str((time.time() - t)/60))    
                        file_error = open(thisdir + "/core/analysis/evaluation/" + exercise_type + "/" + sample + "_best_models_error_calculated.txt", "w") 
                        file_error.write(str(result) + ",")
                        file_error.close()


    def on_testing_recorded_plankhold(self):
        thisdir = os.getcwd()
        model_list = []
        for exercise_type in ["PLANKHOLD"]:
            time_taken = []
            for id in ["10", "14", "7", "8", "9"]:#"1", 
                sample_list = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and id + "_" in f and exercise_type in f]
                models_for_samples_list = []
                for a in ["RF", "NN"]:
                    models_for_samples_list.extend([(a, f) for f in os.listdir(thisdir + "/core/ml_models/" + exercise_type + "/" + a + "/") if "1-14-" + id + "_" in f and "accel-Accel" in f])
                for sample in sample_list:
                    sample_name = sample.split("_")[0] + "_" + sample.split("_")[2] + "_" + sample.split("_")[3]
                    result = []
                    sample_df = pd.read_csv(thisdir + "/core/samples/" + sample)
                    model_data = ModelData("", "", "", "", "", 0)
                    self.modelTester = ModelTester(model_data, sample_df.columns)
                    plankhold_accel_accel = DataDenoiser.denoise_df_column_for_feedback_model(sample_df, ["accel","Accel"])
                    for std_coeff in [2]:
                        t = time.time()
                        self.modelTester.test_feedback_models_on_df(models_for_samples_list, exercise_type, plankhold_accel_accel, sample_name, result, std_coeff)
                        print(len(result))
                        print("File tested for (in min):" + str((time.time() - t)/60))    
                    file_error = open(thisdir + "/core/analysis/evaluation/" + exercise_type + "/" + sample + "_best_models_error_calculated_gyro_not_null.txt", "w") 
                    file_error.write(str(result) + ",")
                    file_error.close()

    def on_testing_recorded_sideplankright(self):
        thisdir = os.getcwd()
        model_list = []
        for exercise_type in ["SIDEPLANKRIGHT"]:
            time_taken = []
            for id in ["1", "10", "14", "7", "8", "9"]:
                sample_list = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and id + "_" in f and exercise_type in f]
                models_for_samples_list = []
                models_for_samples_list.extend([("RF", f) for f in os.listdir(thisdir + "/core/ml_models/" + exercise_type + "/RF/") if "1-14-" + id + "_" in f and "accel-Accel" in f and "_1_" in f])
                models_for_samples_list.extend([("NN", f) for f in os.listdir(thisdir + "/core/ml_models/" + exercise_type + "/NN/") if "1-14-" + id + "_" in f and "accel-Accel" in f and "_5_" in f])
                for sample in sample_list:
                    sample_name = sample.split("_")[0] + "_" + sample.split("_")[2] + "_" + sample.split("_")[3]
                    result = []
                    sample_df = pd.read_csv(thisdir + "/core/samples/" + sample)
                    model_data = ModelData("", "", "", "", "", 0)
                    self.modelTester = ModelTester(model_data, sample_df.columns)
                    plankhold_accel_accel = DataDenoiser.denoise_df_column_for_feedback_model(sample_df, ["accel","Accel"])
                    for std_coeff in [2]:
                        t = time.time()
                        self.modelTester.test_feedback_models_on_df(models_for_samples_list, exercise_type, plankhold_accel_accel, sample_name, result, std_coeff)
                        print(len(result))
                        print("File tested for (in min):" + str((time.time() - t)/60))    
                    file_error = open(thisdir + "/core/analysis/evaluation/" + exercise_type + "/" + sample + "_best_models_error_calculated_gyro_not_null.txt", "w") 
                    file_error.write(str(result) + ",")
                    file_error.close()

    def on_testing_recorded_sideplankleft(self):
            thisdir = os.getcwd()
            model_list = []
            for exercise_type in ["SIDEPLANKLEFT"]:
                time_taken = []
                for id in ["1", "10", "14", "7", "8", "9"]:
                    sample_list = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and id + "_" in f and exercise_type in f]
                    models_for_samples_list = []
                    for a in ["RF", "NN"]:
                        models_for_samples_list.extend([(a, f) for f in os.listdir(thisdir + "/core/ml_models/" + exercise_type + "/" + a + "/") if "1-14-" + id + "_" in f and "accel-Accel" in f])
                    for sample in sample_list:
                        sample_name = sample.split("_")[0] + "_" + sample.split("_")[2] + "_" + sample.split("_")[3]
                        result = []
                        sample_df = pd.read_csv(thisdir + "/core/samples/" + sample)
                        model_data = ModelData("", "", "", "", "", 0)
                        self.modelTester = ModelTester(model_data, sample_df.columns)
                        plankhold_accel_accel = DataDenoiser.denoise_df_column_for_feedback_model(sample_df, ["accel","Accel"])
                        for std_coeff in [2]:
                            t = time.time()
                            self.modelTester.test_feedback_models_on_df(models_for_samples_list, exercise_type, plankhold_accel_accel, sample_name, result, std_coeff)
                            print(len(result))
                            print("File tested for (in min):" + str((time.time() - t)/60))    
                        file_error = open(thisdir + "/core/analysis/evaluation/" + exercise_type + "/" + sample + "_best_models_error_calculated_gyro_not_null.txt", "w") 
                        file_error.write(str(result) + ",")
                        file_error.close()
   