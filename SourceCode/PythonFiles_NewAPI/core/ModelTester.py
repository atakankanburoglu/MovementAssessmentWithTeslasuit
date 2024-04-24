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

    def __init__(self, subject_ids, algorithm, feature_names):
        self.subject_ids = subject_ids
        self.algorithm = algorithm
        self.feature_names = feature_names
        self.relative_errors = pd.DataFrame(columns = ['Timestamp', 'HumanBoneIndex_Axis', 'Error'])
    
    def get_exercise_recognition(self, suit_data):
        tmp = []
        tmp.append(suit_data.tolist())
        testing_data = pd.DataFrame(tmp, columns=self.feature_names)
        testing_data.drop(['TrainingType'], axis=1, inplace=True) 
        testing_data = testing_data.drop(['Timestamp'], axis=1)
        thisdir = os.getcwd()
        svc = load(thisdir + "/core/ml_models/exercise_recognition_svm_model")
        exercise_recognition = svc.predict(testing_data)
        return exercise_recognition[0]


    def get_feedback_from_model(self, exercise_recognition, suit_data):  
        plot_df = pd.DataFrame()
        plot_df['HumanBoneIndex_Axis'] = suit_data.index
        
        testing_df = pd.DataFrame()
        testing_df['HumanBoneIndex_Axis'] = suit_data.index
        testing_df['Gyro_x'] = [0]*suit_data.index.size
        testing_df['Gyro_y'] = [0]*suit_data.index.size
        testing_df['Gyro_z'] = [0]*suit_data.index.size
        testing_df['Value'] = suit_data.values
        testing_dfs = np.split(testing_df, np.arange(int(len(suit_data.index)/10), len(suit_data.index), int(len(suit_data.index)/10)), axis=0)
        
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/ml_models/" + exercise_recognition + "/" + self.algorithm + "/")]
        relative_error = []
        i = 0
        for df in testing_dfs: 
            df = df.reset_index(drop=True)
            humanboneIndex_name = suit_data.index[i].split('_')[0]
            i = i+1
            df['HumanBoneIndex_Axis'] = df.index
            newest_model_time = 0
            newest_model_path = ""
            for f in files:
                file_name = f.split("_") #TODO: has to match subject ids perfectly?
                if(file_name[0] == self.subject_ids and file_name[1] == exercise_recognition and file_name[2] == self.algorithm and file_name[3] == humanboneIndex_name):
                    if newest_model_time < int(file_name[4]):
                        newest_model_time = int(file_name[4])
                        newest_model_path = f
            model = load(thisdir + "/core/ml_models/" + exercise_recognition + "/" + self.algorithm + "/" + newest_model_path)
            mean_std_df =  model.predict(df.drop(['Value'], axis=1))
            df['Mean'] = mean_std_df[:,0]
            df['Std'] = mean_std_df[:,1]
            # Calculate absolute difference, subtract standard deviation and set all negative values to zero.
            # Result: By how much is the standard deviation exceeded, i.e. how big is the error? Within std equals no error.
            df['AbsDifference'] = (df['Mean'] - df['Value']).abs()
            df['Error'] = df['AbsDifference'] - Config.STD_MULTIPLIER * df['Std'] 
            df['FilteredError'] = df['Error'].clip(lower=0)
            # Then take all values where deviation from mean was downwards, i.e. actual smaller than mean
            # and multiply by -1. No we have positive values for upwards deviation and negative values
            # for downwards deviation.
            df.loc[df['Value'] < df['Mean']]['FilteredError'] = df.loc[df['Value'] < df['Mean']]['FilteredError'] * (-1)

            # then make the error relative. Add 0.01 to avoid division by zero
            df['RelativeError'] = df['FilteredError'] / (df['Std'] + 0.01)
            relative_error.extend(df['RelativeError'].values)
        plot_df['Error'] = relative_error
        plot_df['Timestamp'] = int(time.time())
        self.relative_errors = pd.concat((self.relative_errors, plot_df), axis=0)
     
    def test_feedback_models_on_df(self, models_for_samples_list, training_type, sample_df, sample_name, result):
        
        #plot_df = pd.DataFrame()
        #plot_df['HumanBoneIndex_Axis'] = suit_data.index
        thisdir = os.getcwd()
        #files = [f for f in os.listdir(thisdir + "/core/ml_models/" + training_type + "/best/" + ax + "/") if f in model_for_samples_list]
        relevant_humanboneindexes = list(dict.fromkeys([m[5] for m in models_for_samples_list]))
        sample_df = sample_df.loc[:, sample_df.columns.str.contains("|".join(relevant_humanboneindexes))] 
        sample_df = sample_df.loc[:, ~sample_df.columns.str.contains("gyro")] 
        chosen_idx = np.random.choice(len(sample_df)-1, replace=False, size=500)
        for x in chosen_idx:
            print("Sample: " + sample_name + " Row: " + str(x))
            row = sample_df.iloc[x] #randomly selects a row
            testing_df = pd.DataFrame()
            testing_df['HumanBoneIndex_Axis'] = row.index
            testing_df['Gyro_x'] = [0]*row.index.size
            testing_df['Gyro_y'] = [0]*row.index.size
            testing_df['Gyro_z'] = [0]*row.index.size
            testing_df['Value'] = row.values

            testing_dfs = np.split(testing_df, np.arange(int(len(row.index)/len(relevant_humanboneindexes)), len(row.index), int(len(row.index)/len(relevant_humanboneindexes))), axis=0)
        
            
            #relative_error = []
            i = 0
            for df in testing_dfs: 
                df = df.reset_index(drop=True)
                humanboneIndex_name = df['HumanBoneIndex_Axis'].iloc[0].split('_')[0]
                i = i+1
                #newest_model_time = 0
                #newest_model_path = ""
                for model_for_sample in models_for_samples_list:
                    if "all_ax" in model_for_sample[4]:
                        ax = "all_axis"
                    else:
                        ax = model_for_sample[4][:-1]
                    model_file_name = [f for f in os.listdir(thisdir + "/core/ml_models/" + training_type + "/" + model_for_sample[3] + "/" + ax + "/") if model_for_sample[5] in f and "1-14-" + model_for_sample[0] == f.split("_")[0]][-1]  
                    mod_df = copy.deepcopy(df)
                    if "no_magn_" in model_for_sample[4]:
                        mod_df = mod_df.loc[~mod_df['HumanBoneIndex_Axis'].str.contains("magn")]
                    if "no_magn9x" in model_for_sample[4]:
                        mod_df = mod_df.loc[~mod_df['HumanBoneIndex_Axis'].str.contains("magn")]
                        mod_df = mod_df.loc[~mod_df['HumanBoneIndex_Axis'].str.contains("9x")]
                    mod_df['HumanBoneIndex_Axis'] = mod_df.index
                    if humanboneIndex_name in  model_file_name:
                        model = load(thisdir + "/core/ml_models/" + training_type + "/" + model_for_sample[3] + "/" + ax + "/" + model_file_name)
                        mean_std_df =  model.predict(mod_df.drop(['Value'], axis=1))
                        mod_df['Mean'] = mean_std_df[:,0]
                        mod_df['Std'] = mean_std_df[:,1]
                        # Calculate absolute difference, subtract standard deviation and set all negative values to zero.
                        # Result: By how much is the standard deviation exceeded, i.e. how big is the error? Within std equals no error.
                        mod_df['AbsDifference'] = (mod_df['Mean'] - mod_df['Value']).abs()
                        mod_df['Error'] = mod_df['AbsDifference'] - Config.STD_MULTIPLIER * mod_df['Std'] 
                        mod_df['FilteredError'] = mod_df['Error'].clip(lower=0)
                        # Then take all values where deviation from mean was downwards, i.e. actual smaller than mean
                        # and multiply by -1. No we have positive values for upwards deviation and negative values
                        # for downwards deviation.
                        mod_df.loc[mod_df['Value'] < mod_df['Mean']]['FilteredError'] = mod_df.loc[mod_df['Value'] < mod_df['Mean']]['FilteredError'] * (-1)

                        # then make the error relative. Add 0.01 to avoid division by zero
                        mod_df['RelativeError'] = mod_df['FilteredError'] / (mod_df['Std'] + 0.01)
                        no_numpy_relError = tuple(mod_df['RelativeError'].values)
                        if model_file_name in result:
                            result[model_file_name].append((sample_name, x, no_numpy_relError))
                        else:
                            result[model_file_name] = [(sample_name, x, no_numpy_relError)]
              
        return result  
        