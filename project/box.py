# 플레이어 박스
from pico2d import load_image

import config
import game_framework
from sprite_data import BOX_ANIM, draw_box
from state_machine import StateMachine


class Idle:
    @staticmethod
    def enter(box, event):
        box.frame = 0

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        n = BOX_ANIM['idle'][1]
        box.frame = (box.frame + config.ANIM_FPS_IDLE * game_framework.frame_time) % n

    @staticmethod
    def draw(box):
        draw_box(box.sheet, 'idle', box.frame, box.x, box.y, flip=box.face_dir < 0)


class Walk:
    @staticmethod
    def enter(box, event):
        pass

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        pass

    @staticmethod
    def draw(box):
        pass


class Box:
    def __init__(self):
        self.sheet = load_image('resource/box_sheet.png')
        self.x, self.y = config.BOX_START_X, config.GROUND_Y    # 발 위치
        self.face_dir = 1
        self.frame = 0
        self.on_accel_ground = False    # 가속 지형 위 여부 (1주차엔 항상 False)
        self.state_machine = StateMachine(self, Idle, {Idle: [], Walk: []})

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def get_bb(self):
        pass

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        pass
