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
from intelligence import *
from game_constants import *
import os

import re
import json

import numpy as np
import sys


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


def dispatch_action(action):
    if action == Action.RIGHT:
        ActionChains(browser).key_up(Keys.ARROW_LEFT).perform()
        ActionChains(browser).key_down(Keys.ARROW_RIGHT).perform()
    elif action == Action.LEFT:
        ActionChains(browser).key_up(Keys.ARROW_RIGHT).perform()
        ActionChains(browser).key_down(Keys.ARROW_LEFT).perform()
    else:
        ActionChains(browser).key_up(Keys.ARROW_LEFT).perform()
        ActionChains(browser).key_up(Keys.ARROW_RIGHT).perform()


def get_image():
    base64_string = browser.execute_script(jss).split(',')[1]
    decoded = base64.b64decode(base64_string)
    im_file = BytesIO(decoded)  # convert image to file-like object
    img = PIL.Image.open(im_file)
    return np.array(img)


jss = '''
        var canvas = document.getElementById("game");
        return canvas.toDataURL("image/png");
        '''
options = Options()
options.headless = True
np.set_printoptions(threshold=sys.maxsize)

max_time = 120

browser = webdriver.Chrome(os.path.abspath("chrome/chromedriver_win32/chromedriver.exe"))

script = open('game.js', 'r')

start_time = time.time()

checked_bullets = False

try:
    browser.get('file:///' + os.path.abspath("index.html"))
    while time.time() - start_time < max_time:
        np_img = get_image()
        #print_board(np_img)
        player_pos = get_player_pos(np_img[master_height - 1])
        #print(time.time() - start_time)
        #print(player_pos)
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

        # Shooting
        ActionChains(browser).key_down(Keys.SPACE).perform()
        ActionChains(browser).key_up(Keys.SPACE).perform()



finally:
    browser.close()

# input example:
#    ActionChains(browser).key_down(Keys.SPACE).key_up(Keys.SPACE).perform()
#    time.sleep(3)



# trash
##try:
        #    print(browser.execute_script('return map.data'))
        #except:
        #    print("noooo")
        #print(browser.execute_script("return document.getElementsByTagName(\"script\")[0].get_dom_attribute('src')"))
        #info = browser.find_element(By.XPATH, "//script")
        #print(info.get_dom_attribute("innerHTML"))
        #print("score: ", browser.execute_script("return document.getElementsByTagName('script')[0].innerHTML"))
        #browser.
        #m = re.findall(r'var message = *', flags=re.S)[0]
        #data = json.loads(m)

        #print(data['datasets'][0]['data'])

   # jss = '''const getCircularReplacer = () => {
   #           const seen = new WeakSet();
   #           return (key, value) => {
   #             if (typeof value === "object" && value !== null) {
   #               if (seen.has(value)) {
   #                 return;
   #               }
   #               seen.add(value);
   #             }
   #             return value;
   #           };
   #         };
#
   #         return JSON.stringify(this.data, getCircularReplacer());
   #         '''
   # js_data = json.loads(browser.execute_script(jss))
   # print(js_data)
#
# print(get_player_pos(np_img[height-1]))
#         if not checked_bullets and time.time() - start_time > 3:
#             print(get_bullets_pos(np_img))
#             checked_bullets = True