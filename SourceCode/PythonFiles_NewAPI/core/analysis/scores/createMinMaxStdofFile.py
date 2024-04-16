import numpy as np
import csv
import pandas as pd
import os
import seaborn as sns
import ast
import matplotlib.pyplot as plt
import re

if __name__ == "__main__":
    thisdir = os.getcwd()
    for training_type in ["PLANKHOLD", "SIDEPLANKRIGHT", "SIDEPLANKLEFT", "FULLSQUAT"]:
        files = [f for f in os.listdir(thisdir + "/core/analysis/scores") if f.endswith(".txt") and training_type in f and "values" in f]
        id_score_time_model_dict = {}
        for file in files:
            algorithm = file.split("_")[1]
            axes = "_".join([file.split("_")[4], file.split("_")[5]]) + "_"  
            f = open(thisdir + "/core/analysis/scores/" + file, "r")
            f.readline()
            id_score_time_dict = ast.literal_eval(f.readline())
            for humanboneindex_name, id_score_time in id_score_time_dict.items():
                id_score_time_model = [t + (algorithm, axes, ) for t in id_score_time]
                if humanboneindex_name in id_score_time_model_dict:
                    id_score_time_model_dict[humanboneindex_name].extend(id_score_time_model)
                else:
                    id_score_time_model_dict[humanboneindex_name] = id_score_time_model
            f.close()
        #x_axis = []
        #y_axis = []
        f = open(thisdir + "/core/analysis/scores/" + training_type + "_scores_table_best_as_entries.txt", "w")
        for humanboneindex_name, id_score_time_model in id_score_time_model_dict.items():
            entries = []
            for ax in ["all_ax", "no_magn_", "no_magn9x"]:
                entries_by_ax = [t + (humanboneindex_name, ) for t in id_score_time_model if ax in t[4]]
                entries.append(sorted(entries_by_ax, key = lambda i: i[1], reverse = True)[:1])
            
                #entries = [e + (humanboneindex_name, ) for e in entries]
            #entry1 = max(id_score_time_model, key = itemgetter(1))
            #entry1 = max(id_score_time_model, key = itemgetter(1))
            #scores_sorted = np.argsort([t[1] for t in id_score_time_model])
            #entries = [t for t in id_score_time_model if t[1] in scores_sorted[-3:]]
            for entry in entries:
                f.write(str(entry[0]) + "\n")
        f.close()
        
        #for id in ["1", "7", "8", "9", "10", "14"]:
        #for alg in ["LR", "RF", "NN"]:
        #    for ax in ["all_ax", "no_magn", "no_magn9x"]:
        #        for humanboneindex_name, id_score_time_model in id_score_time_model_dict.items():
        #            entry1 = [t[1] if t[1] > 0 else 0 for t in id_score_time_model if "1" in t[0] and alg in t[3] and ax in t[4]]
        #            entry7 = [t[1] if t[1] > 0 else 0 for t in id_score_time_model if "7" in t[0] and alg in t[3] and ax in t[4]]
        #            entry8 = [t[1] if t[1] > 0 else 0 for t in id_score_time_model if "8" in t[0] and alg in t[3] and ax in t[4]]
        #            entry9 = [t[1] if t[1] > 0 else 0 for t in id_score_time_model if "9" in t[0] and alg in t[3] and ax in t[4]]
        #            entry10 = [t[1] if t[1] > 0 else 0 for t in id_score_time_model if "10" in t[0] and alg in t[3] and ax in t[4]]
        #            entry14 = [t[1] if t[1] > 0 else 0 for t in id_score_time_model if "14" in t[0] and alg in t[3] and ax in t[4]]
        #            f.write(alg + " & " +  ax + " & " + humanboneindex_name + " & " + str(round(entry1[0], 2)) + " & " + str(round(entry7[0],2)) + " & " + str(round(entry8[0],2)) + " & " + str(round(entry9[0],2)) + " & " + str(round(entry10[0],2)) + " & " + str(round(entry14[0],2)) + "\\\ \n")
        #f.close()
                #y_axis = ([t[1] for t in id_score_time_model if id in t[0]])
                #y_axis = np.clip(y_axis, 0, max(y_axis))
                #x_axis = ([t[3] for t in id_score_time_model if id in t[0]])
                #plt.plot(x_axis, y_axis, label=humanboneindex_name)
            #plt.legend()
            #plt.savefig(thisdir + "/core/analysis/scores/" + training_type + "_axe_comparison_scores_" + id + ".png", dpi=600)     
            #plt.clf()
            #plt.close()
        #x_axis
    #x_axis = [t[0] t in score if t[0] == "9"]
    #y_axis = [t[1] t in score if t[0] == "9"]
        

    
   
def plot_relative_errors():
    relative_errors = pd.read_csv("C:/Users/Camil/Documents/Uni/Master/Thesis/Code/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles_NewAPI/core/analysis/10_PLANKHOLD_Negative_1711709176.csvrelative_errors.csv")
    relative_errors['label'] = pd.cut(relative_errors['Error'],bins=[-100, -1, 1, 100], labels=['Minus Error', 'No Error', 'Error'])
    d = relative_errors.groupby(['HumanBoneIndex_Axis','label'])['Timestamp'].size().unstack()
    d.plot(kind='bar',stacked=True, title = "Test")
    plt.show() 

def create_analysis():
    for f in os.listdir("C:/Users/Camil/Documents/Uni/Master/Thesis/Code/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles_NewAPI/core/samples/"):
        df = pd.read_csv("C:/Users/Camil/Documents/Uni/Master/Thesis/Code/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles_NewAPI/core/samples/" + f)
        df = df.drop(['TrainingType'], axis=1)
        df = df.drop(['Timestamp'], axis=1)
        df = df[df.columns.drop(list(df.filter(regex='gyro')))]
        df = df[df.columns.drop(list(df.filter(regex='magn')))]
        sns.heatmap(df.corr(), cbar = False, annot = True, fmt=".1f")
        df = df.agg(['min', 'max', 'mean', 'std'])
        dfs = np.split(df, np.arange(20, len(df.columns), 20), axis=1)
        with open("C:/Users/Camil/Documents/Uni/Master/Thesis/Code/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles_NewAPI/core/analysis/" + f + "_min_max_mean_std.csv",'a') as f:
            for df in dfs:
                df.to_csv(f)
                f.write("\n")

def create_heatmap():
    df = pd.read_csv("C:/Users/Camil/Documents/Uni/Master/Thesis/Code/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles_NewAPI/core/samples/7_PLANKHOLD_Positive_1710952813.csv")
    df = df.drop(['TrainingType'], axis=1)
    df = df.drop(['Timestamp'], axis=1)
    df = df.loc[:, (df != 0).any(axis=0)]
    df = df[df.columns.drop(list(df.filter(regex='gyro')))]
    df = df[df.columns.drop(list(df.filter(regex='magn')))]
    df = df[df.columns.drop(list(df.filter(regex='accelerometer')))]
    df = df[df.columns.drop(list(df.filter(regex='linearAccel')))]
    plt.figure(figsize=(25, 25))
    sns.heatmap(df.corr(), cbar = False)
    plt.savefig("C:/Users/Camil/Documents/Uni/Master/Thesis/Code/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles_NewAPI/core/analysis/heatmapOfAll.png", dpi=1200)
    print("Finished saving figure")