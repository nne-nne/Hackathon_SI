# -*- coding: utf-8 -*-
import txt as txt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import PIL.Image
import base64
import helper
from io import BytesIO
from intelligence import Action, decide

import numpy as np
import sys


class Enemy:
    def __init__(self, _centre):
        self.centre = _centre
        self.speed = [0, 0]
        self.refreshed = False

    def update(self, position):
        self.speed = get_delta_pos(self.centre, position)
        self.centre = position
        self.refreshed = True

    def __str__(self):
        return str(self.centre) + ", " + str(self.speed) + " " + str(self.refreshed)


def update_enemies():
    # opuszczam flagi wrogom
    for enemy in enemies:
        enemy.refreshed = False
    positions = get_enemy_positions(30, 20, enemy_x_speeds, np_img)
    #print("positions:", positions)
    positions_removed = []
    # updatuję wrogów
    for position in positions:
        for enemy in enemies:
            dpos = get_delta_pos(position, enemy.centre)
            if abs(dpos[0] < 5) and abs(dpos[1] < 5):
                enemy.update(position)
                positions_removed.append(position)
                break
    # niezupdatowanych wyrzucam, bo pewnie nie istnieją
    for enemy in enemies:
        if not enemy.refreshed:
            enemies.remove(enemy)

    # dodaję nowych wrogów
    for position in positions:
        if position not in positions_removed:
            enemies.append(Enemy(position))


def should_fire(tolerance):
    for enemy in enemies:
        speed = enemy.speed
        centre = enemy.centre
        s1 = player_pos - centre[1]
        s2 = master_height - centre[0] - actor_size[1]
        if speed[1] != 0 and speed[0] != player_bullet_speed:
            accuracy = abs(s1 / speed[1] - s2 / (player_bullet_speed - speed[0]))
            if accuracy <= tolerance:
                return True
    return False


def should_fire_at_enemy(enemy, tolerance):
    speed = enemy.speed
    if speed[1] == 0:
        print("0 speed")
        return False
    centre = enemy.centre
    s1 = player_pos - centre[1]
    s2 = master_height - centre[0] - actor_size[1]
    accuracy = abs(s1 / speed[1] - s2 / (player_bullet_speed - speed[0]))
    if accuracy <= tolerance:
        return True
    else:
        return False


def print_board(arr):
    board = ""
    for row in range(master_height):
        for col in range(master_width):
            pixel = arr[row][col][:3]
            if helper.pixel_bcg(pixel):
                board += " "
            else:
                board += "*"
        board += "\n"
    print(board)


def get_player_pos_raw(bottom_row):
    for i in range(len(bottom_row)):
        pixel = bottom_row[i]
        if not helper.pixel_bcg(pixel):
            return int(i + actor_size[0]/2)


def get_player_pos(bottom_row):
    for i in range(len(bottom_row)):
        pixel = bottom_row[i]
        for color in player_colors:
            if helper.pixel_eq(pixel, color):
                return int(i + actor_size[0]/2)
    return player_pos


def get_player_color(bottom_row, player_pos):
    return bottom_row[player_pos]


def is_player_cornered(player_pos):
    return player_pos < actor_size[0] or player_pos > master_width - actor_size[0]


def scan_for_bullets_row(img, player_pos, y, width):
    #print(int(height-1-distance), int(player_pos-width/2))
    start_x = max(0, int(player_pos-width/2))
    for i in range(width):
        x = start_x + i
        if x >= master_width:
            break

        pixel = img[y][x][:3]
        if not helper.pixel_bcg(pixel):
            return True, x
    return False, 0


def scan_for_bullets(img, player_pos, distance, width, depth, step):
    for i in range(depth):
        y = int(master_height - 1 - (distance + i * step))
        scan_result, x = scan_for_bullets_row(img, player_pos, y, width)
        if scan_result:
            return True, (x, y)
    return False, 0


def to_center(player_pos):
    center_x = master_width / 2
    if player_pos < center_x:
        return Action.RIGHT
    else:
        return Action.LEFT


def get_image():
    base64_string = browser.execute_script(jss).split(',')[1]
    decoded = base64.b64decode(base64_string)
    im_file = BytesIO(decoded)  # convert image to file-like object
    img = PIL.Image.open(im_file)
    return np.array(img)


def is_enemy(img, position):
    if position[0] < 0 or position[0] >= master_width or position[1] < 0 or position[1] >= master_height:
        return False
    if not helper.pixel_bcg(img[position[1]][position[0]]):
        if position[0] > actor_size[0]/2 and not helper.pixel_bcg(img[position[1]][int(position[0]-actor_size[0]/2)]):
            return True
        if position[0] < master_width - actor_size[0]/2 - 1 and not helper.pixel_bcg(img[position[1]][int(position[0]+actor_size[1]/2)]):
            return True
    return False


# to już późno pisana funkcja jest, nie śmiejcie się proszę 🥺🥺🥺
def get_enemy_centre(img, position):
    x_pos = int(position[1])
    y_pos = int(position[0])
    left = x_pos
    right = x_pos
    up = y_pos
    down = y_pos
    while left > 0 and not helper.pixel_bcg(img[y_pos][left]):
        left -= 1
    while right < master_width-1 and not helper.pixel_bcg(img[y_pos][right]):
        right += 1
    while up > 0 and not helper.pixel_bcg(img[up][x_pos]):
        up -= 1
    while down < master_height-1 and not helper.pixel_bcg(img[down][x_pos]):
        down += 1
    return [int((down + up) / 2), int((left + right)/2)]


def get_delta_pos(pos1, pos2):
    delta_pos = []
    for i in range(len(pos1)):
        delta_pos.append(int((pos2[i] - pos1[i])/dframe))
    return delta_pos


def get_enemy_positions(layers_c, step, speed_hor, img):
    enemy_positions = []
    for layer in range(layers_c):
        y_abs = actor_size[1] + (layer+1) * step
        for horizontal_speed in speed_hor:
            x_pos = player_pos + (y_abs - actor_size[1]) * horizontal_speed / (player_bullet_speed + 0.2) #vertical_speed
            y_pos = master_height - y_abs
            pos = [int(x_pos), int(y_pos)]
            if is_enemy(img, pos):
                enemy_centre = get_enemy_centre(img, [y_pos, x_pos])
                enemy_positions.append(enemy_centre)
    return enemy_positions
                # if y_pos - prev_aim_pos[0] == 0 and x_pos - prev_aim_pos[1] == 0:
                #     new_enemy_centre = get_enemy_centre(img, [y_pos, x_pos])
                #     print("dpos: ", get_delta_pos(prev_enemy_centre, new_enemy_centre))
                # else:
                #     pass
                #     print("target changed")
                #temp_prev_enemy_centre = get_enemy_centre(img, [y_pos, x_pos])
                # prev_enemy_centre[0] = temp_prev_enemy_centre[0]
                # prev_enemy_centre[1] = temp_prev_enemy_centre[1]
                # prev_aim_pos[0] = y_pos
                # prev_aim_pos[1] = x_pos



jss = '''
        var canvas = document.getElementById("game");
        return canvas.toDataURL("image/png");
        '''
options = Options()
options.headless = True
np.set_printoptions(threshold=sys.maxsize)

max_time = 120

browser = webdriver.Chrome("C:/Users/adaml/Desktop/Hackathon_SI/chrome/chromedriver_win32/chromedriver.exe")

script = open('game.js', 'r')

start_time = time.time()


master_width = 960
master_height = 540
actor_size = [60, 20]
bullet_size = [8, 20]
bullet_speed = 6
player_speed = 8
player_bullet_speed = 8
player_pos = 480
scanner_dist = int(player_speed*actor_size[0]/2/bullet_speed)
player_colors = [[255, 0, 0], [255, 255, 255]]
enemy_x_speeds = [-3, -2, 2, 3]
enemy_y_speeds = [0.1, 0.2, 0.3]
fps = 50

prev_enemy_centre = [0, 0]
prev_aim_pos = [0, 0]
frame = 0

enemies = []


try:
    browser.get('file:///C:/Users/adaml/Desktop/Hackathon_SI/index.html')
    while time.time() - start_time < max_time:
        nframe = int((time.time() - start_time) * fps)
        dframe = nframe - frame
        frame = nframe
        #print(dframe)

        np_img = get_image()
        player_pos = get_player_pos(np_img[master_height - 1])
        scan_result, bullet_pos = scan_for_bullets(np_img, player_pos, 30, 100, 30, 4)

        action = Action.NONE
        if is_player_cornered(player_pos):
            action = to_center(player_pos)  # I want to breeaak freeeeee!
        elif scan_result:
            if is_player_cornered(player_pos):
                action = to_center(player_pos)
            else:
                if bullet_pos[0] < player_pos:
                    action = Action.RIGHT
                else:
                    action = Action.LEFT
        else:  # Brak zagrażających pocisków
            if is_player_cornered(player_pos):
                action = to_center(player_pos)

        dispatch_action(action)
        update_enemies()
        if should_fire(6):
            ActionChains(browser).key_down(Keys.SPACE).perform()
        else:
            ActionChains(browser).key_up(Keys.SPACE).perform()

finally:
    browser.close()