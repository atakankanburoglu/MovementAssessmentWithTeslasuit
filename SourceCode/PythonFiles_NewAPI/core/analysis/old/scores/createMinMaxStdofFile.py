import numpy as np
import csv
import pandas as pd
import os
import seaborn as sns
import ast
import matplotlib.pyplot as plt
import re
from sklearn.metrics import accuracy_score, f1_score
import statistics 
from sklearn.model_selection import cross_val_score
from sklearn import svm
from pyquaternion import Quaternion
from numpy import linalg 

#if __name__ == "__main__": 
def num_samples():
    thisdir = os.getcwd()
    data = []
    neg_data = []
    for exercise_type in ["SIDEPLANKRIGHT", "PLANKHOLD", "SIDEPLANKLEFT", "FULLSQUAT"]:
            sample_files = [f for f in os.listdir(thisdir + "/core/samples/") if "Negative" in f and exercise_type in f]
            training_data = pd.DataFrame()
            for file in sample_files:
                if training_data.empty:
                    training_data = pd.read_csv(thisdir + "/core/samples/" + file)
                else:  
                    df = pd.read_csv(thisdir + "/core/samples/" + file, header = 0)
                    training_data = pd.concat((training_data, df), axis=0) 
                training_data = training_data.drop(["ExerciseType", "Timestamp"], axis=1)
            training_data = training_data.loc[:,~training_data.columns.str.startswith('Spine')]
            training_data = training_data.loc[:,~training_data.columns.str.startswith('Chest')]
            training_data = training_data.loc[:,~training_data.columns.str.startswith('LeftShoulder')]
            training_data = training_data.loc[:,~training_data.columns.str.startswith('RightShoulder')]
            training_data = training_data.loc[:,~training_data.columns.str.contains('Foot')]
            training_data = training_data.loc[:,~training_data.columns.str.contains('Hand')]
            humanboneindex_dfs = np.split(training_data, np.arange(int(len(training_data.columns)/10), len(training_data.columns), int(len(training_data.columns)/10)), axis=1)
            for humanboneindex_df in humanboneindex_dfs:
                humanboneIndex_name = humanboneindex_df.columns[0].split("_")[0]
                humanboneindex_df = humanboneindex_df.drop_duplicates()
                neg_data.append((exercise_type, humanboneIndex_name, 0, len(humanboneindex_df)))

    for exercise_type in ["SIDEPLANKRIGHT", "PLANKHOLD", "SIDEPLANKLEFT", "FULLSQUAT"]:
            sample_files = [f for f in os.listdir(thisdir + "/core/samples/") if "Positive" in f and exercise_type in f]
            training_data = pd.DataFrame()
            for file in sample_files:
                if training_data.empty:
                    training_data = pd.read_csv(thisdir + "/core/samples/" + file)
                else:  
                    df = pd.read_csv(thisdir + "/core/samples/" + file, header = 0)
                    training_data = pd.concat((training_data, df), axis=0) 
            training_data = training_data.drop(["ExerciseType", "Timestamp"], axis=1)
            training_data = training_data.loc[:,~training_data.columns.str.startswith('Spine')]
            training_data = training_data.loc[:,~training_data.columns.str.startswith('Chest')]
            training_data = training_data.loc[:,~training_data.columns.str.startswith('LeftShoulder')]
            training_data = training_data.loc[:,~training_data.columns.str.startswith('RightShoulder')]
            training_data = training_data.loc[:,~training_data.columns.str.contains('Foot')]
            training_data = training_data.loc[:,~training_data.columns.str.contains('Hand')]
            humanboneindex_dfs = np.split(training_data, np.arange(int(len(training_data.columns)/10), len(training_data.columns), int(len(training_data.columns)/10)), axis=1)
            for humanboneindex_df in humanboneindex_dfs:
                humanboneIndex_name = humanboneindex_df.columns[0].split("_")[0]
                gyro_columns = [c for c in humanboneindex_df.columns if "gyro" in c]
                for t_gyro in [1, 5, 10]:
                    minus_t_gyro = 0 - t_gyro
                    humanboneindex_df_gyro = humanboneindex_df.drop(humanboneindex_df[(humanboneindex_df[gyro_columns[0]] > t_gyro) | (humanboneindex_df[gyro_columns[0]] < minus_t_gyro)].index)
                    humanboneindex_df_gyro = humanboneindex_df_gyro.drop(humanboneindex_df_gyro[(humanboneindex_df_gyro[gyro_columns[1]] > t_gyro) | (humanboneindex_df_gyro[gyro_columns[1]] < minus_t_gyro)].index)
                    humanboneindex_df_gyro = humanboneindex_df_gyro.drop(humanboneindex_df_gyro[(humanboneindex_df_gyro[gyro_columns[2]] > t_gyro) | (humanboneindex_df_gyro[gyro_columns[2]] < minus_t_gyro)].index)
                    #pos_one =  humanboneindex_df.drop(humanboneindex_df[(humanboneindex_df[gyro_columns] >= t_gyro) | (humanboneindex_df[gyro_columns] <= -t_gyro)].index)
                    humanboneindex_df_gyro = humanboneindex_df_gyro.drop_duplicates()
                    data.append((exercise_type, humanboneIndex_name, t_gyro, len(humanboneindex_df_gyro)))
    data.extend(neg_data)
    f = open(thisdir + "/core/analysis/evaluation/num_of_samples.txt", "w")
    data_df = pd.DataFrame(data, columns=["Exercise", "HBI", "t_gyro", "Samples"])
    data_df.drop(["HBI"], axis=1)
    pos_data = []
    for e_ex, e_ex_df in  data_df.groupby(["Exercise"]):
        row = []
        for t, t_df in e_ex_df.groupby(["t_gyro"]):
            mean = t_df["Samples"].mean()
            row.append(mean)
        f.write(e_ex[0] + " & " + str(int(row[1])) + " & " + str(int(row[2])) + " & " + str(int(row[0])) + " \\\\ \n" )
    f.close()
#if __name__ == "__main__": 
def heatmap_per_error():
    vectorBins = {
            "up" : np.array([0, 1, 0]),
            "down" : np.array([0, -1, 0]),

            "front" : np.array([0, 0, -1]),
            "front_up" : np.array([0, 1, -1]),
            "front_down" : np.array([0, -1, -1]),

            "front_left" : np.array([1, 0, -1]),
            "front_left_up" : np.array([1, 1, -1]),
            "front_left_down" : np.array([1, -1, -1]),

            "front_right" : np.array([-1, 0, -1]),
            "front_right_up" : np.array([-1, 1, -1]),
            "front_right_down" : np.array([-1, -1, -1]),

            "left" : np.array([1, 0, 0]),
            "left_up" : np.array([1, 1, 0]),
            "left_down" : np.array([1, -1, 0]),

            "back_left" : np.array([1, 0, 1]),
            "back_left_up" : np.array([1, 1, 1]),
            "back_left_down" : np.array([1, -1, 1]),

            "back" : np.array([0, 0, 1]),
            "back_up" : np.array([0, 1, 1]),
            "back_down" : np.array([0, -1, 1]),

            "back_right" : np.array([-1, 0, 1]),
            "back_right_up" : np.array([-1, 1, 1]),
            "back_right_down" : np.array([-1, -1, 1]),

            "right" : np.array([-1, 0, 0]),
            "right_up" : np.array([-1, 1, 0]),
            "right_down" : np.array([-1, -1, 0]),
        }
#def boxplot_per_error():
    thisdir = os.getcwd()
    for training_type in ["SIDEPLANKRIGHT", "PLANKHOLD", "SIDEPLANKLEFT"]:#, "FULLSQUAT"]: #
        for id in ["10", "14", "7", "8", "9"]: # "1", 
            rows = []
            for sample_type in ["Negative"]:#, "Positive"]:
                sample_files = [f for f in os.listdir(thisdir + "/core/analysis/evaluation/" + training_type + "/") if sample_type in f and id + "_" in f] 
                sample_data = []
                for file in sample_files:
                    f = open(thisdir + "/core/analysis/evaluation/" + training_type + "/" + file, "r")
                    sample_data = ast.literal_eval(f.read())
                    f.close() 
                    for a in sample_data: 
                        rows.extend([(t[0]  + "_" + t[1].split("_")[-1], t[1].split("_")[-2], t[2].split("_")[0], t[3], t[4]) + t[5] for t in a if "NN" in t[0] and t[3] == 2]) 

            axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z"]#, "Accelerometer_x", "Accelerometer_y", "Accelerometer_z"] #"Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"] #,  
            m_sets = ["9x","6x", "Magnetometer"]#, "Accelerometer"]#, "Linear"]"Linear Acceleration"
            columns = ["Model_timestamp", "HBI", "ID", "STD_coeff", "Row"]
            columns.extend(axes)  
            df = pd.DataFrame(rows, columns=columns)
            #df = df.drop(["ID"], axis=1)
            #df = df.drop(["Row"], axis=1)
            #df = df.drop(["HBI"], axis=1)
            for  m_std, m_std_df in df.groupby(["Model_timestamp", "STD_coeff"]):
                fig, axarr = plt.subplots(len(m_sets), sharex='col',gridspec_kw={'hspace': 0, 'wspace': 0}, figsize=(10,8))
                i = 0
                for m_set in m_sets:
                    current_pos = 0
                    ticks = []
                    data = []
                    pos=[]
                    for hbi, hbi_df in m_std_df.groupby(["HBI"]):
                        s = 0
                        #df_agg = m_set_df.agg(['mean'])
                        for row, row_df in hbi_df.groupby(["Row"]):
                            m_set_df = row_df.loc[:,row_df.columns.str.contains(m_set)]
                            entries = tuple(m_set_df.iloc[0].values)
                            if list(entries)[1:] == [0, 0, 0]:
                                entries = (0, 0, 0.01) #make small
                            if len(entries) > 3:
                                quat = Quaternion(axis=list(entries)[1:], angle=entries[0])
                                v = quat.rotate([0, 0, -1]) # rotated from front
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
                    df = pd.DataFrame(data, columns=["HBI", "Bin", "Angle"])
                    df = df.groupby(["HBI", "Bin"]).count()
                    df = df.fillna(0)
                    print(df)
                    plt.figure(figsize=(10,8))
                    df_matrix_1 = df.pivot_table(index="Bin", columns="HBI", values="Angle").sort_values(by=['Bin'],ascending=False)
                    df_matrix_1 = df_matrix_1.fillna(0)
                    ax = sns.heatmap(df_matrix_1, annot=True, cmap="crest") 
                    ax.set(xlabel="Human Bone Index", ylabel="Distance to Vector")
                    plt.xticks(rotation=45) 
                    #plt.xticks(range(2, (len(ticks) * 4)+2, 4), ticks)
                    plt.tight_layout()
                    plt.show()
                    #plt.savefig(thisdir + "/core/analysis/evaluation/" + training_type + "/heatmaps/" + training_type + "_" + m_std[0] + "_" + str(m_std[1]) + "_" + id + "_" + m_set + "_directions_heatmap_mean_rotatedfrom.png", dpi=600)  
                    plt.clf()  




def boxplot_all_errors(): # eval 2 calculate min, max´, mean per 
    thisdir = os.getcwd()
    for training_type in ["FULLSQUAT"]:#,SIDEPLANKRIGHT , "PLANKHOLD"]:#, "FULLSQUAT", "SIDEPLANKLEFT"]: #
        #for id in ["10", "14", "7", "8", "9"]: # "1", 
        rows = []
        for sample_type in ["Negative"]:#, "Positive"]:
            sample_files = [f for f in os.listdir(thisdir + "/core/analysis/evaluation/" + training_type + "/") if sample_type in f]# and id + "_" in f] 
            sample_data = []
            for file in sample_files:
                f = open(thisdir + "/core/analysis/evaluation/" + training_type + "/" + file, "r")
                sample_data = ast.literal_eval(f.read())
                f.close() 
                for a in sample_data: 
                    rows.extend([(t[0]  + "_" + t[1].split("_")[-1], t[1].split("_")[-2], t[2].split("_")[0], t[3], t[4]) + t[5] for t in a if "accel" in t[1] and t[3] == 2])  

        axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"] #,  "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z"]
        m_sets = ["9x","6x", "Magnetometer", "Linear Acceleration"]#, "Linear"]
        columns = ["Model_timestamp", "HBI", "ID", "STD_coeff", "Row"]
        columns.extend(axes)  
        df = pd.DataFrame(rows, columns=columns)
        #df = df.drop(["ID"], axis=1)
        df = df.drop(["Row"], axis=1)
        #df = df.drop(["HBI"], axis=1)
        for  m_std, m_std_df in df.groupby(["Model_timestamp", "STD_coeff"]):
            fig, axarr = plt.subplots(len(m_sets), sharex='col',gridspec_kw={'hspace': 0, 'wspace': 0}, figsize=(15,10))
            i = 0
            for m_set in m_sets:
                current_pos = 0
                ticks = []
                #data_neg = []
                #data_pos = []
                data = {}
                pos=[]
                for hbi, hbi_df in m_std_df.groupby(["HBI"]):
                    s = 0
                    for sample, sample_df in hbi_df.groupby(["ID"]):
                        m_set_df = sample_df.loc[:,sample_df.columns.str.contains(m_set)]
                        for c in m_set_df:
                            df_agg = m_set_df[c].agg(['min', 'mean', 'max'])
                            df_agg = df_agg.clip(-100, 100)
                            #if "Negative" in sample[0]:
                            if sample[0] in data:
                                data[sample[0]].append(tuple(df_agg.values))
                            else:
                                if len(m_set_df.columns) == 3 and current_pos == 0:
                                    current_pos = 1
                                data[sample[0]] = [tuple(df_agg.values)]
                            if len(data[sample[0]]) > len(pos):
                                pos.append(current_pos)
                                current_pos = current_pos + 1
                            #data_neg.append(tuple(df_agg.values))
                            #else:
                                #data_pos.append(tuple(df_agg.values)) 
                        
                    if len(ticks) < 9: 
                        axarr[i].axvline(x=current_pos + 1, color="black", linestyle='-', linewidth=0.1)    
                        if len(m_set_df.columns) > 3:
                            current_pos = current_pos + 3
                        else:
                            current_pos = current_pos + 4
                    ticks.append(hbi[0])

                colors = [(0, 0, 1, 0.5),(0, 1, 0, 0.5), (1, 0.6, 0, 0.5), (1, 0, 0, 0.5), (1, 0, 1, 0.5)]
                co = 0
                for sample in data:
                    axarr[i].boxplot(data[sample], positions=pos, patch_artist=True, boxprops=dict(facecolor=colors[co], color=colors[co]), capprops=dict(color=colors[co]), whiskerprops=dict(color=colors[co]),flierprops=dict(color=colors[co], markeredgecolor="black"),medianprops=dict(color=colors[co]))
                    co=co+1
                if len(m_set) > 3:
                    axarr[i].set_title(m_set, rotation=-90,x=1.01,y=0.15)
                else:
                    axarr[i].set_title(m_set, rotation=-90,x=1.01,y=0.45)
                axarr[i].set_xticks([])
                axarr[i].axhline(y=0, color="black", linestyle='-', linewidth=0.1)
                i = i + 1
            colors = [(0, 0, 1, 0.5),(0, 1, 0, 0.5), (1, 0.6, 0, 0.5), (1, 0, 0, 0.5), (1, 0, 1, 0.5)]
            co = 0
            for sample in data: 
                if "7" == sample:
                    label = "Error 1"
                if "8" == sample:
                    label = "Error 1 & 2"
                if "9" == sample:
                    label = "Error 1 & 4"
                if "10" == sample:
                    label = "Error 1 & 4"
                if "14" == sample:
                    label = "Error 1 & 3 & 4"
                axarr[i-1].plot([], c=colors[co], label=label)
                co=co+1
            
            #axarr[0].plot([], c='green', label='Positive Sample')
            axarr[i-1].legend(loc='lower left', bbox_to_anchor=(0, -0.8), ncol=2)
            axarr[i-1].set_xticks(range(2, (len(ticks) * 7), 7)) 
            axarr[i-1].set_xticklabels(ticks,fontsize=8)
            axarr[i-1].tick_params(labelrotation=45)
            fig.subplots_adjust(bottom=-0.2)
            plt.tight_layout()
            #plt.show()
            fig.savefig(thisdir + "/core/analysis/evaluation/" + training_type + "/boxplots/" + m_std[0] + "_" + training_type  + "_relativeErrors_PerErrorRecording.png", dpi=800)     
            plt.close()
                #           
            #                plt.boxplot(data_pos, positions=pos_pos, patch_artist=True, boxprops=dict(facecolor="green", color="green"), capprops=dict(color="green"), whiskerprops=dict(color="green"),flierprops=dict(color="black", markeredgecolor="black"),medianprops=dict(color="black"))
            #                
            #                plt.legend()
            #                plt.xticks(rotation=90) 
            #                plt.xticks(range(2, (len(ticks) * 4)+2, 4), ticks)
            #                plt.tight_layout()
            #                #plt.show()
                    #plt.tight_layout()
                        
                    #plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/new/plots/" + data_per_model_file[:-24] + "_relative_errors_min_max_subplots.png", dpi=1200)     
                    #plt.clf()
                    #f.close()

       
   
def std_ID_per_model():
    thisdir = os.getcwd()
    for training_type in ["SIDEPLANKLEFT", "SIDEPLANKRIGHT", "PLANKHOLD", "FULLSQUAT"]: #
        #axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
        #columns = ["Axes", "Model", "Sample"]
        #columns.extend(axes)
        #df_all = pd.DataFrame(columns=columns)
        #for ax in ["all_ax", "no_magn_", "no_magn9x"]:
        
        rows = []
        for id in ["1", "10", "14", "7", "8", "9"]: # 
            for sample_type in ["Positive", "Negative"]:
                sample_files = [f for f in os.listdir(thisdir + "/core/analysis/evaluation/" + training_type + "/") if sample_type in f and id + "_" in f] 
                sample_data = []
                for file in sample_files:
                    f = open(thisdir + "/core/analysis/evaluation/" + training_type + "/" + file, "r")
                    sample_data = ast.literal_eval(f.read())
                    f.close() 
                    for a in sample_data:
                        rows.extend([(t[0]  + "_" + t[1].split("_")[-1], t[1].split("_")[-2], t[2].split("_")[0], sample_type, t[3], t[4], np.round(np.asarray(t[5]).min(),2),  np.round(np.asarray(t[5]).max(),2),  np.round(np.asarray(t[5]).mean(),2)) for t in a])  

        axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z"]#, "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
       
        columns = ["Model_timestamp", "HBI", "ID" , "Sample_Type", "STD_coeff", "Row", "Min", "Max", "Mean"]
        #columns.extend(axes)  
        df = pd.DataFrame(rows, columns=columns)
        #df = df.drop(["ID"], axis=1)
        df = df.drop(["Row"], axis=1)
        df = df.drop(["HBI"], axis=1)
        #df = df.groupby(["Model_timestamp", "STD_coeff", "ID" , "Sample_Type"]).agg(['min', 'max', 'mean']) 
        f = open(thisdir + "/core/analysis/evaluation/" + training_type + "/" + training_type + "_" + "ranges.txt", "w")
        for i, m_std_id_df in df.groupby(["Model_timestamp", "STD_coeff", "ID" , "Sample_Type"]):#, "Min", "Max", "Mean"]):
            #cols_min = [c for c in m_std_id_df.columns if 'min' in c[1]]
            #cols_max = [c for c in m_std_id_df.columns if 'max' in c[1]]
            #cols_mean = [c for c in m_std_id_df.columns if 'mean' in c[1]]
            min = m_std_id_df["Min"].values.min()
            max = m_std_id_df["Max"].values.max()
            mean = m_std_id_df["Mean"].values.mean()
            f.write(i[0].split("_")[0] + " & " + str(i[1]) + " & " + i[2]  + " & " + i[3]+ " & " + str(np.round(min, 2))  + " & " +str(np.round(max, 2))  + " & " + str(np.round(mean, 2)) + "\\\\ \n")
        f.close()        
                #for m_std, m_std_df in  df.groupby(["Model_timestamp", "STD_coeff"]):
                #    df_min = df_temp.agg(['min'])   
                #    df_min.columns = axes
                #    df_min.loc[:, df_min.columns != 'HBI'] = df_min.loc[:, df_min.columns != 'HBI'].round(0)
                #    df_max = df_temp.groupby(['HBI']).agg(['max'])

def get_heatmaps_per_std(): #eval 1: has to be edited for each training type
    thisdir = os.getcwd()
    for training_type in ["SIDEPLANKRIGHT"]:#, "PLANKHOLD", "FULLSQUAT"]: #
        #axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
        #columns = ["Axes", "Model", "Sample"]
        #columns.extend(axes)
        #df_all = pd.DataFrame(columns=columns)
        #for ax in ["all_ax", "no_magn_", "no_magn9x"]:
        for id in ["1", "10", "14", "7", "8", "9"]: # 
            for sample_type in ["Positive", "Negative"]:
                sample_files = [f for f in os.listdir(thisdir + "/core/analysis/evaluation/" + training_type + "/") if sample_type in f and id + "_" in f if "1_1_5" not in f] 
                sample_data = []
                rows = []
                for file in sample_files:
                    f = open(thisdir + "/core/analysis/evaluation/" + training_type + "/" + file, "r")
                    sample_data = ast.literal_eval(f.read())
                    f.close() 
                    for a in sample_data:
                        rows.extend([(t[0]  + "_" + t[1].split("_")[-1], t[1].split("_")[-2], t[2].split("_")[0], t[3], t[4]) + t[5] for t in a])  

                axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z"]#, "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
       
                columns = ["Model_timestamp", "HBI", "ID", "STD_coeff", "Row"]
                columns.extend(axes)  
                df = pd.DataFrame(rows, columns=columns)
                df = df.drop(["ID"], axis=1)
                df = df.drop(["Row"], axis=1)
                #df = df.groupby(["Model", "STD_coeff"]).agg(['min', 'max']) 
                for m_std, m_std_df in  df.groupby(["Model_timestamp", "STD_coeff"]):
                    fig, (ax1, ax2, axcb) = plt.subplots(1, 3, gridspec_kw={'hspace': 0, 'wspace': 0.1, 'width_ratios':[1,1,0.07]}, figsize=(20,12))
                    #cols_min = [c for c in df.columns if 'min' in c[1]]
                    df_temp = m_std_df.drop(["STD_coeff"], axis=1)
                    df_temp = df_temp.drop(["Model_timestamp"], axis=1)
                    df_min = df_temp.groupby(['HBI']).agg(['min'])   
                    df_min.columns = axes
                    df_min.loc[:, df_min.columns != 'HBI'] = df_min.loc[:, df_min.columns != 'HBI'].round(0)
                    df_max = df_temp.groupby(['HBI']).agg(['max'])   
                    df_max.columns = axes
                    df_max.loc[:, df_max.columns != 'HBI'] = df_max.loc[:, df_max.columns != 'HBI'].round(0)
                    h1 = sns.heatmap(df_min.T, cmap="crest", annot=True, annot_kws={"fontsize":8}, vmin=-50, vmax=50, cbar=False, ax=ax1) 
                    h1.set_title('Minimum')
                    h2 = sns.heatmap(df_max.T, yticklabels=False, annot=True, annot_kws={"fontsize":8}, vmin=-50, vmax=50, cmap="crest", ax=ax2, cbar_ax=axcb)
                    h2.set_title('Maximum')
                    ax1.set_xlabel('')
                    ax1.set_ylabel('')
                    ax2.set_xlabel('')
                    ax2.set_ylabel('')
                    #fig.tight_layout()
                    fig.subplots_adjust(bottom=0.2)
                    #plt.show()+ str(m_std[1]) + "_" +
                    fig.savefig(thisdir + "/core/analysis/evaluation/" + training_type + "/heatmaps/" + m_std[0] + "_" + str(m_std[1]) + "_" + id + "_" + sample_type + "_relative_errors_min_max_heatmaps_subplots.png", dpi=600)     
                    plt.close()
                    plt.clf()

def get_mean_combined_measurements(): # 4 get combined mean (only FUllsquat)
    thisdir = os.getcwd()
    for training_type in ['FULLSQUAT']:
        files = [f for f in os.listdir(thisdir + "/core/analysis/validation/" + training_type + "/") if f.endswith(".txt") and training_type in f and "values" in f and "accel-Accel" in f] #any(m in f for m in ["6x-9x", "accel-Accel", "6x-accel", "9x-Accel", "6x-Accel", "9x-accel", "6x-magn", "magn-9x", "magn-Accel", "accel-magn"])]
        id_score_model_list = []
        for file in files:
            algorithm = file.split("_")[1]
            measurementSet = file.split("_")[4]
            t_gyro = file.split("_")[5]
            f = open(thisdir + "/core/analysis/validation/" + training_type + "/" + file, "r")
            id_score_dict = ast.literal_eval(f.readline())
            for humanboneindex_name, id_score in id_score_dict.items():
                id_score_model = [t + (algorithm, measurementSet, t_gyro, humanboneindex_name, ) for t in id_score]
                id_score_model_list.extend(id_score_model)
            f.close()

        df = pd.DataFrame(id_score_model_list, columns=["ID", "Score", "Algorithm", "MeasurementSet", "tgyro", "HBI"])
        df = df.drop(["HBI"], axis=1)
        #df = df.drop(["ID"], axis=1)
        df = df.drop(["MeasurementSet"], axis=1)
        df = df.groupby(["Algorithm", "tgyro", "ID"]).agg(['mean'])

        f = open(thisdir + "/core/analysis/validation/" + training_type + "/" + training_type + "_mean_models_per_ID_vali2_table.txt", "w")
        rows = []
        header = ""
        for m_a_t, m_a_t_df in df.groupby(["Algorithm", "tgyro"]):
            if "LR" not in m_a_t[1]:
                row = m_a_t[0] + " & " + m_a_t[1]
                header = "\\textbf{Algorithm} & \\textbf{$t_{gyro}$}"
                means = []
                for id, id_df in m_a_t_df.groupby(["ID"]):
                    header = header + " & \\textbf{" + str(id[0]) + "}"
                    mean = id_df.loc[:,('Score','mean')].values[0]
                    row = row + " & " + str(np.round(mean,2))
                    means.append(mean)
                header = header + " & \\textbf{R² Score Mean}"
                mean_alg = str(np.round(np.mean(means),3))
                row = row + " & " + mean_alg + ("\\\ \n")
                rows.append(row)

        f.write(header + "\\\\\hline \\midrule \n")
        [f.write(row) for row in rows]
        f.close()
#if __name__ == "__main__":
def get_mean_combined_measurements(): # 4 get combined mean
    thisdir = os.getcwd()
    for training_type in ['PLANKHOLD']:#"SIDEPLANKRIGHT", "SIDEPLANKLEFT"]:
        files = [f for f in os.listdir(thisdir + "/core/analysis/validation/" + training_type + "/") if f.endswith(".txt") and training_type in f and "values" in f and any(m in f for m in ["6x-9x", "accel-Accel", "6x-accel", "9x-Accel", "6x-Accel", "9x-accel", "6x-magn", "magn-9x", "magn-Accel", "accel-magn"])]
        id_score_model_list = []
        for file in files:
            algorithm = file.split("_")[1]
            measurementSet = file.split("_")[4]
            t_gyro = file.split("_")[5]
            f = open(thisdir + "/core/analysis/validation/" + training_type + "/" + file, "r")
            id_score_dict = ast.literal_eval(f.readline())
            for humanboneindex_name, id_score in id_score_dict.items():
                id_score_model = [t + (algorithm, measurementSet, t_gyro, humanboneindex_name, ) for t in id_score]
                id_score_model_list.extend(id_score_model)
            f.close()

        df = pd.DataFrame(id_score_model_list, columns=["ID", "Score", "Algorithm", "MeasurementSet", "tgyro", "HBI"])
        df = df.drop(["HBI"], axis=1)
        #df = df.drop(["ID"], axis=1)
        df = df.drop(["tgyro"], axis=1)
        df = df.groupby(["MeasurementSet", "Algorithm", "ID"]).agg(['mean'])

        f = open(thisdir + "/core/analysis/validation/" + training_type + "/" + training_type + "_mean_models_per_ID_vali2_table.txt", "w")
        rows = []
        header = ""
        for m_a_t, m_a_t_df in df.groupby(["MeasurementSet", "Algorithm"]):
            if "LR" not in m_a_t[1]:
                row = m_a_t[0] + " & " + m_a_t[1]
                header = "\\textbf{\\ac{IMU} Measurement Set} & \\textbf{Algorithm}"
                means = []
                for id, id_df in m_a_t_df.groupby(["ID"]):
                    header = header + " & \\textbf{" + str(id[0]) + "}"
                    mean = id_df.loc[:,('Score','mean')].values[0]
                    row = row + " & " + str(np.round(mean,2))
                    means.append(mean)
                header = header + " & \\textbf{R² Score Mean}"
                mean_alg = str(np.round(np.mean(means),3))
                row = row + " & " + mean_alg + ("\\\ \n")
                rows.append(row)

        f.write(header + "\\\\\hline \\midrule \n")
        [f.write(row) for row in rows]
        f.close()

if __name__ == "__main__":
#def mean_per_t_gyro(): # 3 (for second table that shows what best t_gyro to use for vali round 2)) 
    thisdir = os.getcwd()
    for training_type in ["SIDEPLANKLEFT", "PLANKHOLD", "SIDEPLANKRIGHT", "FULLSQUAT"]:
        files = [f for f in os.listdir(thisdir + "/core/analysis/validation/") if f.endswith(".txt") and training_type in f and "values_new" in f]
        id_score_model_list = []
        for file in files:
            algorithm = file.split("_")[1]
            measurementSet = file.split("_")[5]
            t_gyro = file.split("_")[6]
            f = open(thisdir + "/core/analysis/validation/" + file, "r")
            id_score_dict = ast.literal_eval(f.readline())
            for humanboneindex_name, id_score in id_score_dict.items():
                id_score_model = [t + (algorithm, measurementSet, t_gyro, humanboneindex_name, ) for t in id_score]
                id_score_model_list.extend(id_score_model)
            f.close()

        df = pd.DataFrame(id_score_model_list, columns=["ID", "Score", "Algorithm", "MeasurementSet", "tgyro", "HBI"])
        df = df.drop(["HBI"], axis=1)
        df = df.drop(["ID"], axis=1)
        df = df.groupby(["MeasurementSet", "Algorithm", "tgyro"]).agg(['mean'])

        f = open(thisdir + "/core/analysis/validation/" + training_type + "/" + training_type + "_mean_models_per_tgyro_table_combi.txt", "w")
        rows = []
        f.write("\\textbf{Excluded \\ac{IMU} Measurement Set} & \\textbf{Algorithm} & \\textbf{$t_{gyro}$} & \\textbf{Mean R² score} \\\\\hline \\midrule \n")
        for i in df.index:
            if "5" == i[2]:# and "-" not in i[0]: 
                index1 = (i[0], i[1], '5')
                mean1 = str(np.round(df[('Score', 'mean')].loc[index1],3))
                index2 = (i[0], i[1], '10')
                mean2 = str(np.round(df[('Score', 'mean')].loc[index2],3))
                diff = np.round(abs(np.round(df[('Score', 'mean')].loc[index1],3) - np.round(df[('Score', 'mean')].loc[index2],3)), 3)
                row = i[0] + " & " + i[1] + " & " + mean1 + " & " + mean2 + "\\\ \n" # + " & " + str(diff)  + 
                f.write(row)
        f.close()

def get_best_performing_model_groups(): #2 (for table in eval round 1)
    thisdir = os.getcwd()
    for training_type in ["PLANKHOLD", "SIDEPLANKRIGHT", "SIDEPLANKLEFT", "FULLSQUAT"]:
        files = [f for f in os.listdir(thisdir + "/core/analysis/validation/" + training_type + "/") if f.endswith(".txt") and training_type in f and "values" in f ]
        id_score_model_list = []
        for file in files:
            algorithm = file.split("_")[1]
            measurementSet = file.split("_")[4]
            t_gyro = file.split("_")[5]
            f = open(thisdir + "/core/analysis/validation/" + training_type + "/" + file, "r")
            id_score_dict = ast.literal_eval(f.readline())
            for humanboneindex_name, id_score in id_score_dict.items():
                id_score_model = [t + (algorithm, measurementSet, t_gyro, humanboneindex_name, ) for t in id_score]
                id_score_model_list.extend(id_score_model)
            f.close()

        df = pd.DataFrame(id_score_model_list, columns=["ID", "Score", "Algorithm", "MeasurementSet", "tgyro", "HBI"])
        df = df.drop(["HBI"], axis=1)
        df = df.groupby(["MeasurementSet","Algorithm",  "tgyro", "ID"]).agg(['mean'])
        #df = df.sort_values(by=[('Score', 'mean')])

        rows = []
        rows.append("\\textbf{\\ac{IMU} Measurement Set} & \\textbf{Algorithm} & \\textbf{$t_{gyro}$} & \\textbf{ID} & \\textbf{Mean of Scores} \\\\\hline \\midrule \n")
        mean_mean = 0
        for index, index_df in df.groupby(["MeasurementSet"]):
            means = []
            for id, id_df in index_df.groupby(["ID"]):
                max_mean_index = id_df[('Score', 'mean')].idxmax()
                max_mean_value = id_df.loc[max_mean_index].values[0]
                means.append(max_mean_value)
                mean = str(np.round(max_mean_value,2))
                row = max_mean_index[0] + " & " + max_mean_index[1] + " & " + max_mean_index[2] + " & " + max_mean_index[3] + " & " + mean + "\\\ \n"
                rows.append(row)
            index_df_mean = str(np.round(np.mean(means),3))
            row = index[0] + " &  &  &  & " + index_df_mean + "\\\\\hline \\hline\n"
            rows.append(row)
        f = open(thisdir + "/core/analysis/validation/" + training_type + "/" + training_type + "_best-performing_by_mean_models_per_id_table.txt", "w")

        [f.write(row) for row in rows]
        f.close()


def get_mean_per_id(): #1 (for longtable)
    thisdir = os.getcwd()
    for training_type in ["PLANKHOLD", "SIDEPLANKRIGHT", "SIDEPLANKLEFT", "FULLSQUAT"]:
        files = [f for f in os.listdir(thisdir + "/core/analysis/validation/" + training_type + "/") if f.endswith(".txt") and training_type in f and "values" in f]
        id_score_model_list = []
        for file in files:
            algorithm = file.split("_")[1]
            measurementSet = file.split("_")[4]
            t_gyro = file.split("_")[5]
            f = open(thisdir + "/core/analysis/validation/" + training_type + "/" + file, "r")
            id_score_dict = ast.literal_eval(f.readline())
            for humanboneindex_name, id_score in id_score_dict.items():
                id_score_model = [t + (algorithm, measurementSet, t_gyro, humanboneindex_name, ) for t in id_score]
                id_score_model_list.extend(id_score_model)
            f.close()

        df = pd.DataFrame(id_score_model_list, columns=["ID", "Score", "Algorithm", "MeasurementSet", "tgyro", "HBI"])
        df = df.drop(["HBI"], axis=1)
        df = df.groupby(["MeasurementSet","Algorithm",  "tgyro", "ID"]).agg(['min', 'max', 'mean'])
   
        rows = []
        header = ""
        for m_a_t, m_a_t_df in df.groupby(["MeasurementSet", "Algorithm",  "tgyro"]):
            row = m_a_t[0] + " & " + m_a_t[1] + " & " + m_a_t[2]
            header = "\\textbf{\\ac{IMU} Measurement Set} & \\textbf{Algorithm} & \\textbf{$t_{gyro}$}"
            for id, id_df in m_a_t_df.groupby(["ID"]):
                header = header + " & \\textbf{" + str(id[0]) + "}"
                mean = str(np.round(id_df.loc[:,('Score','mean')].values[0],2))
                row = row + " & " + mean
            row = row + ("\\\ \n")
            rows.append(row)
        f = open(thisdir + "/core/analysis/validation/" + training_type + "/" + training_type + "_mean_models_per_id_table_with_combined.txt", "w")

        f.write(header + "\\\\\hline \\midrule \n")
        [f.write(row) for row in rows]
        f.close()
        
    #    f = open(thisdir + "/core/analysis/scores/" + "PLANKHOLD" + "_best_performing_models_per_id_per_set.txt", "w")
    ##6 ids * 3 achsen * 10 Human Bone Indexes = 720 (180 pro file, da pro trainingsytype)
        
    #entries = []
    #for id in ["14", "9", "10", "7", "8", "1"]:
    #    for m in ["", "magn", "9x", "6x", "accel", "Accel"]:
    #        for humanboneindex_name, id_score_algorithm_measurementSet_t_gyro in id_score_time_model_dict.items():
    #            entries_by_id_ax = [t + (humanboneindex_name, ) for t in id_score_algorithm_measurementSet_t_gyro if m in t[3] and id == t[0]]
    #            entries.append(sorted(entries_by_id_ax, key = lambda i: i[1], reverse = True))

    #for entry in entries:
    #    f.write(str(entry[0]) + ",")
    #f.close()
    


#if __name__ == "__main__": 
def max_min_mean_std_of_gyro():
    thisdir = os.getcwd()
    training_data = []
    files = [f for f in os.listdir(thisdir + "/core/samples/") if f.endswith(".csv") and "Positive" in f]
    for f in files:
        if len(training_data) == 0:
            training_data = df = pd.read_csv(thisdir + "/core/samples/" + f)
        else:
            df = pd.read_csv(thisdir + "/core/samples/" + f, header = 0)
            training_data = pd.concat((training_data, df), axis=0) 
    training_data = training_data.loc[:,~training_data.columns.str.startswith('Spine')]
    training_data = training_data.loc[:,~training_data.columns.str.startswith('Chest')]
    training_data = training_data.loc[:,~training_data.columns.str.startswith('LeftShoulder')]
    training_data = training_data.loc[:,~training_data.columns.str.startswith('RightShoulder')]
    training_data = training_data.loc[:,~training_data.columns.str.contains('Foot')]
    training_data = training_data.loc[:,~training_data.columns.str.contains('Hand')]
    training_data = training_data.loc[:,training_data.columns.str.contains('gyro')]
    training_data = training_data.agg(['min', 'max', 'mean', 'std'])
    #training_data = training_data.reset_index(drop=True)
    training_data = training_data.agg(min_min=('min', 'min'), max_max=('max', 'max'), meanmean=('mean', 'mean'), std_mean=('mean', 'std'), axis=1)
    #training_data = training_data.agg(['max', 'min', 'mean', 'mean'], axis=1)
    print(training_data)

def subplots_heatmaps():
    thisdir = os.getcwd()
    for training_type in ["FULLSQUAT"]:#, "PLANKHOLD", "FULLSQUAT"]: #
        #axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
        #columns = ["Axes", "Model", "Sample"]
        #columns.extend(axes)
        #df_all = pd.DataFrame(columns=columns)
        for ax in ["all_ax", "no_magn_", "no_magn9x"]:
            model_data_per_sample_files = [f for f in os.listdir(thisdir + "/core/analysis/relative_errors/" + training_type + "/new/") if ax in f] 
            for data_per_model_file in model_data_per_sample_files:
                f = open(thisdir + "/core/analysis/relative_errors/" + training_type + "/new/" + data_per_model_file, "r")
                data_per_model_dict = ast.literal_eval(f.read())
                
                axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
              
                if ax in "no_magn_":
                    axes = [a for a in axes if "Magn" not in a]
                if ax in "no_magn9x":
                    axes = [a for a in axes if "Magn" not in a and "9x" not in a]

                rows = []
                for  model_name, data_per_model in data_per_model_dict[0].items():
                    rows.extend([(model_name.split("_")[1], ) + data[2] for data in data_per_model]) 
                columns = ["Model"]
                columns.extend(axes)  
                df = pd.DataFrame(rows, columns=columns)
                fig, (ax1, ax2, axcb) = plt.subplots(1, 3, gridspec_kw={'hspace': 0, 'wspace': 0.1, 'width_ratios':[1,1,0.07]}, figsize=(20,12))
                df_min = df.groupby(['Model']).agg(['min'])   
                df_min.columns = axes
                df_max = df.groupby(['Model']).agg(['max'])   
                df_max.columns = axes
                h1 = sns.heatmap(df_min.T, annot=True, cmap="crest", vmin=-50, vmax=50, cbar=False, ax=ax1)
                h1.set_title('Minimum')
                h2 = sns.heatmap(df_max.T, annot=True, yticklabels=False, cmap="crest", vmin=-50, vmax=50, ax=ax2, cbar_ax=axcb)
                h2.set_title('Maximum')
                ax1.set_xlabel('')
                ax1.set_ylabel('')
                ax2.set_xlabel('')
                ax2.set_ylabel('')
                fig.tight_layout()
                #plt.show()
                fig.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/new/plots/" + data_per_model_file[:-24] + "_relative_errors_min_max_subplots.png", dpi=600)     
                plt.clf()
                #fig, axarr = plt.subplots(len(data_per_model_dict[0]), sharex='col',gridspec_kw={'hspace': 1, 'wspace': 0})
                #plt.figure(figsize=(20, 20))
                #i=0
                #for  model_name, data_per_model in data_per_model_dict[0].items():
                #    rows = [data[2] for data in data_per_model]       
                #    #columns = ["Model"]
                #    #c0olumns.extend(axes)  
                #    df = pd.DataFrame(rows, columns=axes)
                #    df = df.agg(['min', 'mean', 'max'])
                #    print(df)
                #    data_min = df.loc['min'].values
                #    data_mean = df.loc['mean'].values
                #    data_max = df.loc['max'].values
                #    axarr[i].fill_between(axes, data_min, data_max, facecolor="green", alpha=0.5)
                #    axarr[i].plot(range(len(axes)), data_mean, color="green")
                #    axarr[i].set_title(model_name)
                #    axarr[i].tick_params(labelrotation=20)
                #    #axarr[0].legend()
                #    i = i + 1
                #plt.tight_layout()
                ##plt.show()
                #plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/new/plots/" + data_per_model_file[:-24] + "_relative_errors_min_max_subplots.png", dpi=1200)     
                #plt.clf()
                #f.close()
        
            #f = open(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + id + "_models_mean_std_relative_error_table.txt" , "w")      
            #f.write(str(ax_samplename_row_relativeerrors_dict_all))
            #f.close()

        #    for model_name, ax_samplename_row_relativeerrors_list in ax_samplename_row_relativeerrors_dict_all.items():
        #        axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
        #        if "no_magn_" in ax_samplename_row_relativeerrors_list[0][0]:
        #            axes = [a for a in axes if "Magn" not in a]
        #        if "no_magn9x" in ax_samplename_row_relativeerrors_list[0][0]:
        #            axes = [a for a in axes if "Magn" not in a and "9x" not in a]
        
        #        rows = [(ax_samplename_row_relativeerrors[0], model_name, ax_samplename_row_relativeerrors[1].split("_")[1], ax_samplename_row_relativeerrors[2]) + ax_samplename_row_relativeerrors[3] for ax_samplename_row_relativeerrors in ax_samplename_row_relativeerrors_list]       
        #        columns = ["Axes", "Model", "Sample", "Row"]
        #        columns.extend(axes)  
        #        df = pd.DataFrame(rows, columns=columns)
        #        df_all = pd.concat((df_all, df), axis=0)
        #        print("Rows added")
        
        #df_all = df_all.drop(['Row'], axis=1)
        #df_min_mean_max = df_all.groupby(['Axes', 'Model', 'Sample']).agg(['min', 'mean', 'max'])
        #df_min_mean_max = df_min_mean_max.reset_index()
        #for axes, df_axes in df_min_mean_max.groupby(['Axes']):
        #    if "no_magn_" in axes[0]:
        #        df_axes = df_axes.drop([t for t in df_axes.columns if 'Magn' in t[0]], axis=1)
        #    if "no_magn9x" in axes[0]:
        #        df_axes = df_axes.drop([t for t in df_axes.columns if 'Magn' in t[0]], axis=1)
        #        df_axes = df_axes.drop([t for t in df_axes.columns if '9x' in t[0]], axis=1)
                
            
        #    fig, axarr = plt.subplots(10, sharex='col',gridspec_kw={'hspace': 1, 'wspace': 0})
        #    plt.figure(figsize=(20, 20))
        #    i = 0
        #    a = axarr[0]
        #    for model, df_model in df_axes.groupby(['Model']):
        #        for sample, df_sample in df_model.groupby(['Sample']):
        #            if 'Negative' in sample[0]:
        #                c="red"
        #            else:
        #                c="green"
        #            xticks = [t[0] for t in df_sample.columns if 'min' in t[1]]
        #            data_min = df_sample[[t for t in df_sample.columns if 'min' in t[1]]].iloc[0]
        #            data_mean = df_sample[[t for t in df_sample.columns if 'mean' in t[1]]].iloc[0]
        #            data_max = df_sample[[t for t in df_sample.columns if 'max' in t[1]]].iloc[0]
        #            axarr[i].fill_between(xticks, data_min, data_max, label=sample[0], facecolor=c, alpha=0.5)
        #            axarr[i].plot(range(len(xticks)), data_mean, color=c)
        #        axarr[i].set_title(model[0])
        #        axarr[i].tick_params(labelrotation=20)
        #        axarr[0].legend()
        #        i = i + 1
        #    plt.tight_layout()
        #    plt.show()
        #    plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + axes[0] + "_relative_errors_min_max_subplot.png", dpi=1600)     
        #    plt.clf()
                


    
    
def evaluate_relative_errors():    
    thisdir = os.getcwd()
    for training_type in ["SIDEPLANKLEFT", "SIDEPLANKRIGHT", "PLANKHOLD", "FULLSQUAT"]: #
        axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
        columns = ["Axes", "Model", "Sample"]
        columns.extend(axes)
        df_all = pd.DataFrame(columns=columns)
        for id in ["14", "9", "10", "7", "8", "1"]:
            ax_samplename_row_relativeerrors_dict_all = {}
            data_per_model_files = [f for f in os.listdir(thisdir + "/core/analysis/relative_errors/" + training_type) if training_type in f and id in f] 
            for data_per_model_file in data_per_model_files:
                f = open(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + data_per_model_file, "r")
                ax_samplename_row_relativeerrors_dict_per_sample = ast.literal_eval(f.read())
                for model_name, ax_samplename_row_relativeerrors in ax_samplename_row_relativeerrors_dict_per_sample.items():
                    if model_name in ax_samplename_row_relativeerrors_dict_all:
                        ax_samplename_row_relativeerrors_dict_all[model_name].extend(ax_samplename_row_relativeerrors)
                    else:
                        ax_samplename_row_relativeerrors_dict_all[model_name] = ax_samplename_row_relativeerrors
                f.close()
        
            #f = open(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + id + "_models_mean_std_relative_error_table.txt" , "w")      
            #f.write(str(ax_samplename_row_relativeerrors_dict_all))
            #f.close()

            for model_name, ax_samplename_row_relativeerrors_list in ax_samplename_row_relativeerrors_dict_all.items():
                axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
                if "no_magn_" in ax_samplename_row_relativeerrors_list[0][0]:
                    axes = [a for a in axes if "Magn" not in a]
                if "no_magn9x" in ax_samplename_row_relativeerrors_list[0][0]:
                    axes = [a for a in axes if "Magn" not in a and "9x" not in a]
        
                rows = [(ax_samplename_row_relativeerrors[0], model_name, ax_samplename_row_relativeerrors[1].split("_")[1], ax_samplename_row_relativeerrors[2]) + ax_samplename_row_relativeerrors[3] for ax_samplename_row_relativeerrors in ax_samplename_row_relativeerrors_list]       
                columns = ["Axes", "Model", "Sample", "Row"]
                columns.extend(axes)  
                df = pd.DataFrame(rows, columns=columns)
                df_all = pd.concat((df_all, df), axis=0)
                print("Rows added")
        
        df_all = df_all.drop(['Row'], axis=1)
        df_min_mean_max = df_all.groupby(['Axes', 'Model', 'Sample']).agg(['min', 'mean', 'max'])
        df_min_mean_max = df_min_mean_max.reset_index()
        for axes, df_axes in df_min_mean_max.groupby(['Axes']):
            if "no_magn_" in axes[0]:
                df_axes = df_axes.drop([t for t in df_axes.columns if 'Magn' in t[0]], axis=1)
            if "no_magn9x" in axes[0]:
                df_axes = df_axes.drop([t for t in df_axes.columns if 'Magn' in t[0]], axis=1)
                df_axes = df_axes.drop([t for t in df_axes.columns if '9x' in t[0]], axis=1)
                
            
            fig, axarr = plt.subplots(10, sharex='col',gridspec_kw={'hspace': 1, 'wspace': 0})
            plt.figure(figsize=(20, 20))
            i = 0
            a = axarr[0]
            for model, df_model in df_axes.groupby(['Model']):
                for sample, df_sample in df_model.groupby(['Sample']):
                    if 'Negative' in sample[0]:
                        c="red"
                    else:
                        c="green"
                    xticks = [t[0] for t in df_sample.columns if 'min' in t[1]]
                    data_min = df_sample[[t for t in df_sample.columns if 'min' in t[1]]].iloc[0]
                    data_mean = df_sample[[t for t in df_sample.columns if 'mean' in t[1]]].iloc[0]
                    data_max = df_sample[[t for t in df_sample.columns if 'max' in t[1]]].iloc[0]
                    axarr[i].fill_between(xticks, data_min, data_max, label=sample[0], facecolor=c, alpha=0.5)
                    axarr[i].plot(range(len(xticks)), data_mean, color=c)
                axarr[i].set_title(model[0])
                axarr[i].tick_params(labelrotation=20)
                axarr[0].legend()
                i = i + 1
            plt.tight_layout()
            plt.show()
            plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + axes[0] + "_relative_errors_min_max_subplot.png", dpi=1600)     
            plt.clf()
                    

        #for column in df_all.columns:
        #    if column not in ["Axes", "Model", "Sample", "Row"]:
        #        plt.figure(figsize=(20, 20))
        #        for sample, df_sample in df_all.groupby(['Axes', 'Model', 'Sample']):
        #            df_col = pd.concat((df_sample['Row'], df_sample[column]), axis=1)
        #            df_col = df_col.drop_duplicates(subset=['Row'])
        #            y_axis = list(df_col[column].values)
        #            x_axis = list(df_col['Row'].values)
        #            plt.plot(x_axis, y_axis, label = sample[2][:-4])
        #        plt.legend()
        #        plt.xlabel('Rows')
        #        plt.ylabel('Relative Error')
        #        #plt.show()
        #        plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + sample[0] + "_" + sample[1] + "_" + column + "_relative_errors_plot.png", dpi=1200)     
        #        plt.clf()
        #df_all.drop(["Row"], axis=1)
        #df_all = df_all.groupby(['Axes', 'Model','Sample']).agg(['min', 'mean', 'max'])
        
        
        
        #column_done = ""
        #for column in df_all.columns: 
        #    if column[0] not in column_done:
        #        column_done = column[0]
        #        axes = df_all.index[0][0]
        #        model = df_all.index[0][1]
        #        column_done = column[0]
        #        current_pos = 1
        #        pos_neg = []
        #        pos_pos = []
        #        data_neg = []
        #        data_pos = []
        #        ticks = [model]
        #        for i in range(len(df_all)):
        #            if axes not in df_all.index[i][0]:
        #                plt.figure(figsize=(20, 20))
        #                plt.boxplot(data_neg, positions=pos_neg, patch_artist=True, boxprops=dict(facecolor="red", color="red"), capprops=dict(color="red"), whiskerprops=dict(color="red"),flierprops=dict(color="black", markeredgecolor="black"),medianprops=dict(color="black"))
        #                plt.boxplot(data_pos, positions=pos_pos, patch_artist=True, boxprops=dict(facecolor="green", color="green"), capprops=dict(color="green"), whiskerprops=dict(color="green"),flierprops=dict(color="black", markeredgecolor="black"),medianprops=dict(color="black"))
        #                plt.plot([], c='red', label='Negative Sample')
        #                plt.plot([], c='green', label='Positive Sample')
        #                plt.legend()
        #                plt.xticks(rotation=90) 
        #                plt.xticks(range(2, (len(ticks) * 4)+2, 4), ticks)
        #                plt.tight_layout()
        #                #plt.show()
        #                plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + axes + "_" + column[0] + "_relative_errors_plot.png", dpi=1200)     
        #                axes = df_all.index[i][0]
        #                current_pos = 1
        #                pos_neg = []
        #                pos_pos = []
        #                data_neg = []
        #                data_pos = []
        #                ticks = []
        #            if model not in df_all.index[i][1]:
        #                ticks.append(model)
        #                ticks_pos = []
        #                model = df_all.index[i][1]
        #            cols = [t for t in df_all.columns if column[0] in t[0]]
        #            data = df_all[cols].iloc[i]
        #            if "Negative" in df_all.index[i][2]:
        #                data_neg.append(data.values)
        #                pos_neg.append(current_pos)
        #            else:
        #                data_pos.append(data.values)
        #                pos_pos.append(current_pos)
        #            current_pos = current_pos + 1
                
                
            
                #if column not in ["Axes", "Model", "Sample"]:
                
            #for column in df.columns:
            #    if column not in ["Axes", "Model", "Sample", "Row"]:
            #        plt.figure(figsize=(20, 20))
            #        for sample, df_sample in df.groupby(['Axes', 'Model', 'Sample']):
            #            df_col = pd.concat((df_sample['Row'], df_sample[column]), axis=1)
            #            df_col = df_col.drop_duplicates(subset=['Row'])
            #            y_axis = list(df_col[column].values)
            #            x_axis = list(df_col['Row'].values)
            #            plt.plot(x_axis, y_axis, label = sample[2][:-4])
            #        plt.legend()
            #        plt.xlabel('Rows')
            #        plt.ylabel('Relative Error')
            #        #plt.show()
            #        plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + axes_model[0] + "_" + axes_model[1] + "_" + column + "_relative_errors_plot.png", dpi=1200)     
            #        plt.clf()

        #df_mean_std = df_all.groupby(['Axes', 'Model','Sample']).agg(['mean', 'std'])
        #df_mean_std = df_mean_std.reset_index()
            
        #w = 0.25
        #fig, ax = plt.subplots(figsize =(20, 8))
        #for axes_model, axes_model_df in df_mean_std.groupby(['Axes', 'Model']):
        #    b = np.arange((axes_model_df.shape[1]-3)/2)
        #    for i in axes_model_df.index:
        #        b_ = [x + w*i for x in b]
        #        y_axis_mean=axes_model_df.loc[i, [t for t in axes_model_df.columns if 'mean' in t[1]]].values #axes_model_df.columns[1].str.contains('mean')].values
        #        yerr_std =axes_model_df.loc[i, [t for t in axes_model_df.columns if 'std' in t[1]]].values
        #        plt.bar(b_, y_axis_mean, width=w, label=axes_model_df['Sample'].iloc[0][:-4], yerr = yerr_std)
        #    plt.xticks(b, [t[0] for t in axes_model_df.columns if 'mean' in t[1]])
        #    plt.legend()
        #    plt.tight_layout()
        #    plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + axes_model[0] + "_" + axes_model[1] + "_relative_errors_per_axes_barchart.png", dpi=1200)     
        #    plt.clf()



            #f = open(thisdir + "/core/analysis/relative_errors/" + training_type + "/Models_mean_std_relative_error_table.txt" , "w")      
            #table_header = "\\textbf{\\ac{IMU} measurement Set} & \\textbf{Human Bone Index} & \\textbf{Subject ID} & \\textbf{Sample Type}"
            #for cols in df_mean_std:
            #    table_header = table_header + " & \\textbf{" + cols[0] + " \\\ " + cols[1].title() + "}"
            #f.write(table_header + "\\\\hline \n")
            #df_mean_std_rows = []
            #for i in range(len(df_mean_std)):
            #    axes_name = df_mean_std.index[i][0]
            #    model_name = df_mean_std.index[i][1]
            #    sample_name = df_mean_std.index[i][2]
            #    bone = model_name.split("_")[1]
            #    id_sampletype = sample_name.split("_")
            #    row_str = axes_name + " & " + bone + " & " + id_sampletype[0] + " & " + id_sampletype[1]
            #    row_content = df_mean_std.loc[df_mean_std.index[i]]
            #    for c in row_content:
            #        row_str = row_str + " & " + str(round(c,2))
            #    f.write(row_str + " \\\ \n")
            #f.close()
            #print("Table for mean and std saved")
            #temp_df = pd.DataFrame()
            #temp_df["Row"]=[ax_samplename_row_relativeerrors[2]]*len(axes)
            #temp_df["Axes"]= [a + "_" + ax_samplename_row_relativeerrors[1] for a in axes]
            #temp_df["RelativeError"]=list(ax_samplename_row_relativeerrors[3])
            #df = pd.concat((df, temp_df), axis=0)
                    #create mean and std for each axis ("transpoose") to see how big the error is for which axes for which files and then p
                    #put in error chart

               
                #    print(df)
                #    df.sort_values(by=['Axes'])
                #    df_matrix = df.pivot_table(index="Row", columns="Axes", values="RelativeError").sort_values(by=['Row'],ascending=False)
                #    plt.figure(figsize=(30,30))
                #    ax = sns.heatmap(df_matrix)
                #    ax.set(xlabel="Axes", ylabel="Rows in Test File")
                #    plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + model_name + "_relative_errors_per_axes_heatmap.png", dpi=1200)     
                #    print("finished saving plot")
                #    plt.clf()
                #axes_label_location = np.arange(len(axes))  # the label locations
                #rects = ax.bar(axes_label_location, measurement, width, label=attribute)

def create_heatmaps_for_relative_error_per_model_per_axe():
    for training_type in ["SIDEPLANKLEFT", "SIDEPLANKRIGHT"]:#"PLANKHOLD", "FULLSQUAT"]: #
        axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
        columns = ["Axes", "Model", "Sample"]
        columns.extend(axes)
        df_all = pd.DataFrame(columns=columns)
        for id in ["14", "9", "10", "7", "8", "1"]:
            f = open(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + id + "_models_mean_std_relative_error_table.txt" , "r")      
            
            df_mean_std = df_all.groupby(['Axes','Model','Sample']).agg(['mean'])#, 'std'])
            gb_axes = df_mean_std.groupby(['Axes'])

            for axes_name in gb_axes.groups:
                samples = gb_axes.get_group((axes_name,))
                samples = samples.reset_index()
                axes = ["9x_w", "9x_x", "9x_y", "9x_z", "6x_w", "6x_x", "6x_y", "6x_z", "Magnetometer_x", "Magnetometer_y", "Magnetometer_z", "Accelerometer_x", "Accelerometer_y", "Accelerometer_z", "Linear Acceleration_x", "Linear Acceleration_y", "Linear Acceleration_z"]  
                columns = ["Axes", "Model", "Sample"]
                columns.extend(axes) 
                samples.columns = columns
                if "no_magn_" in axes_name:
                    samples = samples.loc[:,~samples.columns.str.contains('Magn')]
                if "no_magn9x" in axes_name:
                    samples = samples.loc[:,~samples.columns.str.contains('Magn')]
                    samples = samples.loc[:,~samples.columns.str.contains('9x')]
                neg_samples = samples.loc[samples['Sample'].str.contains('Negative')]
                neg_samples = neg_samples.drop(['Axes'], axis=1)
                neg_samples = neg_samples.drop(['Sample'], axis=1)
                cols = [s.split("_")[1] for s in neg_samples['Model'].values]
                neg_samples = neg_samples.drop(['Model'], axis=1)
                index= neg_samples.columns
                values = np.round(neg_samples.T.values, 2)
                df = pd.DataFrame(values, index=index, columns=cols)
                plt.figure(figsize=(15,15))
                sns.heatmap(df, annot=True, cmap="crest", annot_kws={"fontsize":14}, vmin=-50, vmax=50)
                plt.xticks(rotation=0) 
                plt.tight_layout()
                plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + axes_name + "_relative_errors_per_axes_heatmap_negative_samples.png", dpi=1200)     
                #plt.show()
                plt.clf()
            
                pos_samples = samples.loc[samples['Sample'].str.contains('Positive')]
                pos_samples = pos_samples.drop(['Sample'], axis=1)
                gb_pos_samples = pos_samples.groupby(['Axes', 'Model']).agg(['mean'])
                cols = [i[1].split("_")[1] for i in gb_pos_samples.index]
                index= [c[0] for c in gb_pos_samples.columns]
                values = np.round(gb_pos_samples.T.values, 2)
                df = pd.DataFrame(values, index=index, columns=cols)
                plt.figure(figsize=(15,15))
                sns.heatmap(df, annot=True, cmap="crest", annot_kws={"fontsize":14}, vmin=-50, vmax=50)
                plt.xticks(rotation=0) 
                plt.tight_layout()
                plt.savefig(thisdir + "/core/analysis/relative_errors/" + training_type + "/" + axes_name + "_relative_errors_per_axes_heatmap_positive_samples_mean.png", dpi=1200)     
                #plt.show()
                plt.clf()

def calculate_mean_std_per_measurement():
    data1 = [0.93, 0.89, 0.94, 0.89, 0.9, 0.93, 0.94, 0.74, 0.93, 0.86]
    data2 = [0.98, 0.54, 0.96, 0.85, 0.82, 0.84, 0.99, 0.91, 0.94, 0.88]
    data3 = [0.85, 0.91, 0.96, 0.93, 0.92, 0.91, 0.98, 0.78, 0.93, 0.81]

    m1 = statistics.mean(data1)
    s1 = statistics.stdev(data1)
    m2 =statistics.mean(data2)
    s2 = statistics.stdev(data2)
    m3 =statistics.mean(data3)
    s3 = statistics.stdev(data3)
    print("All Axes & " + str(m1) + " & " + str(round(s1, 3)) + " \\\ ")
    print("No Magnetometer & " + str(m2) + " & " + str(round(s2, 3)) + " \\\ ")
    print("No Magnetometer \& 9x & " + str(m3) + " & " + str(round(s3, 3)) + " \\\ ")

#if __name__ == "__main__":
def exercise_recognition_performance_plot():
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
    
    plt.xlabel('Subject ID')
    plt.ylabel('Accuracy')
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