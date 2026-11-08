# 건물 타일: 타일 정의, 발판, 타일 그리기
import math

from pico2d import load_image

import camera
import config
from config import LEDGE_Y, ROAD_Y, ROOF_Y, TILE_W

PEGS_Y = (270, 330, 450, 510)           # 배수관 발디딤 (390은 창틀이 대신함)


def basic_ledges():
    return [('ledge', a, LEDGE_Y, a + 120, LEDGE_Y) for a in (60, 240, 420)]


TILES = {
    # 'walls': 벽(건물 몸통) x 범위, 'deco': 밟지 않는 장식(배수관·전봇대) 사각형, 'platforms': 발판 선분 (타일 안 좌표)
    'start': {'walls': [], 'deco': [], 'platforms': []},
    'basic': {'walls': [(40, 560)], 'deco': [],
              'platforms': [('roof', 40, ROOF_Y, 560, ROOF_Y)] + basic_ledges()},
    'pipe':  {'walls': [(40, 560)], 'deco': [('pipe', 82, ROAD_Y, 98, ROOF_Y)],
              'platforms': [('roof', 40, ROOF_Y, 560, ROOF_Y)] + basic_ledges()
                           + [('peg', 60, y, 120, y) for y in PEGS_Y]},
    'pole':  {'walls': [(200, 560)], 'deco': [('pole', 92, ROAD_Y, 108, 600)],
              'platforms': [('roof', 200, ROOF_Y, 560, ROOF_Y),
                            ('ledge', 220, LEDGE_Y, 340, LEDGE_Y), ('ledge', 420, LEDGE_Y, 540, LEDGE_Y)]
                           + [('peg', 70, y, 130, y) for y in (270, 330, 390, 450, 510)]},
    'accel': {'walls': [(40, 560)], 'deco': [],
              'platforms': [('accel', 40, 630, 560, ROOF_Y)] + basic_ledges()},
    'gap':   {'walls': [(240, 560)], 'deco': [],
              'platforms': [('roof', 240, ROOF_Y, 560, ROOF_Y),
                            ('ledge', 260, LEDGE_Y, 380, LEDGE_Y), ('ledge', 440, LEDGE_Y, 540, LEDGE_Y)]},
}
# 모든 타일 맨 아래에 도로 (끊기지 않음)
for tile in TILES.values():
    tile['platforms'].insert(0, ('road', 0, ROAD_Y, TILE_W, ROAD_Y))

images = {}


class Platform:
    # 윗면이 밟히는 선분 (월드 좌표)
    def __init__(self, kind, x0, y0, x1, y1):
        self.kind = kind
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1

    def surface_y(self, x):
        # x에서의 윗면 높이, 발판 밖 x는 가까운 끝의 높이
        x = max(self.x0, min(x, self.x1))
        return self.y0 + (self.y1 - self.y0) * (x - self.x0) / (self.x1 - self.x0)

    def covers(self, x):
        # 박스 발 폭이 발판 x 범위와 겹치는지
        return x + config.FOOT_HALF >= self.x0 and x - config.FOOT_HALF <= self.x1


def load_images():
    # 리셋·재시작해도 한 번만 불러옴
    if not images:
        images['road'] = load_image('resource/placeholder/ph_ground.png')
        images['wall'] = load_image('resource/placeholder/ph_wall.png')
        images['deco'] = load_image('resource/placeholder/ph_pipe.png')
        images['roof'] = load_image('resource/placeholder/ph_roof.png')
        images['ledge'] = load_image('resource/placeholder/ph_ledge.png')
        images['peg'] = load_image('resource/placeholder/ph_peg.png')
        images['accel'] = load_image('resource/placeholder/ph_accel.png')


def draw_rect(image, x0, y0, x1, y1):
    image.draw((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0)


def draw_slope(image, x0, y0, x1, y1, thick):
    # 윗면이 선분에 오도록, 가운데를 두께의 절반만큼 선분 아래쪽 수직 방향으로 내림
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    cx = (x0 + x1) / 2 + dy / length * thick / 2
    cy = (y0 + y1) / 2 - dx / length * thick / 2
    image.composite_draw(math.atan2(dy, dx), '', cx, cy, length, thick)


def draw_tile(name, left):
    # 진짜 타일 그림이 오면 이 함수 안에서 한 장으로 교체
    tile = TILES[name]
    screen_left = camera.to_screen(left)
    draw_rect(images['road'], screen_left, config.PLAY_BOTTOM, screen_left + TILE_W, ROAD_Y)
    for x0, x1 in tile['walls']:
        draw_rect(images['wall'], screen_left + x0, ROAD_Y, screen_left + x1, ROOF_Y)
    for _, x0, y0, x1, y1 in tile['deco']:
        draw_rect(images['deco'], screen_left + x0, y0, screen_left + x1, y1)
    for kind, x0, y0, x1, y1 in tile['platforms']:
        if kind in ('roof', 'ledge', 'peg'):
            # 윗면이 발판 선에 오도록 두께만큼 아래로
            draw_rect(images[kind], screen_left + x0, y0 - config.PLATFORM_THICK[kind], screen_left + x1, y0)
        elif kind == 'accel':
            draw_slope(images[kind], screen_left + x0, y0, screen_left + x1, y1, config.PLATFORM_THICK[kind])
