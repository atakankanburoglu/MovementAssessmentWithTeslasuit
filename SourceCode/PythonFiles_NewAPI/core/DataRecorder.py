import pandas as pd

import os
import Config
import time
from Plotter import Plotter
from data.DataAccess import DataAccess
import csv

class DataRecorder:
    def __init__(self, subjectId, trainingType):
        self.subjectId = subjectId
        self.trainingType = trainingType
        self.recordedData = []
        self.recordedSegments = []
        #self.plotter = Plotter()

    def log_data(self, suit_data):
        self.recordedData.append(suit_data)

    def save_data_to_csv(self, sampleType):
        t = time.time()
        with open("core/samples/" + self.subjectId + '_' + self.trainingType +'_' + sampleType +'_' + str(int(t)) + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for row in self.recordedData:
                writer.writerow(row)

   