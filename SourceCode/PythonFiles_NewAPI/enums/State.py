from enum import Enum


class State(Enum):
    IDLE = 0
    INIT = 1
    RUNNING = 2
    FINISHED = 3
