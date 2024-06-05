import pandas as pd
import os
import csv
import shutil
import glob
import copy
import numpy as np
from core.DataDenoiser import DataDenoiser

class DataPreprocessor:

    @staticmethod
    def preprocess_data_for_feedback_model(id_training_dict, leave_one_out_id, measurement_sets, t_gyro):
        training_dict = {}
        validation_dict = {}
        for id, dfs in id_training_dict.items():
            for df in dfs:
                i = 1
                df = DataDenoiser.denoise_df_column_for_feedback_model_training(df, measurement_sets)
                mean_std_df = df.agg(['mean', 'std'])
                humanboneindex_dfs = np.split(df, np.arange(int(len(df.columns)/10), len(df.columns), int(len(df.columns)/10)), axis=1)
                for humanboneindex_df in humanboneindex_dfs:
                    humanboneindex_df = humanboneindex_df.reset_index(drop=True)
                    gyro_df = DataDenoiser.denoise_gyro(humanboneindex_df, t_gyro)
                    a = 0
                    boneindexList = []
                    gyroXList = []
                    gyroYList = []
                    gyroZList = []
                    meanList = []
                    stdList = []
                    for axis_name, axis in  humanboneindex_df.items():
                        if 'gyro' not in axis_name:
                            boneindexList.extend([a]*gyro_df.shape[0])
                            gyroXList.extend(gyro_df.iloc[:,0].values)
                            gyroYList.extend(gyro_df.iloc[:,1].values)
                            gyroZList.extend(gyro_df.iloc[:,2].values)
                            meanList.extend([mean_std_df.loc['mean'][axis_name]]*gyro_df.shape[0])
                            stdList.extend([mean_std_df.loc['std'][axis_name]]*gyro_df.shape[0])
                            a = a + 1
                    boneindex_df = pd.DataFrame()
                    boneindex_df['HumanBoneIndex_Axis'] = boneindexList
                    boneindex_df['Gyro_x'] = gyroXList
                    boneindex_df['Gyro_y'] = gyroYList
                    boneindex_df['Gyro_z'] = gyroZList
                    boneindex_df['Mean'] = meanList
                    boneindex_df['Std'] = stdList
                    if id != leave_one_out_id:
                        if axis_name.split('_')[0] in training_dict:
                            training_dict[axis_name.split('_')[0]] = pd.concat((training_dict[axis_name.split('_')[0]], boneindex_df), axis=0)
                        else:
                            training_dict[axis_name.split('_')[0]] = boneindex_df   
                    else:
                        if axis_name.split('_')[0] in validation_dict:
                            validation_dict[axis_name.split('_')[0]] = pd.concat((validation_dict[axis_name.split('_')[0]], boneindex_df), axis=0)
                        else:
                            validation_dict[axis_name.split('_')[0]] = boneindex_df  
        return training_dict, validation_dict

