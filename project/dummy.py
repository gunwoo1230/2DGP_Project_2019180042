# 몸통박치기 테스트용 허수아비
from pico2d import load_image

import config


class Dummy:
    def __init__(self):
        self.image = load_image('resource/placeholder/ph_dummy.png')
        self.x = config.DUMMY_X
        self.y = config.GROUND_Y + config.DUMMY_H / 2   # 그림의 가운데

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x, self.y, config.DUMMY_W, config.DUMMY_H)

    def get_bb(self):
        half_w, half_h = config.DUMMY_W / 2, config.DUMMY_H / 2
        return self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h

    def handle_collision(self, group, other):
        pass

    def on_hit(self):
        pass
