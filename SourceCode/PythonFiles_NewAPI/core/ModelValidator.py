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
from sklearn.metrics import f1_score, accuracy_score
from joblib import load

pd.set_option('mode.chained_assignment', None)

class ModelValidator:

    @staticmethod
    def validate_feedback_model(validation_dict, subject_ids, training_type, algorithm, t, score_dict, leave_one_out_id, model_creation_dict):
        thisdir = os.getcwd()
        for humanboneindex_name, validation_df in validation_dict.items():
            model = load(thisdir + "/core/ml_models/" + training_type + "/" + algorithm + "/no_magn9x/" + subject_ids + "_" + humanboneindex_name + "_" + t)
            X = validation_df.loc[:, 'HumanBoneIndex_Axis':'Gyro_z']
            X.fillna("0", inplace=True, axis=1)
            Y = validation_df.loc[:, 'Mean':'Std']
            score = model.score(X, Y)
            if humanboneindex_name in score_dict:
                score_dict[humanboneindex_name].append((leave_one_out_id, score, model_creation_dict[humanboneindex_name]))
            else:
                score_dict[humanboneindex_name] = [(leave_one_out_id, score, model_creation_dict[humanboneindex_name])]
        return score_dict
    
    @staticmethod
    def plot_score_dict(score_dict, training_type, algorithm):
        for humanboneindex_name, score in score_dict.items():
            thisdir = os.getcwd()
            x = [t[0] for t in score]
            y = [t[1] for t in score]
            plt.plot(x, y, label=humanboneindex_name)
        plt.legend()
        plt.savefig(thisdir + "/core/analysis/scores/" + training_type + "_" + algorithm + "_scores_no_magn9x" + "_" + str(int(time.time())) + ".png")     
        plt.clf()
        f = open(thisdir + "/core/analysis/scores/" + training_type + "_" + algorithm + "_scores" + "_values_no_magn9x_" + str(int(time.time())) + ".txt", "w")
        f.write("This is the score_dict of: " + training_type + "_" + algorithm + "_" + str(int(time.time())) + "\n" + str(score_dict))
        f.close()

        print("Scores plotted")