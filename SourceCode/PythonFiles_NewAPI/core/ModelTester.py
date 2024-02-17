import pandas as pd
from sklearn import svm
from joblib import dump
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

pd.set_option('mode.chained_assignment', None)

class ModelTester:

    @staticmethod
    def train_exercise_recognition_model(training_data):
        print("Creating Excercise Recognition Model...")

        X = training_data.drop(["label"], axis=1)
        Y = strippedData["label"]

        print("Building SVM Model with ", len(Y), " data points.")
        supportVectorMachine = svm.SVC()
        supportVectorMachine.fit(X, Y)

        print("Dumping Excercise Recognition Model Results")
        dump(supportVectorMachine, "../core/ml-models/svm_model")

    @staticmethod
    def train_feedback_model(training_data, subject_ids, training_type, algorithm):
        save_string = subject_ids + training_type
        X = training_data.drop(["label"], axis=1)
        Y = training_data["label"]
        if(algorithm == Algorithm.LR):
            lr = linear_model.LinearRegression()
            lr.fit(X, Y)
            print("Dumping LR Model Results")
            dump(lr, "../core/ml-models/" + save_string + "_lr_model")
        if(algorithm == Algorithm.RF):
            rf = RandomForestRegressor(max_depth=2, random_state=0)
            rf.fit(X, Y)
            print("Dumping RF Model Results")
            dump(rf, "../core/ml-models/" + save_string + "_rf_model")
        if(algorithm == Algorithm.NN):
            nn = MLPClassifier()
            nn.fit(X, Y)
            print("Dumping NN Model Results")
            dump(regr, "../core/ml-models/" + save_string + "_nn_model")
