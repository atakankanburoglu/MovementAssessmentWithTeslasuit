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

        # delete TrainingType 
        training_data.drop(['TrainingType'], axis=1, inplace=True)
        
        y = training_data['Timestamp']
        X = training_data.drop(['Timestamp'], axis=1) 

        X.fillna("0", inplace=True, axis=1)

        if(algorithm == "LR"):
            lr = linear_model.LinearRegression()
            lr.fit(X, y)
            print("Dumping LR Model Results")
            dump(lr, thisdir + "/core/ml_models/" + save_string + "_" + str(int(t)))
        if(algorithm == "RF"):
            rf = RandomForestRegressor(max_depth=2, random_state=0)
            rf.fit(X, y)
            print("Dumping RF Model Results")
            dump(rf, thisdir + "/core/ml_models/" + save_string + "_" + str(int(t)))
        if(algorithm == "NN"):
            nn = MLPRegressor()
            nn.fit(X, y)
            print("Dumping NN Model Results")
            dump(nn, thisdir + "/core/ml_models/" + save_string + "_" + str(int(t)))
