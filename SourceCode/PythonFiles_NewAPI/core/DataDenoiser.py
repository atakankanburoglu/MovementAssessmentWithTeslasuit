import numpy as np
import pandas as pd

class DataDenoiser:

    @staticmethod
    def denoise_df_column_for_feedback_model_training(df, measurement_sets):
        df = df.drop(['ExerciseType'], axis=1)
        df = df.drop(['Timestamp'], axis=1)
        df = df.loc[:,~df.columns.str.startswith('Spine')]
        df = df.loc[:,~df.columns.str.startswith('Chest')]
        df = df.loc[:,~df.columns.str.startswith('LeftShoulder')]
        df = df.loc[:,~df.columns.str.startswith('RightShoulder')]
        df = df.loc[:,~df.columns.str.contains('Foot')]
        df = df.loc[:,~df.columns.str.contains('Hand')]
        if len(measurement_sets) > 0:
            measurement_sets_join = "|".join(list(measurement_sets)) 
            df = df.loc[:,~df.columns.str.contains(measurement_sets_join)] 
        return df
    
    @staticmethod
    def denoise_df_column_for_feedback_model_testing(df, measurement_sets):
        df = df.drop(['ExerciseType'], axis=1)
        df = df.drop(['Timestamp'], axis=1)
        df = df.loc[:,~df.columns.str.startswith('Spine')]
        df = df.loc[:,~df.columns.str.startswith('Chest')]
        df = df.loc[:,~df.columns.str.startswith('LeftShoulder')]
        df = df.loc[:,~df.columns.str.startswith('RightShoulder')]
        df = df.loc[:,~df.columns.str.contains('Foot')]
        df = df.loc[:,~df.columns.str.contains('Hand')]
        df = df.loc[:,~df.columns.str.contains('gyro')]
        if len(measurement_sets) > 0:
            measurement_sets_join = "|".join(list(measurement_sets)) 
            df = df.loc[:,~df.columns.str.contains(measurement_sets_join)] 
        return df


    @staticmethod 
    def denoise_df_for_exercise_recognition_model_training(df):
        df = df.drop(['Timestamp'], axis=1)
        df = df.loc[:,~df.columns.str.startswith('Spine')]
        df = df.loc[:,~df.columns.str.startswith('Chest')]
        df = df.loc[:,~df.columns.str.startswith('LeftShoulder')]
        df = df.loc[:,~df.columns.str.startswith('RightShoulder')]
        df = df.loc[:,~df.columns.str.contains('Foot')]
        df = df.loc[:,~df.columns.str.contains('Hand')]
        df = df.loc[:,~df.columns.str.contains('magn')]
        df = df.loc[:,~df.columns.str.contains('linearAccel')]
        df = df.loc[:,~df.columns.str.contains('9x')]
        df = df.loc[:,~df.columns.str.contains('6x')]
        return df
    
    @staticmethod 
    def denoise_df_for_exercise_recognition_model_testing(df):
        df = df.drop(['ExerciseType'], axis=1)
        df = df.drop(['Timestamp'], axis=1)
        df = df.loc[:,~df.columns.str.startswith('Spine')]
        df = df.loc[:,~df.columns.str.startswith('Chest')]
        df = df.loc[:,~df.columns.str.startswith('LeftShoulder')]
        df = df.loc[:,~df.columns.str.startswith('RightShoulder')]
        df = df.loc[:,~df.columns.str.contains('Foot')]
        df = df.loc[:,~df.columns.str.contains('Hand')]
        df = df.loc[:,~df.columns.str.contains('magn')]
        df = df.loc[:,~df.columns.str.contains('linearAccel')]
        df = df.loc[:,~df.columns.str.contains('9x')]
        df = df.loc[:,~df.columns.str.contains('6x')]
        return df

    @staticmethod
    def denoise_gyro(df, t_gyro):
        minus_t_gyro = 0 - t_gyro
        gyro_df = df.loc[:,df.columns.str.contains('gyro')]
        gyro_df = gyro_df.drop(gyro_df[(gyro_df[gyro_df.columns[0]] > t_gyro) | (gyro_df[gyro_df.columns[0]] < minus_t_gyro)].index)
        gyro_df = gyro_df.drop(gyro_df[(gyro_df[gyro_df.columns[1]] > t_gyro) | (gyro_df[gyro_df.columns[1]] < minus_t_gyro)].index)
        gyro_df = gyro_df.drop(gyro_df[(gyro_df[gyro_df.columns[2]] > t_gyro) | (gyro_df[gyro_df.columns[2]] < minus_t_gyro)].index)
        gyro_df = gyro_df.drop_duplicates()
        return gyro_df

