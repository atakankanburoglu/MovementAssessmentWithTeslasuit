import pandas as pd
import time
from sklearn import svm
from joblib import dump
from sklearn import svm, linear_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support
from sklearn.preprocessing import LabelEncoder
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

class ModelTrainer:

    @staticmethod
    def train_exercise_recognition_model(training_data):
        print("Creating Excercise Recognition Model...")
        
        training_data.drop(['Timestamp'], axis=1, inplace=True)
        
        y = training_data['TrainingType'].values
        X = training_data.drop(['TrainingType'], axis=1)

        X.fillna("0", inplace=True, axis=1)
        #print("Building SVM Model with ", len(y), " data points.")
        svc = svm.SVC()
        svc.fit(X, y)
        
        
        thisdir = os.getcwd()
        print("Dumping Excercise Recognition Model Results")
        dump(svc, thisdir + "/core/ml_models/exercise_recognition_svm_model")

    @staticmethod
    def train_feedback_model(training_data, algorithm, save_string):
        thisdir = os.getcwd()
        t = time.time()
        #Preprocessing
        #delete TrainingType, Timestamp and Spine, Chest and Left - & Rightshoulder (have no values)
        training_data.drop(['TrainingType'], axis=1, inplace=True)
        training_data.drop(['Timestamp'], axis=1, inplace=True)
        training_data = training_data.loc[:,~training_data.columns.str.startswith('Spine')]
        training_data = training_data.loc[:,~training_data.columns.str.startswith('Chest')]
        training_data = training_data.loc[:,~training_data.columns.str.startswith('LeftShoulder')]
        training_data = training_data.loc[:,~training_data.columns.str.startswith('RightShoulder')]
        #Create mean and std for every column
        mean_std_df = training_data.agg(['mean', 'std'])
        #split each HumanBoneIndex into different dfs 
        humanboneindex_dfs = np.split(training_data, np.arange(20, len(training_data.columns), 20), axis=1)
        #per HumanBoneIndex_df split all columns and find only unique values
        for humanboneindex in humanboneindex_dfs:
            #create empty training df per humanboneindex to fill
            training_df = pd.DataFrame(columns=['HumanBoneIndex_Axis', 'Value', 'Mean', 'Std'])
            humanboneIndex_name = []
            humanboneindex_axis_dfs = np.split(humanboneindex, np.arange(1, len(humanboneindex.columns), 1), axis=1)
            a = 0
            for axis in  humanboneindex_axis_dfs:
                a = a + 1
                humanboneIndex_name = axis.columns[0].split('_')
                #round to 5 decimals places
                axis = axis.round(5)
                axis = axis.drop_duplicates()
                #add each unique value with axis name, value, mean and std to final training_df
                for i in range(len(axis)):
                    #axis_name = axis.columns[0]
                    #value = axis.iloc[i][0]
                    mean = mean_std_df.loc['mean'][axis.columns[0]]
                    std = mean_std_df.loc['std'][axis.columns[0]]
                    training_df.loc[len(training_df)] = {'HumanBoneIndex_Axis':a, 'Value': axis.iloc[i][0], 'Mean': mean_std_df.loc['mean'][axis.columns[0]], 'Std': mean_std_df.loc['std'][axis.columns[0]]}    
            X = training_df.loc[:, 'HumanBoneIndex_Axis':'Value']
            X.fillna("0", inplace=True, axis=1)
            Y = training_df.loc[:, 'Mean':'Std']
            if(algorithm == "LR"):
                lr = linear_model.LinearRegression()
                lr.fit(X, Y)
                print("Dumping LR Model Results")
                dump(lr, thisdir + "/core/ml_models/" + save_string[0] + "_" + humanboneIndex_name[0] + "_" + str(int(t)))
            if(algorithm == "RF"):
                rf = RandomForestRegressor(max_depth=2, random_state=0)
                rf.fit(X, Y)
                print("Dumping RF Model Results")
                dump(rf, thisdir + "/core/ml_models/" + save_string[0] + "_" + humanboneIndex_name[0] + "_" + str(int(t)))
            if(algorithm == "NN"):
                nn = MLPRegressor()
                nn.fit(X, Y)
                print("Dumping NN Model Results")
                dump(nn, thisdir + "/core/ml_models/" + save_string[0] + "_" + humanboneIndex_name[0] + "_" + str(int(t)))
        print("Model creation (in min):" + str((time.time() - t)/60))