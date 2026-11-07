# 몸통박치기 테스트용 허수아비
from pico2d import load_font, load_image

import config


class Dummy:
    def __init__(self):
        self.image = load_image('resource/placeholder/ph_dummy.png')
        self.font = load_font('resource/font/Gaegu-Bold.ttf', config.DUMMY_FONT_SIZE)
        self.x = config.DUMMY_X
        self.y = config.GROUND_Y + config.DUMMY_H / 2   # 그림의 가운데
        self.hit_count = 0

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x, self.y, config.DUMMY_W, config.DUMMY_H)
        # 머리 위에 맞은 횟수 표시 (디버그 글자)
        text_y = self.y + config.DUMMY_H / 2 + config.DUMMY_TEXT_GAP
        self.font.draw(self.x, text_y, str(self.hit_count), (40, 40, 40))

    def get_bb(self):
        half_w, half_h = config.DUMMY_W / 2, config.DUMMY_H / 2
        return self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h

    def handle_collision(self, group, other):
        pass

    def on_hit(self):
        self.hit_count += 1
