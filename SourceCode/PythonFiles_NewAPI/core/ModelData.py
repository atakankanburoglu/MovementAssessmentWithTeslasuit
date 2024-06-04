import ast

class ModelData:
    def __init__(self, subject_ids, exercise_type, algorithm, t_gyro, measurement_sets, timestamp):
        self.subject_ids = subject_ids
        self.exercise_type = exercise_type
        self.algorithm = algorithm
        self.t_gyro = t_gyro
        self.measurement_sets = []
        if len(measurement_sets) > 0:
            self.measurement_sets = measurement_sets.split(",")
        self.timestamp = str(int(timestamp))
    