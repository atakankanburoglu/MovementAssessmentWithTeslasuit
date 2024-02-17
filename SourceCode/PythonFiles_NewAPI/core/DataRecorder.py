import pandas as pd

import os
import Config
import time
from Plotter import Plotter
from data.DataAccess import DataAccess
import csv

class DataRecorder:
    def __init__(self, subjectId, trainingType):
        self.subjectId = subjectId
        self.trainingType = trainingType
        self.recordedData = []
        self.recordedSegments = []
        #self.plotter = Plotter()

    def log_data(self, suit_data):
        self.recordedData.append(suit_data)

    def save_data_to_csv(self, sampleType):
        t = time.time()
        with open("core/samples/" + self.subjectId + '_' + self.trainingType +'_' + sampleType +'_' + str(int(t)) + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for row in self.recordedData:
                writer.writerow(row)

    def get_data_from_csv(self, subject_ids, training_type, header):
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "core/samples/") if f.endswith(".csv")]
        training_df = pd.DataFrame()
        if "-" in subject_ids:
                list_of_subjects = data[0].split("-");
                start = int(list_of_subjects[0])
                end = int(list_of_subjects[1])
                for id in range(start, end):
                    for f in files:
                        file_name = f.split("_")
                        if(file_name[0] == id and file_name[1] == training_type and file_name[2] == "Positive"):
                            training_df.append(data_to_df(thisdir + "core/samples/" + f, header))
        else:
             for f in files:
                        file_name = f.split("_")
                        if(file_name[0] == id and file_name[1] == training_type and file_name[2] == "Positive"):
                            training_df.append(data_to_df(thisdir + "core/samples/" + f, header))
        return training_df

    def get_data_from_csv_for_exercise_recognition(self):
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "core/samples/") if f.endswith(".csv")]
        training_df = pd.DataFrame()
        for f in files:
            file_name = f.split("_")
            if(file_name[2] == "Positive"):
                training_df.append(data_to_df(thisdir + "core/samples/" + f, training_df.empty))
        return training_df

    def data_to_df(self, path, header):
        if(header):
            return pd.read_csv(path)
        else:
            return pd.read_csv(path, header=None)
        return dataFrame

    #def errorToDataframe(self):
    #    columns = ["timestamp"]
    #    columns.extend(DataAccess.get_joints_properties_names(Config.streamedJoints))
    #    dataFrame = pd.DataFrame(self.recordedErrors, columns=columns)
    #    return dataFrame