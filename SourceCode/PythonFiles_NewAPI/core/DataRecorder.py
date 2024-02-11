import pandas as pd

import Config
from Plotter import Plotter
from data.DataAccess import DataAccess


class DataRecorder:
    def __init__(self, subjectId, trainingType):
        self.subjectId = subjectId
        self.trainingType = trainingType
        self.recordedData = []
        self.recordedSegments = []
        #self.plotter = Plotter()

    def log_data(self, suit_data, segmentDetected):
        self.recordedData.append(suit_data)
        self.recordedSegments.append(segmentDetected)

    def save_data_to_csv(self, sampleType):
        with open("/samples/" + subjectId + '_' + trainingType + +'_' + sampleType + '.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            recordedSegmentsIt = iter(recordedSegments)
            for row in recordedData:
                writer.writerow(next(recordedSegmentsIt), row)

    def dataToDataframe(self):
        dataFrame = pd.DataFrame(self.recordedData, columns=DataAccess.result_columns())
        return dataFrame

    #def errorToDataframe(self):
    #    columns = ["timestamp"]
    #    columns.extend(DataAccess.get_joints_properties_names(Config.streamedJoints))
    #    dataFrame = pd.DataFrame(self.recordedErrors, columns=columns)
    #    return dataFrame