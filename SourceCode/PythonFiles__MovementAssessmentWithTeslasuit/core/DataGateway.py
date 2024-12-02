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
from Feedback import Feedback


class DataGateway:
    def __init__(self):
        # Feedback-System initialisieren
        model_path = "/Users/mac113/Desktop/Personal/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles__MovementAssessmentWithTeslasuit/model/SVM_model.pkl"  # Absoluter Pfad zum Modell
        self.feedback = Feedback(model_path)

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
                model_data = ModelData(payload[0], "", payload[2], 5, payload[3], 0)
                self.modelTester = ModelTester(model_data, payload[4])
            if state == "RUNNING":
                imu_data = ImuData(payload[0][1], np.array(payload[0][2:]), payload[0][0])
                return "RelativeError " + str(self.on_imu_data_stream(imu_data, topic))
            if state == "RECORDED":
                thisdir = os.getcwd()
                filename = payload[4].split("_")
                model_data = ModelData("1-14-"+filename[0], "", payload[2], 10, payload[3], 0)
                self.on_testing_recorded(model_data, f)

        # Neu hinzugefügtes Topic: Feedback
        if topic == "Feedback":
            return self.process_feedback_request(payload)

    def process_feedback_request(self, payload):
        """
        Verarbeitet Feedback-Anfragen basierend auf IMU-Daten.
        """
        print("Feedback-Anfrage erhalten...")

        imu_data = {
            'replayPosition': payload  # Angenommen, das Payload enthält die Positionsdaten
        }

        # Feedback-Logik aufrufen
        misalignment_detected, misaligned_joints = self.feedback.detect_misalignment(imu_data)
        feedback_message = self.feedback.generate_feedback_message(misaligned_joints)

        print(f"Feedback-Nachricht: {feedback_message}")
        return feedback_message

    def on_imu_data_stream(self, imu_data, application_mode):
        if application_mode == "Recording":
            self.dataRecorder.log_data(imu_data)
        if application_mode == "Testing":
            testing_df = self.modelTester.get_imu_df(imu_data)
            ex_df = DataDenoiser.denoise_df_for_exercise_recognition_model_testing(copy.deepcopy(testing_df))
            exercise_recognition = self.modelTester.get_exercise_recognition(ex_df.T)
            testing_df = DataDenoiser.denoise_df_column_for_feedback_model_testing(testing_df, self.modelTester.model_data.measurement_sets)
            if exercise_recognition != None:
                error = self.modelTester.get_feedback_from_model(exercise_recognition, testing_df.T)
                directions = ModelEvaluator.error_to_direction(self.modelTester.model_data, error)
                return exercise_recognition + " " + directions + " " + feedback_message  # Append feedback
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
                for a in ["NN", "RF", "LR"]:
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
