import pandas as pd
from sklearn import svm
from joblib import dump
from sklearn import svm, linear_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPClassifier
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

pd.set_option('mode.chained_assignment', None)

class ModelTrainer:

    @staticmethod
    def train_exercise_recognition_model(training_data):
        print("Creating Excercise Recognition Model...")
        #TODO: how should this look?
        X = training_data.x.tolist()
        Y = training_data.y

        print("Building SVM Model with ", len(Y), " data points.")
        supportVectorMachine = svm.SVC()
        supportVectorMachine.fit(X, Y)
        
        t = time.time()
        print("Dumping Excercise Recognition Model Results")
        dump(supportVectorMachine, "../core/ml-models/svm_model" + str(int(t)))

    @staticmethod
    def train_feedback_model(training_data, algorithm, save_string):
        # delete timestamp for now (but not from training file)
        training_data.drop('TrainingType', axis=1, inplace=True)

        x = training_data.drop('Timestamp', axis=1).values
        #x.columns = x.columns.astype(str)
        y = training_data['Timestamp'].values
        y = LabelEncoder().fit_transform(y)

        if(algorithm == "LR"):
            lr = linear_model.LinearRegression()
            lr.fit(x, y)
            print("Dumping LR Model Results")
            dump(lr, "../core/ml-models/" + save_string + "_lr_model")
        if(algorithm == "RF"):
            rf = RandomForestRegressor(max_depth=2, random_state=0)
            rf.fit(x, y)
            print("Dumping RF Model Results")
            dump(rf, "../core/ml-models/" + save_string + "_rf_model")
        if(algorithm == "NN"):
            nn = MLPClassifier()
            nn.fit(x, y)
            print("Dumping NN Model Results")
            dump(regr, "../core/ml-models/" + save_string + "_nn_model")
