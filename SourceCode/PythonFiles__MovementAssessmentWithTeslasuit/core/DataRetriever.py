import pandas as pd
import os
import csv
import shutil
import glob

class DataRetriever:

    @staticmethod
    def get_data_from_csv_for_feedback_model(subject_ids, exercise_type):
        ID_dict = {}
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv")]
        subject_id_lst = subject_ids.split(",")
        for ids in subject_id_lst:
            if "-" in ids:
                list_of_subjects = ids.split("-");
                start = int(list_of_subjects[0])
                end = int(list_of_subjects[1])
                for id in range(start, end+1):
                    for f in files:
                        file_name = f.split("_")
                        if(file_name[0] == str(id) and file_name[1] == exercise_type and file_name[2] == "Positive"):
                            df = pd.read_csv(thisdir + "/core/samples/" + f)
                            if id in ID_dict:
                                ID_dict[str(id)].append(df)
                            else:
                                ID_dict[str(id)] = [df]
                            
            else:
                for f in files:
                        file_name = f.split("_")
                        if(file_name[0] == ids and file_name[1] == exercise_type and file_name[2] == "Positive"):
                            df = pd.read_csv(thisdir + "/core/samples/" + f)
                            if id in ID_dict:
                                ID_dict[str(id)].append(df)
                            else:
                                ID_dict[str(id)] = [df]
        return ID_dict

    @staticmethod
    def get_data_from_csv_for_exercise_recognition():
        training_data = pd.DataFrame()
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv")]
        for f in files:
            file_name = f.split("_")
            if(file_name[2] == "Positive"):
                if training_data.empty:
                    training_data = pd.read_csv(thisdir + "/core/samples/" + f)
                else:  
                    df = pd.read_csv(thisdir + "/core/samples/" + f, header = 0)
                    training_data = pd.concat((training_data, df), axis=0) 
        return training_data

    @staticmethod
    def get_data_from_recorded_sample(recorded_file_name):
        thisdir = os.getcwd()
        df = pd.read_csv(thisdir + "/core/samples/" + recorded_file_name)
        return df
    
    @staticmethod
    def on_get_exercise_list():
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/samples/")]
        return files
