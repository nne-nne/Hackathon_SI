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
from io import BytesIO
from intelligence import *
from game_constants import *

import re
import json

import numpy as np
import sys


#def count_colors(arr):
#    colors = []
#    for row in range(height):
#        for col in range(width):
#            pixel = arr[row][col][:3]
#            is_new = True
#            for color in colors:
#                if color[0] == pixel[0] and color[1] == pixel[1] and color[2] == pixel[2]:
#                    is_new = False
#                    break
#            if is_new:
#                colors.append(pixel)
#
#    print(colors)

def pixel_eq(pixel, value):
    if pixel[0] == value[0] and pixel[1] == value[1] and pixel[2] == value[2]:
        return True
    else:
        return False


def print_board(arr):
    board = ""
    for row in range(master_height):
        for col in range(master_width):
            pixel = arr[row][col][:3]
            if pixel_bcg(pixel):
                board += " "
            else:
                board += "*"
        board += "\n"
    print(board)


def get_player_pos_raw(bottom_row):
    for i in range(len(bottom_row)):
        pixel = bottom_row[i]
        if not pixel_bcg(pixel):
            return int(i + actor_size[0]/2)


def get_player_pos(bottom_row, player_color):
    for i in range(len(bottom_row)):
        pixel = bottom_row[i]
        if pixel_eq(pixel, player_color):
            return int(i + actor_size[0]/2)
    return player_pos


def get_player_color(bottom_row, player_pos):
    return bottom_row[player_pos]


def is_bullet_corner(img, pos):
    color = img[pos[0], pos[1]]
    if pixel_bcg(color):
        return False
    if not pixel_eq(img[pos[0]+bullet_size[0], pos[1]], color):
        return False
    if pixel_eq(img[pos[0] + bullet_size[0] + 1, pos[1]], color):
        return False
    if not pixel_eq(img[pos[0], pos[1] + bullet_size[1]], color):
        return False
    return True


def get_bullets_pos(img):
    bullets = []
    for row in range(int(bullet_size[0]) + 1, master_height - int(bullet_size[0]) - 1):
        for col in range(int(bullet_size[1]) + 1, master_width - int(bullet_size[1]) - 1):
            if is_bullet_corner(img, [row, col]):
                bullets.append([row + int(bullet_size[0]/2), col + int(bullet_size[1]/2)])
    return bullets






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

browser = webdriver.Chrome("F:/Hackathon/Zad3/Hackathon_SI/chrome/chromedriver_win32/chromedriver.exe")

script = open('game.js', 'r')

start_time = time.time()

checked_bullets = False

try:
    browser.get('file:///F:/Hackathon/Zad3/Hackathon_SI/index.html')
    time.sleep(0.1)
    np_img = get_image()
    player_pos = get_player_pos_raw(np_img[master_height - 1])
    player_color = get_player_color(np_img[master_height - 1], player_pos)

    while time.time() - start_time < max_time:
        np_img = get_image()
        #print_board(np_img)
        player_pos = get_player_pos(np_img[master_height - 1], player_color)
        #print(time.time() - start_time)
        #print(player_pos)
        scan_result, bullet_pos = scan_for_bullets(np_img, player_pos, 30, 100, 30, 4)
        action = Action.NONE
        if scan_result:
            if is_player_cornered(player_pos):
                action = to_center(player_pos)
            else:
                if bullet_pos[0] < player_pos:
                    action = Action.RIGHT
                else:
                    action = Action.LEFT
        else:
            if is_player_cornered(player_pos):
                action = to_center(player_pos)

        # Dispatch action
        if action == Action.RIGHT:
            ActionChains(browser).key_up(Keys.ARROW_LEFT).perform()
            ActionChains(browser).key_down(Keys.ARROW_RIGHT).perform()
        elif action == Action.LEFT:
            ActionChains(browser).key_up(Keys.ARROW_RIGHT).perform()
            ActionChains(browser).key_down(Keys.ARROW_LEFT).perform()
        else:
            ActionChains(browser).key_up(Keys.ARROW_LEFT).perform()
            ActionChains(browser).key_up(Keys.ARROW_RIGHT).perform()



        # action = decide()
        # if action == Action.LEFT:
        #     ActionChains(browser).key_up(Keys.ARROW_RIGHT).perform()
        #     ActionChains(browser).key_down(Keys.ARROW_LEFT).perform()
        # elif action == Action.RIGHT:
        #     ActionChains(browser).key_up(Keys.ARROW_LEFT).perform()
        #     ActionChains(browser).key_down(Keys.ARROW_RIGHT).perform()

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