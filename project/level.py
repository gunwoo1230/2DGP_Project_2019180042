# 레벨: 타일 목록으로 발판과 그릴 것을 만듦
from pico2d import draw_line

import camera
import config
from tiles import TILES, Platform, draw_tile, load_images


class Level:
    def __init__(self, tile_names):
        load_images()
        # (타일 이름, 왼쪽 끝 월드 x)
        self.tiles = [(name, config.MAP_LEFT + config.TILE_W * i) for i, name in enumerate(tile_names)]
        self.right = config.MAP_LEFT + config.TILE_W * len(tile_names)
        # 타일의 발판을 왼쪽 끝만큼 옮겨 월드 좌표로
        self.platforms = [Platform(kind, x0 + left, y0, x1 + left, y1)
                          for name, left in self.tiles
                          for kind, x0, y0, x1, y1 in TILES[name]['platforms']]

    def update(self):
        pass

    def draw(self):
        for name, left in self.tiles:
            # 타일 양쪽 끝이 모두 화면 밖이면 건너뜀
            if camera.to_screen(left + config.TILE_W) >= -config.DRAW_MARGIN \
                    and camera.to_screen(left) <= config.SCREEN_W + config.DRAW_MARGIN:
                draw_tile(name, left)

    def draw_debug(self):
        # F1: 발판 윗면 선 (빨강, 가속 지붕은 주황)
        for p in self.platforms:
            color = (255, 140, 0) if p.kind == 'accel' else (255, 0, 0)
            draw_line(camera.to_screen(p.x0), p.y0, camera.to_screen(p.x1), p.y1, *color)

    def find_landing(self, prev_x, prev_y, x, y):
        # 위에서 윗면을 지나 내려온 발판 중 가장 높은 것 (경사가 있어 각 위치의 윗면과 비교)
        hits = [p for p in self.platforms
                if p.covers(x) and prev_y >= p.surface_y(prev_x) and p.surface_y(x) > y]
        return max(hits, key=lambda p: p.surface_y(x), default=None)

    def find_ground(self, x, y):
        # 발밑에 붙을 수 있는 발판 중 가장 높은 것
        hits = [p for p in self.platforms
                if p.covers(x) and abs(p.surface_y(x) - y) <= config.SNAP]
        return max(hits, key=lambda p: p.surface_y(x), default=None)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
