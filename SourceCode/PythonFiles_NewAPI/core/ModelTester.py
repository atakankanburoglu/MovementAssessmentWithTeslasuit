import pandas as pd
import time
from sklearn import svm
from joblib import dump, load
from sklearn import svm, linear_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPClassifier
#from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support

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
        #testing_data.apply(lambda x: x.str.replace('"', ""))
        #for col in testing_data.columns:
            #testing_data[col] = testing_data[col].astype(float)

        thisdir = os.getcwd()
        svc = load(thisdir + "/core/ml_models/exercise_recognition_svm_model")
        exercise_recognition = svc.predict(testing_data)

        return exercise_recognition[0]


    def get_feedback_from_model(self, exercise_recognition, suit_data):  
        tmp = suit_data['Timestamp']
        #delete empty columns
        suit_data.drop(['TrainingType'], axis=0, inplace=True)
        suit_data.drop(['Timestamp'], axis=0, inplace=True)
        suit_data = suit_data.loc[~suit_data.index.str.startswith('Spine')]
        suit_data = suit_data.loc[~suit_data.index.str.startswith('Chest')]
        suit_data = suit_data.loc[~suit_data.index.str.startswith('LeftShoulder')]
        suit_data = suit_data.loc[~suit_data.index.str.startswith('RightShoulder')]
        
        plot_df = pd.DataFrame()
        plot_df['HumanBoneIndex_Axis'] = suit_data.index
        plot_df['Timestamp'] = tmp
        
        testing_df = pd.DataFrame(columns = ['HumanBoneIndex_Axis', 'Value'])
        testing_df['HumanBoneIndex_Axis'] = suit_data.index
        testing_df['Value'] = suit_data.values
        testing_dfs = np.split(testing_df, np.arange(20, len(testing_df), 20), axis=0)
        
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/ml_models/")]
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
            model = load(thisdir + "/core/ml_models/" + newest_model_path)
            mean_std_df =  model.predict(df)
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
        self.relative_errors = pd.concat((self.relative_errors, plot_df), axis=0)
        
    def plot_feedback_result(self, filename):
        self.relative_errors.to_csv("C:/Users/Camil/Documents/Uni/Master/Thesis/Code/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles_NewAPI/core/analysis/" + filename + "relative_errors.csv")
        print(self.relative_errors)
        self.relative_errors['label'] = pd.cut(self.relative_errors['Error'],bins=[-100, -10, -1, 1, 10, 100], labels=['Big Minus Error', 'Minus Error', 'No Error', 'Error', 'Big Error'])
        print(self.relative_errors)
        d = self.relative_errors.groupby(['HumanBoneIndex_Axis','label'])['Timestamp'].size().unstack()
        d.plot(kind='bar',stacked=True, title = "Test")
        plt.show()