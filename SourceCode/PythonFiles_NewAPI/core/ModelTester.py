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

import os

pd.set_option('mode.chained_assignment', None)

class ModelTester:

    def __init__(self, subject_ids, algorithm):
        self.subject_ids = subject_ids
        self.algorithm = algorithm
    
    def get_exercise_recognition(suit_data):
        thisdir = os.getcwd()
        svc = load(thisdir + "/core/ml_models/exercise_recognition_svm_model")
        exercise_recognition = svc.predict(suit_data)
        if exercise_recognition != "":
            return exercise_recognition


    def get_feedback_from_model(exercise_recognition, suit_data):
        thisdir = os.getcwd()
        files = [f for f in os.listdir(thisdir + "/core/ml_models/")]
        newest_model_time = 0
        newest_model_path = ""
        for f in files:
            filename = f.split("_")
            if(file_name[0] == self.subject_ids and file_name[1] == exercise_recognition and file_name[2] == self.algorithm):
                if newest_model_time < int(file_name[3]):
                    newest_model_time = int(file_name[3])
                    newest_model_path = f
        model = load(newest_model_path)
        error = model.predict(suit_data)
        if error != "":
            return error
