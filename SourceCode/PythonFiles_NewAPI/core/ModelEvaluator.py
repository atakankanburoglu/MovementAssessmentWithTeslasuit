import pandas as pd
import time
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
import seaborn as sns
from enums.Algorithm import Algorithm
import os

class ModelEvaluator:

    @staticmethod
    def plot_feedback_result_heatmaps(self, df_to_plot, subject_ids, training_type, algorithm, t):
        thisdir = os.getcwd()
        t = time.time()
        df_to_plot['Timestamp'] = df_to_plot['Timestamp'].min()

        gb_df_to_plot = df_to_plot.groupby(['HumanBoneIndex_Axis'])
        humanboneIndex_name = ""
        df = pd.DataFrame()
        for name, group in gb_df_to_plot: 
            name = name[0].split('_')[0]
            if humanboneIndex_name == "":
                humanboneIndex_name = name
            if humanboneIndex_name != name:
                df.fillna("0", inplace=True, axis=0)
                df_matrix = df.pivot_table(index="Timestamp", columns="HumanBoneIndex_Axis", values="Error").sort_values(by=['Timestamp'],ascending=False)
                plt.figure(figsize=(10, 10))
                sns.heatmap(df_matrix)
                plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + algorithm + "/" + subject_ids + "_" + humanboneindex_name + "_" + t + "_relative_errors_heatmap.png", dpi=1200)     
                plt.clf()
                humanboneIndex_name = name
                df = group
            else:
                df = pd.concat((df, group), axis=0)
        df.fillna("0", inplace=True, axis=0)
        df_matrix = df.pivot_table(index="Timestamp", columns="HumanBoneIndex_Axis", values="Error")
        plt.figure(figsize=(10, 10))
        sns.heatmap(df_matrix)
        plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + algorithm + "/" + subject_ids + "_" + humanboneindex_name + "_" + t + "_relative_errors_heatmap.png")     
        plt.clf()
        print("Finished saving heatmaps")

    @staticmethod
    def plot_feedback_result_barcharts(self, df_to_plot, filename, rows):
        thisdir = os.getcwd()
        t = time.time()
        gb_df_to_plot = df_to_plot.groupby(['HumanBoneIndex_Axis'])
        humanboneIndex_name = ""
        df = pd.DataFrame()
        for name, group in gb_df_to_plot: 
            name = name[0].split('_')[0]
            if humanboneIndex_name == "":
                humanboneIndex_name = name
            if humanboneIndex_name != name:
                df['label'] = pd.cut(df['Error'],bins=[-100, -10, -1, 1, 10, 100], labels=['Big Minus Error', 'Minus Error', 'No Error', 'Error', 'Big Error'])
                d = df.groupby(['HumanBoneIndex_Axis','label'])['Timestamp'].size().unstack()
                d.plot(kind='bar',stacked=True, title = "Test")
                plt.savefig("C:/Users/Camil/Documents/Uni/Master/Thesis/Code/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles_NewAPI/core/analysis/" + filename + "_" + self.algorithm + "_" + humanboneIndex_name + "_" + str(int(t)) + "_barchart.png", dpi=1200)
                plt.clf()
                humanboneIndex_name = name
                df = pd.DataFrame()
            else:
                df = pd.concat((df, group), axis=0)
        print("Finished saving barcharts")