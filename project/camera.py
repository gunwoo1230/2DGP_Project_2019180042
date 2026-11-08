# 카메라: 오른쪽으로만 따라감, 월드 좌표 -> 화면 좌표
import config

x = 0.0
max_x = 0.0     # 맵 오른쪽 끝이 플레이 칸 오른쪽에 오는 위치


def init(map_right):
    global x, max_x
    x = 0.0
    max_x = map_right - config.PLAY_RIGHT


def reset():
    global x
    x = 0.0


def follow(box_x):
    # 뒤로는 돌아가지 않음
    global x
    x = min(max(x, box_x - config.CAMERA_FOLLOW_X), max_x)


def to_screen(world_x):
    return world_x - x


def visible(world_x):
    # 화면 밖 물체는 그리지 않음
    return -config.DRAW_MARGIN <= to_screen(world_x) <= config.SCREEN_W + config.DRAW_MARGIN
