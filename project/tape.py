# 테이프: 바닥 테이프와 줍기 연출
from pico2d import load_image

import config
import game_framework
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
    image = None

    def __init__(self, start_x, start_y, box, hud):
        if TapePickupFx.image is None:
            TapePickupFx.image = load_image('resource/item_sheet.png')
        self.start_x, self.start_y = start_x, start_y
        self.x, self.y = start_x, start_y
        # 머리 위 도착 위치
        self.head_x = box.x
        self.head_y = box.y + config.BOX_BODY_H + config.FX_RISE_H
        self.scale = SCALE
        self.time = 0.0

    def update(self):
        self.time += game_framework.frame_time
        p = min(self.time / config.FX_RISE_TIME, 1)
        self.x = self.start_x + (self.head_x - self.start_x) * p
        self.y = self.start_y + (self.head_y - self.start_y) * p

    def draw(self):
        # 떠오른 뒤 머리 위에 있는 동안 테이프 뒤에서 반짝임
        sparkle_time = self.time - config.FX_RISE_TIME
        if 0 <= sparkle_time < config.FX_SPARKLE_TIME:
            draw_item(TapePickupFx.image, 'sparkle', sparkle_time * config.FX_SPARKLE_FPS, self.x, self.y)
        draw_item(TapePickupFx.image, 'tape', 0, self.x, self.y, scale=self.scale)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
