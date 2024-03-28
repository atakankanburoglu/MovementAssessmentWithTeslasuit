import numpy as np
import csv
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == "__main__":
    humanboneIndex_dict = {}
    sample = pd.read_csv("C:/Users/Camil/Documents/Uni/Master/Thesis/Code/MovementAssessmentWithTeslasuit/SourceCode/PythonFiles_NewAPI/core/samples/7_PLANKHOLD_Positive_1710952813.csv")
    #Preprocessing
    #delete TrainingType, Timestamp and Spine, Chest and Left - & Rightshoulder (have no values)
    sample.drop(['TrainingType'], axis=1, inplace=True)
    sample.drop(['Timestamp'], axis=1, inplace=True)
    sample = sample.loc[:,~sample.columns.str.startswith('Spine')]
    sample = sample.loc[:,~sample.columns.str.startswith('Chest')]
    sample = sample.loc[:,~sample.columns.str.startswith('LeftShoulder')]
    sample = sample.loc[:,~sample.columns.str.startswith('RightShoulder')]
    #round to 6 decimals places
    #sample1 = sample.round(6).copy()
    #sample2 = np.round(sample, decimals=6)
    #Create mean and std for every column
    mean_std_df = sample.agg(['mean', 'std'])
    #split each HumanBoneIndex into different dfs 
    humanboneindex_dfs = np.split(sample, np.arange(20, len(sample.columns), 20), axis=1)
    #per HumanBoneIndex_df split all columns and find only unique values
    for humanboneindex in humanboneindex_dfs:
        #create empty training df per humanboneindex to fill
        training_df = pd.DataFrame(columns=['HumanBoneIndex_Axes', 'Value', 'mean', 'std'])
        humanboneIndex_name = []
        humanboneindex_axes_dfs = np.split(humanboneindex, np.arange(1, len(humanboneindex.columns), 1), axis=1)
        for axes in  humanboneindex_axes_dfs:
            humanboneIndex_name = axes.columns[0].split('_')
            axes = axes.round(5)
            axes = axes.drop_duplicates()
            #add each unique value with axes name, value, mean and std to final training_df
            for i in range(len(axes)):
                axes_name = axes.columns[0]
                value = axes.iloc[i][0]
                mean = mean_std_df.loc['mean'][axes.columns[0]]
                std = mean_std_df.loc['std'][axes.columns[0]]
                training_df.loc[len(training_df)] = {'HumanBoneIndex_Axes':axes.columns[0], 'Value': axes.iloc[i][0], 'mean': mean_std_df.loc['mean'][axes.columns[0]], 'std': mean_std_df.loc['std'][axes.columns[0]]}    
        
        humanboneIndex_dict[humanboneIndex_name[0]] = training_df
    print(humanboneIndex_dict)
    #round seconds to whole number
    #training_data['Timestamp'] = training_data['Timestamp'].astype(int)
    #split into multiple dataframes depending on timestamp
    #training_gb = training_data.groupby(['Timestamp'])
    #print(training_data['Timestamp'])
    #Y = pd.DataFrame()
    #for df in mean_std_dfs:
        #Y = pd.concat((Y, df), axis=1)
    
    #boneIndex = pd.DataFrame(list(training_data), columns=['HumanBoneIndex'])
   # X = pd.concat((boneIndex, training_data['Timestamp']), axis=1)
    
   
        
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