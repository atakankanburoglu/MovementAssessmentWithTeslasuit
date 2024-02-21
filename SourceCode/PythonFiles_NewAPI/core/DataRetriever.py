import pandas as pd
import os
import csv

class DataRetriever:

    def get_data_from_csv(self, subject_ids, training_type, header):
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv")]
        training_df = pd.DataFrame()
        if "-" in subject_ids:
                list_of_subjects = subject_ids.split("-");
                start = int(list_of_subjects[0])
                end = int(list_of_subjects[1])
                for id in range(start, end):
                    for f in files:
                        file_name = f.split("_")
                        if(file_name[0] == id and file_name[1] == training_type and file_name[2] == "Positive"):
                            training_df = pd.concat([training_df, self.data_to_d(thisdir + "core/samples/" + f, training_df.empty)])
        else:
             for f in files:
                        file_name = f.split("_")
                        if(file_name[0] == subject_ids and file_name[1] == training_type and file_name[2] == "Positive"):
                            training_df = pd.concat([training_df, self.data_to_df(thisdir + "/core/samples/" + f, training_df.empty)])
        return training_df

    def get_data_from_csv_for_exercise_recognition(self):
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv")]
        training_df = pd.DataFrame()
        for f in files:
            file_name = f.split("_")
            if(file_name[2] == "Positive"):
                training_df = pd.concat([training_df, self.data_to_d(thisdir + "/core/samples/" + f, training_df.empty)])
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