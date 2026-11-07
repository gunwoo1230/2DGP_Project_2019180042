# 플레이어 박스
import math

from pico2d import load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT

import config
import game_framework
from sprite_data import BOX_ANIM, draw_box
from state_machine import StateMachine


# 전환 조건
def is_moving(box, event):
    return event[0] == 'KEY' and box.dir != 0


def is_stopped(box, event):
    return event[0] == 'KEY' and box.dir == 0


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
    FRAMES = BOX_ANIM['jump'][1]
    CYCLE_TIME = FRAMES / config.ANIM_FPS_MOVE  # 애니 한 바퀴에 깡충 1번

    @staticmethod
    def enter(box, event):
        box.frame = 0
        box.walk_time = 0.0

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        dt = game_framework.frame_time
        box.x += box.dir * config.WALK_SPEED * dt
        box.clamp_x()
        box.frame = (box.frame + config.ANIM_FPS_MOVE * dt) % Walk.FRAMES
        box.walk_time += dt

    @staticmethod
    def hop_offset(box):
        # 깡충은 그림 위치만 움직임 (실제 y는 그대로)
        return config.HOP_HEIGHT * abs(math.sin(math.pi * box.walk_time / Walk.CYCLE_TIME))

    @staticmethod
    def draw(box):
        draw_box(box.sheet, 'jump', box.frame, box.x, box.y + Walk.hop_offset(box), flip=box.face_dir < 0)


class Box:
    def __init__(self):
        self.sheet = load_image('resource/box_sheet.png')
        self.x, self.y = config.BOX_START_X, config.GROUND_Y    # 발 위치
        self.left_down, self.right_down = False, False
        self.last_dir = 0       # 마지막에 누른 방향
        self.dir = 0            # 지금 이동할 방향 (-1, 0, 1)
        self.face_dir = 1       # 바라보는 방향
        self.frame = 0
        self.on_accel_ground = False    # 가속 지형 위 여부 (1주차엔 항상 False)
        self.state_machine = StateMachine(self, Idle, {
            Idle: [(is_moving, Walk)],
            Walk: [(is_stopped, Idle)],
        })

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def get_bb(self):
        pass

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        if event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.update_dir(event)
        self.state_machine.handle_event(('KEY', event))

    def clamp_x(self):
        # 플레이 칸 좌우 끝을 넘지 못함
        half = config.BOX_BB_W / 2
        self.x = max(config.PLAY_LEFT + half, min(self.x, config.PLAY_RIGHT - half))

    def update_dir(self, event):
        # 왼쪽·오른쪽 눌림 기록
        pressed = event.type == SDL_KEYDOWN
        key_dir = -1 if event.key == SDLK_LEFT else 1
        if key_dir < 0:
            self.left_down = pressed
        else:
            self.right_down = pressed
        if pressed:
            self.last_dir = key_dir

        # 둘 다 눌리면 마지막에 누른 방향
        if self.left_down and self.right_down:
            self.dir = self.last_dir
        elif self.left_down:
            self.dir = -1
        elif self.right_down:
            self.dir = 1
        else:
            self.dir = 0

        if self.dir != 0:
            self.face_dir = self.dir

    def handle_collision(self, group, other):
        pass
