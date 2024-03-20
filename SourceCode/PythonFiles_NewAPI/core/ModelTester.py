import pandas as pd
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
        self.feature_names = feature_names.split(",")
    
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
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/ml_models/")]
        newest_model_time = 0
        newest_model_path = ""
        for f in files:
            file_name = f.split("_") #TODO: has to match subject ids perfectly?
            if(file_name[0] == self.subject_ids and file_name[1] == exercise_recognition and file_name[2] == self.algorithm):
                if newest_model_time < int(file_name[3]):
                    newest_model_time = int(file_name[3])
                    newest_model_path = f
        model = load(thisdir + "/core/ml_models/" + newest_model_path)

        tmp = []
        tmp.append(suit_data.tolist())
        data = pd.DataFrame(tmp, columns=self.feature_names)
        data.drop(['TrainingType'], axis=1) 
        testing_data = data['Timestamp'].values
        testing_data = testing_data.reshape(-1, 1) 
        mean = model.predict(testing_data)
        std = np.std(mean, axis=0)

        # Calculate absolute difference, subtract standard deviation and set all negative values to zero.
        # Result: By how much is the standard deviation exceeded, i.e. how big is the error? Within std equals no error.
        difference = mean - data
        absDiff = abs(difference)
        error = absDiff - std


        # Then take all values where deviation from mean was downwards, i.e. actual smaller than mean
        # and multiply by -1. No we have positive values for upwards deviation and negative values
        # for downwards deviation.
        error[data < mean] = error[data < mean] * (-1)

        # then make the error relative. Add 0.01 to avoid division by zero
        relativeError = error / (std + 0.01)

        return relativeError
