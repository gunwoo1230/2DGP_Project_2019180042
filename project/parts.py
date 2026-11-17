# 진짜 그림 (resource/parts): parts.json의 크기·기준점과 이미지
# 그림은 게임 화면 크기(1배) 그대로 그림, 기준점의 "~_row"는 그림 위에서 잰 픽셀 줄, "~_x"·"plank_~"는 왼쪽에서 잰 픽셀
import json

from pico2d import load_image

import config

PARTS_DIR = 'resource/parts/'

# 크기·기준점은 그림을 불러오기 전(타일 정의)에도 쓰므로 바로 읽음
with open(PARTS_DIR + 'parts.json', encoding='utf-8') as f:
    INFO = json.load(f)

images = {}


def size(name):
    # (가로, 세로)
    return tuple(INFO[name]['size'])


def image(name):
    # 처음 쓸 때 한 번만 불러옴
    if name not in images:
        images[name] = load_image(PARTS_DIR + name + '.png')
    return images[name]


def draw_top_left(name, left, top, flip=False, w=None):
    # 그림 왼쪽 위 모서리를 (left, top)에 (화면 좌표), flip이면 좌우 뒤집음, w가 있으면 가로만 그 폭으로 늘려 그림
    w0, h = size(name)
    w = w0 if w is None else w
    if flip:
        image(name).composite_draw(0, 'h', left + w / 2, top - h / 2, w, h)
    else:
        image(name).draw(left + w / 2, top - h / 2, w, h)


def draw_center(name, cx, cy):
    image(name).draw(cx, cy)


def draw_bottom_center(name, cx, bottom):
    image(name).draw(cx, bottom + size(name)[1] / 2)


def draw_window(name, x, y, dx=0):
    # 창틀 발판 (x ~ x + 판자 폭, 높이 y) 위의 창문, 가운데 = 발판 가운데 (화면 좌표)
    # 아랫변은 창틀 윗면에서 WINDOW_DROP만큼 내려 창틀 뒤로 들어가게 (그림만)
    plank = INFO['sill']['plank_right'] - INFO['sill']['plank_left']
    draw_bottom_center(name, x + plank / 2 + dx, y - config.WINDOW_DROP)


def draw_sill(x, y):
    # 판자 왼쪽 끝이 x, 판자 윗면이 y에 오게 (창문보다 나중에 그림)
    info = INFO['sill']
    draw_top_left('sill', x - info['plank_left'], y + info['plank_top_row'])
