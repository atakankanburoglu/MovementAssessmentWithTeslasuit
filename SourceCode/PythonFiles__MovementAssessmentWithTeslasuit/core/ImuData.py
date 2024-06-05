

class ImuData:
    def __init__(self, exercise_type, imu_data, timestamp):
        self.exercise_type = exercise_type
        self.imu_data = imu_data
        self.timestamp = timestamp