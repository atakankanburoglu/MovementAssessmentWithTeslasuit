from enum import Enum

class ApplicationMode(Enum):
    IDLE = 1
    TRAINING = 2
    MODELCREATION = 3
    TESTING = 4
    FEEDBACK = 5
