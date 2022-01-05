import random
import enum


class Action(enum.Enum):
    NONE = 0
    RIGHT = 1
    LEFT = 2


def decide():
    if random.random() < 0.5:
        return Action.RIGHT
    else:
        return Action.LEFT