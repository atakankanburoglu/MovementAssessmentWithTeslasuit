import pandas as pd
import os
import csv
import shutil
import glob

class DataRetriever:

    @staticmethod
    def get_data_from_csv_for_feedback_model(subject_ids, training_type):
        training_dict = {}
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
                        if(file_name[0] == str(id) and file_name[1] == training_type and file_name[2] == "Positive"):
                            df = pd.read_csv(thisdir + "/core/samples/" + f)
                            if id in training_dict:
                                training_dict[str(id)].append(df)
                            else:
                                training_dict[str(id)] = [df]
                            
            else:
                for f in files:
                        file_name = f.split("_")
                        if(file_name[0] == ids and file_name[1] == training_type and file_name[2] == "Positive"):
                            df = pd.read_csv(thisdir + "/core/samples/" + f)
                            if id in training_dict:
                                training_dict[str(id)].append(df)
                            else:
                                training_dict[str(id)] = [df]
        return training_dict

    @staticmethod
    def get_data_from_csv_for_exercise_recognition():
        training_data = []
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv")]
        for f in files:
            file_name = f.split("_")
            if(file_name[2] == "Positive"):
                if training_data.empty:
                    training_data = pd.read_csv(thisdir + "/core/samples/" + f)
                else:  
                    df = pd.read_csv(thisdir + "/core/samples/" + f, header = 0)
                    training_data = pd.concat((pos_data, df), axis=0) 
        return training_data
