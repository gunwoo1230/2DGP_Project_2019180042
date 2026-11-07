# 테스트 바닥 (플레이 칸 전체 폭, 윗면이 ROAD_Y)
from pico2d import load_image

import config


class Ground:
    def __init__(self):
        self.image = load_image('resource/placeholder/ph_ground.png')
        self.x = (config.PLAY_LEFT + config.PLAY_RIGHT) / 2
        self.y = (config.PLAY_BOTTOM + config.ROAD_Y) / 2
        self.w = config.PLAY_RIGHT - config.PLAY_LEFT
        self.h = config.ROAD_Y - config.PLAY_BOTTOM

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x, self.y, self.w, self.h)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
