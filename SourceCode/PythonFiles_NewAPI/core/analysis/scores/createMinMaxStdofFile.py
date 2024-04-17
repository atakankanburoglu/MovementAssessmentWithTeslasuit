import numpy as np
import csv
import pandas as pd
import os
import seaborn as sns
import ast
import matplotlib.pyplot as plt
import re
from sklearn.metrics import accuracy_score, f1_score

from sklearn.model_selection import cross_val_score
from sklearn import svm

if __name__ == "__main__":
    sampleid_trainingtype_score_list = [("10", "FULLSQUAT" , 1.0), ("10", "PLANKHOLD" , 0.89), ("10", "SIDEPLANKLEFT", 1.0), ("10", "SIDEPLANKRIGHT" , 1.0),("14", "FULLSQUAT" , 1.0), ("14", "PLANKHOLD" , 1.0), ("14", "SIDEPLANKLEFT", 0.996), ("14", "SIDEPLANKRIGHT" , 1.0),("7", "FULLSQUAT" , 0.963), ("7", "PLANKHOLD" , 0.966), ("7", "SIDEPLANKLEFT" , 0.5205), ("7", "SIDEPLANKRIGHT" , 1.0), ("8", "FULLSQUAT", 1.0), ("8", "PLANKHOLD" , 1.0), ("8", "SIDEPLANKLEFT" , 0.9867), ("8", "SIDEPLANKRIGHT", 1.0), ("9", "FULLSQUAT" , 0.755), ("9", "PLANKHOLD" , 0.9995), ("9", "SIDEPLANKLEFT" , 0.9104), ("9", "SIDEPLANKRIGHT", 1.0), ("9", "SIDEPLANKRIGHT", 1.0)]
    training_type_list = ["PLANKHOLD", "FULLSQUAT", "SIDEPLANKRIGHT", "SIDEPLANKLEFT"]
        
    for training_type in training_type_list:
        x_axis = []
        y_axis = []
        for sampleid_trainingtype_score in sampleid_trainingtype_score_list:
            if sampleid_trainingtype_score[1] in training_type:
                y_axis.append(sampleid_trainingtype_score[2])
                x_axis.append(sampleid_trainingtype_score[0])
        plt.plot(x_axis, y_axis, label=training_type)
    plt.legend()
    plt.show()

def evaluate_validate_exercise_recognition_model():
    thisdir = os.getcwd()
    pos_data = pd.DataFrame()
    f = open(thisdir + "/core/analysis/scores/exercise_recognition_scores_onlyAccelerometerGyroscope.txt", "w")
    
    files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and "Positive" in f]
    for file_name in files:
        if pos_data.empty:
            pos_data = pd.read_csv(thisdir + "/core/samples/" + file_name)
        else:  
            df = pd.read_csv(thisdir + "/core/samples/" + file_name, header = 0)
            pos_data = pd.concat((pos_data, df), axis=0) 
    pos_data = pos_data.drop(['Timestamp'], axis=1)
    pos_data = pos_data.loc[:,~pos_data.columns.str.startswith('Spine')]
    pos_data = pos_data.loc[:,~pos_data.columns.str.startswith('Chest')]
    pos_data = pos_data.loc[:,~pos_data.columns.str.startswith('LeftShoulder')]
    pos_data = pos_data.loc[:,~pos_data.columns.str.startswith('RightShoulder')]
    pos_data = pos_data.loc[:,~pos_data.columns.str.contains('Foot')]
    pos_data = pos_data.loc[:,~pos_data.columns.str.contains('Hand')]
    pos_data = pos_data.loc[:,~pos_data.columns.str.contains('magn')]
    pos_data = pos_data.loc[:,~pos_data.columns.str.contains('linearAccel')]
    pos_data = pos_data.loc[:,~pos_data.columns.str.contains('9x')]
    pos_data = pos_data.loc[:,~pos_data.columns.str.contains('6x')]
    y_train = pos_data['TrainingType'].values
    X_train = pos_data.drop(['TrainingType'], axis=1)
    clf_cross = svm.SVC()
    scores = cross_val_score(clf_cross, X_train, y_train, cv=5)
    scores_str = np.array2string(scores, precision=2, separator=',',
                      suppress_small=True) 
    f.write(scores_str + str(scores.mean()) + "; " + str(scores.std())) 

    neg_samples = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and "Negative" in f] 
    pos_samples = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and "Positive" in f] 
    
    for neg_sample in neg_samples:
        id = neg_sample.split("_")[0] + "_"
        training_type = neg_sample.split("_")[1]
        pos_data = pd.DataFrame()
        files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and "Positive" in f and id not in f]
        for file_name in files:
            if pos_data.empty:
                pos_data = pd.read_csv(thisdir + "/core/samples/" + file_name)
            else:  
                df = pd.read_csv(thisdir + "/core/samples/" + file_name, header = 0)
                pos_data = pd.concat((pos_data, df), axis=0) 
        pos_data = pos_data.drop(['Timestamp'], axis=1)
        pos_data = pos_data.loc[:,~pos_data.columns.str.startswith('Spine')]
        pos_data = pos_data.loc[:,~pos_data.columns.str.startswith('Chest')]
        pos_data = pos_data.loc[:,~pos_data.columns.str.startswith('LeftShoulder')]
        pos_data = pos_data.loc[:,~pos_data.columns.str.startswith('RightShoulder')]
        pos_data = pos_data.loc[:,~pos_data.columns.str.contains('Foot')]
        pos_data = pos_data.loc[:,~pos_data.columns.str.contains('Hand')]
        pos_data = pos_data.loc[:,~pos_data.columns.str.contains('magn')]
        pos_data = pos_data.loc[:,~pos_data.columns.str.contains('linearAccel')]
        pos_data = pos_data.loc[:,~pos_data.columns.str.contains('9x')]
        pos_data = pos_data.loc[:,~pos_data.columns.str.contains('6x')]
        y_train = pos_data['TrainingType'].values
        X_train = pos_data.drop(['TrainingType'], axis=1)
        clf = svm.SVC()
        clf.fit(X_train, y_train)
        neg_data = pd.read_csv(thisdir + "/core/samples/" + neg_sample)
        neg_data = neg_data.drop(['Timestamp'], axis=1)
        neg_data = neg_data.loc[:,~neg_data.columns.str.startswith('Spine')]
        neg_data = neg_data.loc[:,~neg_data.columns.str.startswith('Chest')]
        neg_data = neg_data.loc[:,~neg_data.columns.str.startswith('LeftShoulder')]
        neg_data = neg_data.loc[:,~neg_data.columns.str.startswith('RightShoulder')]
        neg_data = neg_data.loc[:,~neg_data.columns.str.contains('Foot')]
        neg_data = neg_data.loc[:,~neg_data.columns.str.contains('Hand')]
        neg_data = neg_data.loc[:,~neg_data.columns.str.contains('magn')]
        neg_data = neg_data.loc[:,~neg_data.columns.str.contains('linearAccel')]
        neg_data = neg_data.loc[:,~neg_data.columns.str.contains('9x')]
        neg_data = neg_data.loc[:,~neg_data.columns.str.contains('6x')]
        X_test = neg_data.drop(['TrainingType'], axis=1)
        y_pred = clf.predict(X_test)
        y_true = [training_type]*len(y_pred)
        score = accuracy_score(y_true, y_pred)
        f.write("(" + neg_sample  + " , " + str(score) +")") 
    f.close()

def validate_excercise_model():
    pos_data = []
    neg_data = []
    thisdir = os.getcwd()
    files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv")]
    for f in files:
        file_name = f.split("_")
        if(file_name[2] == "Positive"):
            df = pd.read_csv(thisdir + "/core/samples/" + f)
            data.append(df)
    
    y = training_data['TrainingType'].values
    X = training_data.drop(['TrainingType'], axis=1)
    clf = svm.SVC()
    scores = cross_val_score(clf, X, y, cv=5)
    f = open(thisdir + "/core/analysis/scores/exercise_recognition_scores_5-fold.txt", "w")
    f.write(scores) 
    f.close()

def save_model_performance():
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