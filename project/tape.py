# 테이프: 바닥 테이프와 줍기 연출
import math

from pico2d import load_image

import camera
import config
import game_framework
import game_world
from sprite_data import ITEM_RECT, SCALE, draw_item

TAPE_W = ITEM_RECT['tape'][0][2] * SCALE    # 화면에 그려지는 크기
TAPE_H = ITEM_RECT['tape'][0][3] * SCALE


class TapeItem:
    image = None

    def __init__(self, x):
        if TapeItem.image is None:
            TapeItem.image = load_image('resource/item_sheet.png')
        self.x = x
        self.y = config.ROAD_Y + TAPE_H / 2   # 그림의 가운데
        self.bob_time = 0.0

    def update(self):
        self.bob_time += game_framework.frame_time

    def bob_offset(self):
        # 둥실은 그림만 움직임 (충돌 박스는 그대로)
        return config.TAPE_BOB_H * math.sin(2 * math.pi * self.bob_time / config.TAPE_BOB_TIME)

    def draw(self):
        if camera.visible(self.x):
            draw_item(TapeItem.image, 'tape', 0, camera.to_screen(self.x), self.y + self.bob_offset())

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
        # 도착하는 생명 칸이 화면 좌표라서 연출 전체를 화면 좌표로 계산
        self.start_x, self.start_y = camera.to_screen(start_x), start_y
        self.x, self.y = self.start_x, self.start_y
        # 머리 위 도착 위치
        self.head_x = camera.to_screen(box.x)
        self.head_y = box.y + config.BOX_BODY_H + config.FX_RISE_H
        # 날아갈 생명 칸은 생성할 때 정해 둠
        self.hud = hud
        slot = hud.reserve_slot()
        self.slot_x = config.UI_LIFE_X + config.UI_LIFE_GAP * slot
        self.slot_y = config.UI_LIFE_Y
        self.scale = SCALE
        self.time = 0.0

    def update(self):
        self.time += game_framework.frame_time
        fly_time = self.time - config.FX_RISE_TIME - config.FX_SPARKLE_TIME
        if fly_time < 0:
            # 머리 위로 떠오름 (다 떠오르면 그 자리에서 반짝임)
            p = min(self.time / config.FX_RISE_TIME, 1)
            self.x = self.start_x + (self.head_x - self.start_x) * p
            self.y = self.start_y + (self.head_y - self.start_y) * p
            return

        # 작아지며 생명 칸으로 날아감
        p = min(fly_time / config.FX_FLY_TIME, 1)
        self.x = self.head_x + (self.slot_x - self.head_x) * p
        self.y = self.head_y + (self.slot_y - self.head_y) * p
        self.scale = SCALE + (config.FX_END_SCALE - SCALE) * p
        if p >= 1:
            self.hud.add_life()
            game_world.remove_object(self)

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
