# 건물 타일: 타일 정의, 발판, 타일 그리기
from pico2d import load_image

import camera
import config

TILES = {
    'start': {'walls': [], 'deco': [], 'platforms': []},
}

images = {}


class Platform:
    def __init__(self, kind, x0, y0, x1, y1):
        pass

    def surface_y(self, x):
        pass

    def covers(self, x):
        pass


def load_images():
    # 리셋·재시작해도 한 번만 불러옴
    if not images:
        images['road'] = load_image('resource/placeholder/ph_ground.png')


def draw_tile(name, left):
    # 진짜 타일 그림이 오면 이 함수 안에서 한 장으로 교체
    screen_left = camera.to_screen(left)
    road_h = config.ROAD_Y - config.PLAY_BOTTOM
    images['road'].draw(screen_left + config.TILE_W / 2, config.PLAY_BOTTOM + road_h / 2, config.TILE_W, road_h)
