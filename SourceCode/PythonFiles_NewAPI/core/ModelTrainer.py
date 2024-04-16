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
import seaborn as sns
from enums.Algorithm import Algorithm
from core.DataDenoiser import DataDenoiser
import os

pd.set_option('mode.chained_assignment', None)

class ModelTrainer:

    @staticmethod
    def train_exercise_recognition_model(training_data):
        print("Creating Excercise Recognition Model...")
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
    def train_feedback_model(training_dict, subject_ids, training_type, algorithm):
        thisdir = os.getcwd()
        t = time.time()
        model_creation_dict = {}
        for humanboneindex_name, training_df in training_dict.items():
            X = training_df.loc[:, 'HumanBoneIndex_Axis':'Gyro_z']
            X.fillna("0", inplace=True, axis=1)
            Y = training_df.loc[:, 'Mean':'Std']
            if(algorithm == "LR"):
                lr = linear_model.LinearRegression()
                lr.fit(X, Y)
                print("Dumping LR Model Results for humanboneindex: " + humanboneindex_name)
                dump(lr, thisdir + "/core/ml_models/" + training_type + "/" + algorithm + "/no_magn9x/" + subject_ids + "_" + humanboneindex_name + "_" + str(int(t)))
            if(algorithm == "RF"):
                rf = RandomForestRegressor(max_depth=2, random_state=0)
                rf.fit(X, Y)
                print("Dumping RF Model Results for humanboneindex: " + humanboneindex_name)
                dump(rf, thisdir + "/core/ml_models/" + training_type + "/" + algorithm + "/no_magn9x/" + subject_ids + "_" + humanboneindex_name + "_" + str(int(t)))
            if(algorithm == "NN"):
                nn = MLPRegressor(random_state=0, max_iter=2000)
                nn.fit(X, Y)
                print("Dumping NN Model Results for humanboneindex: " + humanboneindex_name)
                dump(nn, thisdir + "/core/ml_models/" + training_type + "/" + algorithm + "/no_magn9x/" + subject_ids + "_" + humanboneindex_name + "_" + str(int(t)))
            model_creation_dict[humanboneindex_name] = (time.time() - t)/60
        print("Model creation (in min):" + str((time.time() - t)/60))
        return str(int(t)), model_creation_dict