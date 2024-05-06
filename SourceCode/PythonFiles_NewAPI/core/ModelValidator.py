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
    def validate_feedback_model(validation_dict, model_data, score_dict, leave_one_out_id):
        thisdir = os.getcwd()
        for humanboneindex_name, validation_df in validation_dict.items():
            model = load(thisdir + "/core/ml_models/" + model_data.exercise_type + "/" + model_data.algorithm + "/" + model_data.subject_ids + "_" + "-".join(model_data.measurement_sets) + "_" + str(model_data.t_gyro) + "_" + humanboneindex_name + "_" + model_data.timestamp)
            X = validation_df.loc[:, 'HumanBoneIndex_Axis':'Gyro_z']
            X.fillna("0", inplace=True, axis=1)
            Y = validation_df.loc[:, 'Mean':'Std']
            score = model.score(X, Y)
            if humanboneindex_name in score_dict:
                score_dict[humanboneindex_name].append((leave_one_out_id, score))
            else:
                score_dict[humanboneindex_name] = [(leave_one_out_id, score)]
        return score_dict
    
    @staticmethod
    def plot_score_dict(score_dict, model_data):
        for humanboneindex_name, score in score_dict.items():
            thisdir = os.getcwd()
            x = [t[0] for t in score]
            y = [t[1] for t in score]
            plt.plot(x, y, label=humanboneindex_name)
        plt.legend()
        plt.savefig(thisdir + "/core/analysis/validation/" + model_data.exercise_type + "_" + model_data.algorithm + "_scores_" + "-".join(model_data.measurement_sets) + "_" + str(model_data.t_gyro) + "_" + model_data.timestamp + ".png")     
        plt.clf()
        f = open(thisdir + "/core/analysis/validation/" + model_data.exercise_type + "_" + model_data.algorithm + "_scores_values_new_" + "-".join(model_data.measurement_sets) + "_" + str(model_data.t_gyro) + "_" + model_data.timestamp + ".txt", "w")
        f.write(str(score_dict))
        f.close()
        print("Scores plotted")