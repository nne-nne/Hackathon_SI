import random
import enum
from game_constants import *


class Action(enum.Enum):
    NONE = 0
    RIGHT = 1
    LEFT = 2


def pixel_bcg(pixel):
    if pixel[0] == pixel[1] and pixel[1] == pixel[2]:
        return True
    else:
        return False


def scan_for_bullets_row(img, player_pos, y, width):
    #print(int(height-1-distance), int(player_pos-width/2))
    start_x = max(0, int(player_pos-width/2))
    for i in range(width):
        x = start_x + i
        if x >= master_width:
            break

        pixel = img[y][x][:3]
        if not pixel_bcg(pixel):
            return True, x
    return False, 0


def scan_for_bullets(img, player_pos, distance, width, depth, step):
    for i in range(depth):
        y = int(master_height - 1 - (distance + i * step))
        scan_result, x = scan_for_bullets_row(img, player_pos, y, width)
        if scan_result:
            return True, (x, y)
    return False, 0


def to_center(player_pos) -> Action:
    center_x = master_width / 2
    if player_pos < center_x:
        return Action.RIGHT
    else:
        return Action.LEFT


def is_player_cornered(player_pos):
    return player_pos < actor_size[0] or player_pos > master_width - actor_size[0]
