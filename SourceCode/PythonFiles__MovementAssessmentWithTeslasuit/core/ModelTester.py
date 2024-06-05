import pandas as pd
import time
from sklearn import svm
from joblib import dump, load
from sklearn import svm, linear_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPClassifier
#from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support

from core.DataDenoiser import DataDenoiser
import Config
from data.DataAccess import DataAccess
from data.DataManager import DataManager
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score, LeaveOneGroupOut
import seaborn as sns
from enums.Algorithm import Algorithm
import copy
import os

pd.set_option('mode.chained_assignment', None)

class ModelTester:

    def __init__(self, model_data, feature_names):
        self.model_data = model_data
        self.feature_names = feature_names.split(",")
        self.columns = ['Timestamp', 'HumanBoneIndex_Axis', 'Error']
        self.models = {}

    def get_imu_df(self, imu_data):
        tmp = imu_data.imu_data.tolist().split(",")
        testing_data = pd.DataFrame(tmp, index=self.feature_names)
        return testing_data

    def get_exercise_recognition(self, testing_df):
        thisdir = os.getcwd()
        svc = load(thisdir + "/core/ml_models/exercise_recognition_svm_model")
        exercise_recognition = svc.predict(testing_df)
        return exercise_recognition[0]

    def load_models(self):
        thisdir = os.getcwd()
        m_set_join = "-".join(self.model_data.measurement_sets)
        files = [f for f in os.listdir(thisdir + "/core/ml_models/" + self.model_data.exercise_type + "/" + self.model_data.algorithm + "/") if self.model_data.subject_ids in f and "_" + str(self.model_data.t_gyro) + "_" in f and m_set_join in f]
        for f in files:
            hbi = f.split("_")[3]
            self.models[hbi] = load(thisdir + "/core/ml_models/" + self.model_data.exercise_type + "/" + self.model_data.algorithm + "/" + f)

    def get_feedback_from_model(self, exercise_recognition, suit_data):  
        if self.model_data.exercise_type != exercise_recognition:
            self.model_data.exercise_type = exercise_recognition
            self.load_models()

        columns = suit_data.columns
        testing_df = pd.DataFrame()
        testing_df['HumanBoneIndex_Axis'] = suit_data.columns
        testing_df['Gyro_x'] = [0]*suit_data.columns.size
        testing_df['Gyro_y'] = [0]*suit_data.columns.size
        testing_df['Gyro_z'] = [0]*suit_data.columns.size
        testing_df['Value'] = pd.to_numeric(suit_data.values[0])
        
        relative_error = []
        for humanboneIndex_name, df in testing_df.groupby(testing_df['HumanBoneIndex_Axis'].str.split("_").str[0]):
            df = df.reset_index(drop=True)
            df['HumanBoneIndex_Axis'] = df.index
            model = self.models[humanboneIndex_name]
            mean_std_df =  model.predict(df.drop(['Value'], axis=1))
            df['Mean'] = mean_std_df[:,0]
            df['Std'] = mean_std_df[:,1]
            # Calculate absolute difference, subtract standard deviation and set all negative values to zero.
            # Result: By how much is the standard deviation exceeded, i.e. how big is the error? Within std equals no error.
            df['AbsDifference'] = (df['Mean'] - df['Value']).abs()
            df['Error'] = df['AbsDifference'] - 2 * df['Std'] 
            df['FilteredError'] = df['Error'].clip(lower=0)
            # Then take all values where deviation from mean was downwards, i.e. actual smaller than mean
            # and multiply by -1. No we have positive values for upwards deviation and negative values
            # for downwards deviation.
            df.loc[df['Value'] < df['Mean']]['FilteredError'] = df.loc[df['Value'] < df['Mean']]['FilteredError'] * (-1)
            # then make the error relative. Add 0.01 to avoid division by zero
            df['RelativeError'] = df['FilteredError'] / (df['Std'] + 0.01)
            relative_error.append((humanboneIndex_name, ) + tuple(df['RelativeError'].values))
        return relative_error
     
    def test_feedback_models_on_df(self, models_for_samples_list, exercise_type, sample_df, sample_name, result, std_coeff):
        thisdir = os.getcwd()
        sample_df = sample_df.loc[:, ~sample_df.columns.str.contains("gyro")] 
        chosen_idx = np.random.choice(len(sample_df)-1, replace=False, size=250)
        for x in chosen_idx:
            print("Sample: " + sample_name + " Row: " + str(x))
            row = sample_df.iloc[x] #randomly selects a row
            testing_df = pd.DataFrame()
            testing_df['HumanBoneIndex_Axis'] = row.index
            testing_df['Gyro_x'] = [0]*row.index.size
            testing_df['Gyro_y'] = [0]*row.index.size
            testing_df['Gyro_z'] = [0]*row.index.size
            testing_df['Value'] = row.values

            testing_dfs = np.split(testing_df, np.arange(int(len(row.index)/10), len(row.index), int(len(row.index)/10)), axis=0)
        
            i = 0
            for df in testing_dfs: 
                df = df.reset_index(drop=True)
                humanboneIndex_name = df['HumanBoneIndex_Axis'].iloc[0].split('_')[0]
                i = i+1
                for model_for_sample in models_for_samples_list:
                    mod_df = copy.deepcopy(df)
                    mod_df['HumanBoneIndex_Axis'] = mod_df.index
                    if humanboneIndex_name in  model_for_sample[1]:
                        model = load(thisdir + "/core/ml_models/" + exercise_type + "/" + model_for_sample[0] + "/" + model_for_sample[1])
                        mean_std_df =  model.predict(mod_df.drop(['Value'], axis=1))
                        mod_df['Mean'] = mean_std_df[:,0]
                        mod_df['Std'] = mean_std_df[:,1]
                        # Calculate absolute difference, subtract standard deviation and set all negative values to zero.
                        # Result: By how much is the standard deviation exceeded, i.e. how big is the error? Within std equals no error.
                        mod_df['AbsDifference'] = (mod_df['Mean'] - mod_df['Value']).abs()
                        mod_df['Error'] = mod_df['AbsDifference'] - std_coeff * mod_df['Std'] 
                        mod_df['FilteredError'] = mod_df['Error'].clip(lower=0)
                        # Then take all values where deviation from mean was downwards, i.e. actual smaller than mean
                        # and multiply by -1. Now we have positive values for upwards deviation and negative values
                        # for downwards deviation.
                        mod_df.loc[mod_df['Value'] < mod_df['Mean']]['FilteredError'] = mod_df.loc[mod_df['Value'] < mod_df['Mean']]['FilteredError'] * (-1)

                        # then make the error relative. Add 0.01 to avoid division by zero
                        mod_df['RelativeError'] = mod_df['FilteredError'] / (mod_df['Std'] + 0.01)
                        no_numpy_relError = tuple(mod_df['RelativeError'].values)
                        result.append(model_for_sample + (sample_name, std_coeff, x, no_numpy_relError))
        return result  
        