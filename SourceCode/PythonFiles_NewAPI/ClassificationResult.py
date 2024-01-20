from enum import Enum


class ClassificationType(Enum):
    NONE = 1
    POSE = 2
    REP = 3


class ClassificationExercise(Enum):
    NEGATIVE = 1
    PLANKHOLD = 2
    SIDEPLANKRIGHT = 3
    SIDEPLANKLEFT = 4
    FULLSQUAT = 5
   # PUSHUP = 2
   # SQUAT = 3
   # LUNGE = 4
