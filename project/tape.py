# 테이프: 바닥 테이프와 줍기 연출
from pico2d import load_image

import config
from sprite_data import ITEM_RECT, SCALE, draw_item

TAPE_W = ITEM_RECT['tape'][0][2] * SCALE    # 화면에 그려지는 크기
TAPE_H = ITEM_RECT['tape'][0][3] * SCALE


class TapeItem:
    image = None

    def __init__(self, x):
        if TapeItem.image is None:
            TapeItem.image = load_image('resource/item_sheet.png')
        self.x = x
        self.y = config.GROUND_Y + TAPE_H / 2   # 그림의 가운데

    def update(self):
        pass

    def draw(self):
        draw_item(TapeItem.image, 'tape', 0, self.x, self.y)

    def get_bb(self):
        half_w = TAPE_W * config.TAPE_BB_RATE / 2
        half_h = TAPE_H * config.TAPE_BB_RATE / 2
        return self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h

    def handle_collision(self, group, other):
        pass


class TapePickupFx:
    def __init__(self, start_x, start_y, box, hud):
        pass

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
