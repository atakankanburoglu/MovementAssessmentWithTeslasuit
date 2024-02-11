from enum import Enum


class State(Enum):
    IDLE = 1
    INIT = 2
    RUNNING = 3
    FINISHED = 4
