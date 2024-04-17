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
     
    def test_feedback_models_on_df(self, models_for_samples_list, sample_df, sample, result):
        
        #plot_df = pd.DataFrame()
        #plot_df['HumanBoneIndex_Axis'] = suit_data.index
        thisdir = os.getcwd()
        #files = [f for f in os.listdir(thisdir + "/core/ml_models/" + training_type + "/best/" + ax + "/") if f in model_for_samples_list]
        relevant_humanboneindexes = [m[2].split("_")[1] for m in models_for_samples_list]
        sample_df = sample_df.loc[:, sample_df.columns.str.contains("|".join(relevant_humanboneindexes))] 
        chosen_idx = np.random.choice(len(sample_df)-1, replace=False, size=60)
        for x in chosen_idx:
            print("Sample: " + sample + " Row: " + str(x))
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
                humanboneIndex_name = row.index[i].split('_')[0]
                i = i+1
                df['HumanBoneIndex_Axis'] = df.index
                #newest_model_time = 0
                #newest_model_path = ""
                for model_for_sample in models_for_samples_list:
                    model = load(thisdir + "/core/ml_models/" + model_for_sample[0] + "/best/" + model_for_sample[1] + "/" + model_for_sample[2])
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
                    if model_for_sample[2] in result:
                        result[model_for_sample[2]].append((model_for_sample[0], model_for_sample[1], sample, x, df['RelativeError'].values))
                    else:
                        result[model_for_sample[2]] = [(model_for_sample[0], model_for_sample[1], sample, x, df['RelativeError'].values)]
                    df = df.drop(['AbsDifference'], axis=1)
                    df = df.drop(['Error'], axis=1)
                    df = df.drop(['Mean'], axis=1)
                    df = df.drop(['Std'], axis=1)
                    df = df.drop(['FilteredError'], axis=1)
                    df = df.drop(['RelativeError'], axis=1)
        return result  
        