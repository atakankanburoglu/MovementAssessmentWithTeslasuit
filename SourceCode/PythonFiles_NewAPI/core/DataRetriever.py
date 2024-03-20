import pandas as pd
import os
import csv
import shutil
import glob

class DataRetriever:

    @staticmethod
    def get_data_from_csv_for_feedback_model(subject_ids, training_type):
        training_data = pd.DataFrame()
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv")]
        for ids in subject_ids:
            if "-" in ids:
                list_of_subjects = ids.split("-");
                start = int(list_of_subjects[0])
                end = int(list_of_subjects[1])
                for id in range(start, end):
                    for f in files:
                        file_name = f.split("_")
                        if(file_name[0] == str(id) and file_name[1] == training_type and file_name[2] == "Positive"):
                            df = pd.read_csv(thisdir + "/core/samples/" + f)
                            training_data = pd.concat((df, training_data), axis=0)
            else:
                for f in files:
                        file_name = f.split("_")
                        if(file_name[0] == ids and file_name[1] == training_type and file_name[2] == "Positive"):
                            df = pd.read_csv(thisdir + "/core/samples/" + f)
                            training_data = pd.concat((df, training_data), axis=0)
        return training_data

    @staticmethod
    def get_data_from_csv_for_exercise_recognition():
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv")]
        training_data = pd.DataFrame()
        for f in files:
            file_name = f.split("_")
            if(file_name[2] == "Positive"):
                df = pd.read_csv(thisdir + "/core/samples/" + f)
                training_data = pd.concat((df, training_data), axis=0)
        return training_data
