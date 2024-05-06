import pandas as pd

import os
import Config
import time
from Plotter import Plotter
from data.DataAccess import DataAccess
import csv

class DataRecorder:
    def __init__(self, header):
        self.header = header
        self.recordedData = []
        self.recordedSegments = []

    def log_data(self, suit_data):
        self.recordedData.append(suit_data)

    def save_data_to_csv(self, sample_data):
        t = time.time()
        with open("core/samples/" + sample_data.subjectId + '_' + sample_data.trainingType +'_' + sample_data.sampleType +'_' + str(int(t)) + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for row in self.recordedData:
                writer.writerow(row)

   