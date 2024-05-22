import pandas as pd
import time
from sklearn import svm
from joblib import dump, load
from sklearn import svm, linear_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, precision_recall_fscore_support

import Config
from data.DataAccess import DataAccess
from data.DataManager import DataManager
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsClassifier
import seaborn as sns
from enums.Algorithm import Algorithm
from pyquaternion import Quaternion
import os

class ModelEvaluator:

    @staticmethod
    def plot_feedback_result_heatmaps(model_data, relative_errors):
        vectorBins = {
            "up" : np.array([0, 1, 0]),
            "down" : np.array([0, -1, 0]),

            "forward" : np.array([0, 0, -1]),
            "forward_up" : np.array([0, 1, -1]),
            "forward_down" : np.array([0, -1, -1]),

            "forward_left" : np.array([1, 0, -1]),
            "forward_left_up" : np.array([1, 1, -1]),
            "forward_left_down" : np.array([1, -1, -1]),

            "forward_right" : np.array([-1, 0, -1]),
            "forward_right_up" : np.array([-1, 1, -1]),
            "forward_right_down" : np.array([-1, -1, -1]),

            "left" : np.array([1, 0, 0]),
            "left_up" : np.array([1, 1, 0]),
            "left_down" : np.array([1, -1, 0]),

            "backward_left" : np.array([1, 0, 1]),
            "backward_left_up" : np.array([1, 1, 1]),
            "backward_left_down" : np.array([1, -1, 1]),

            "backward" : np.array([0, 0, 1]),
            "backward_up" : np.array([0, 1, 1]),
            "backward_down" : np.array([0, -1, 1]),

            "backward_right" : np.array([-1, 0, 1]),
            "backward_right_up" : np.array([-1, 1, 1]),
            "backward_right_down" : np.array([-1, -1, 1]),

            "right" : np.array([-1, 0, 0]),
            "right_up" : np.array([-1, 1, 0]),
            "right_down" : np.array([-1, -1, 0]),
        }
        data_err = []
        for t1 in relative_errors:
              data_err.extend([(t1[0], t1[1], ) + t2 for t2 in t1[2]])
        
        full_axes_lst = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "magnetometer_x", "magnetometer_y", "magnetometer_z" , "accelerometer_x", "accelerometer_y", "accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"] #,  
        
        needed_axes_lst = [a for a in full_axes_lst if not any(m for m in model_data.measurement_sets if m in a)]
        m_sets = [m1 for m1 in ["9x","6x", "magn", "accel", "linearAccel"] if not any(m2 for m2 in model_data.measurement_sets if m2 in m1)]
        columns = ["ExerciseType", "Row", "HBI"]
        columns.extend(needed_axes_lst)  
        df = pd.DataFrame(data_err, columns=columns)
        for  m_std, m_std_df in df.groupby(["ExerciseType"]): #should be all rows
            for m_set in m_sets:
                data = []
                for hbi, hbi_df in m_std_df.groupby(["HBI"]):
                    for row, row_df in hbi_df.groupby(["Row"]):
                        m_set_df = row_df.loc[:,row_df.columns.str.contains(m_set)]
                        entries = tuple(m_set_df.iloc[0].values)
                        if (len(entries) > 3  and (list(entries)[1:] != [0, 0, 0] and list(entries) != [0, 0, 0, 0])) or (len(entries) <= 3 and list(entries) != [0, 0, 0]):   
                            if len(entries) > 3:
                                quat = Quaternion(axis=list(entries)[1:], angle=entries[0])
                                v = quat.rotate([0, 0, -1]) # rotated around forward vector
                            else:
                                v = list(entries)
                            min_bin= ""
                            min_angle=0
                            for bin in vectorBins:
                                unit_vector_1 = vectorBins[bin] / np.linalg.norm(vectorBins[bin])
                                unit_vector_2 = v / np.linalg.norm(v)
                                dot_product = np.dot(unit_vector_1, unit_vector_2)
                                angle = np.arccos(dot_product)
                                if angle < min_angle or min_bin == "":
                                    min_bin = bin
                                    min_angle = angle
                            data.append((hbi[0], min_bin, np.round(angle, 2)))
                            for bin in vectorBins:
                                if bin != min_bin:
                                    data.append((hbi[0], bin, np.NaN))
                        else:
                            data.append((hbi[0], "None" , 0))
                df = pd.DataFrame(data, columns=["HBI", "Bin", "Angle"])
                df = df.groupby(["HBI", "Bin"]).count()
                df = df.fillna(0)
                plt.figure(figsize=(10,8))
                df_matrix_1 = df.pivot_table(index="Bin", columns="HBI", values="Angle").sort_values(by=['Bin'],ascending=False)
                df_matrix_1 = df_matrix_1.fillna(0)
                ax = sns.heatmap(df_matrix_1, annot=True, cmap="crest", annot_kws={"fontsize":7}, fmt='g', cbar_kws={'label': 'Number of Errors'}) 
                ax.set(xlabel="Human Bone Index", ylabel="Closest Direction to Vectors") 
                plt.xticks(rotation=45) 
                plt.tight_layout()
                #plt.show()
                thisdir = os.getcwd()
                plt.savefig(thisdir + "/core/analysis/evaluation/" + m_std[0] + "/heatmaps/" + model_data.subject_ids + "_" + model_data.algorithm + "_" + m_set + "_" + m_std[0] + "_" + str(model_data.t_gyro) + "_directions_heatmap.png", dpi=600)  
                plt.clf()