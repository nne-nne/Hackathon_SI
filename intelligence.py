import enum
from game_constants import *


DANGER_TOLERANCE = 5
PREDICTION_FRAMECOUNT = 1  # liczba ramek w przód, na którą trzeba złożyć przewidywania
CORNERED_TOLERANCE = 6


class Action(enum.Enum):
    NONE = 0
    RIGHT = 1
    LEFT = 2


class ImmediateDangerReport:
    def __init__(self, left_safe: bool, stay_safe: bool, right_safe: bool):
        self.left_safe = left_safe
        self.stay_safe = stay_safe
        self.right_safe = right_safe

    def is_action_safe(self, action: Action):
        if action == Action.LEFT:
            return self.left_safe
        if action == Action.RIGHT:
            return self.right_safe
        return self.stay_safe

    def redirect_action(self, action: Action) -> Action:
        """Zmienia akcję na jakąś inną, jeśli jest niebezpieczna"""
        if self.is_action_safe(action):
            return action  # chill

        actions = [Action.NONE, Action.RIGHT, Action.LEFT]
        for alternative in actions:
            if alternative == action or not self.is_action_safe(alternative):
                continue
            return alternative  # Ratunek
        return action  # Wszyscy zginiemy


def pixel_bcg(pixel):
    if pixel[0] == pixel[1] and pixel[1] == pixel[2]:
        return True
    else:
        return False


def scan_for_bullets_row(img, player_pos, y, width):
    #print(int(height-1-distance), int(player_pos-width/2))
    for i in range(int(width/2)):
        for x in [player_pos - i, player_pos + i]:
            if x >= master_width:
                continue

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
    """Czy gracz jest przyparty do ściany"""
    if player_pos < player_width/2 + CORNERED_TOLERANCE:
        return True
    if player_pos > master_width - player_width/2 - CORNERED_TOLERANCE:
        return True
    return False


def hypothetical_position(player_pos, action, framecount):
    """Pozycja, którą osiągnie gracz w następnych klatkach danej akcji"""
    if action == Action.RIGHT:
        return min(int(master_width - player_width/2), player_pos + player_speed * framecount)
    if action == Action.LEFT:
        return max(int(player_width / 2), player_pos - player_speed * framecount)
    return player_pos  # brak zmiany pozycji


def is_bullet_inside(img, center, width, height):
    start_x = int(center[0] - width/2)
    start_y = int(center[1] - height/2)
    for i in range(width):
        x = start_x + i
        if x >= master_width:
            continue
        for j in range(height):
            y = start_y + j

            pixel = img[y][x][:3]
            if not pixel_bcg(pixel):
                return True
    return False


def is_action_safe(img, player_pos, action):
    future_pos = hypothetical_position(player_pos, action, PREDICTION_FRAMECOUNT)

    danger_rect_height = player_height + bullet_speed * PREDICTION_FRAMECOUNT + DANGER_TOLERANCE * 2

    target_center_y = int(player_y - danger_rect_height/2)
    danger_rect_center = (int((future_pos + player_pos)/2), target_center_y)
    danger_rect_width = abs(future_pos - player_pos) + player_width + DANGER_TOLERANCE * 2
    return is_bullet_inside(img,
                            danger_rect_center,
                            danger_rect_width,
                            danger_rect_height)


def immediate_danger(img, player_pos) -> ImmediateDangerReport:
    """Jak poszczególne ruchy mogą być natychmiast ukarane przez pociski"""
    report = ImmediateDangerReport(False, False, False)  # Inicjalizacja jako niebezpieczne

    if is_action_safe(img, player_pos, Action.NONE):
        report.stay_safe = True
    if is_action_safe(img, player_pos, Action.LEFT):
        report.left_safe = True
    if is_action_safe(img, player_pos, Action.RIGHT):
        report.right_safe = True

    return report


def try_prioritize_immediate(immediate_report: ImmediateDangerReport):
    if immediate_report.left_safe and not immediate_report.right_safe and not immediate_report.stay_safe:
        return True, Action.LEFT
    if immediate_report.right_safe and not immediate_report.left_safe and not immediate_report.stay_safe:
        return True, Action.RIGHT
    if immediate_report.stay_safe and not immediate_report.left_safe and not immediate_report.right_safe:
        return True, Action.NONE

    return False, Action.NONE


def preventive_action(img, player_pos):
    """Decyzje, które podejmuje bot, gdy nie ma bezpośrednich zagrożeń"""
    scan_result, bullet_pos = scan_for_bullets(img, player_pos, 30, 100, 30, 4)
    if not scan_result:
        return Action.NONE

    if scan_result:
        if is_player_cornered(player_pos):
            return to_center(player_pos)  # I want to breeaak freeeeee!
        if bullet_pos[0] < player_pos:
            return Action.RIGHT
        else:
            return Action.LEFT
