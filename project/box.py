# 플레이어 박스
import math

from pico2d import load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_LSHIFT, SDLK_RSHIFT

import config
import game_framework
import game_world
from sprite_data import BOX_ANIM, draw_box
from state_machine import StateMachine
from tape import TapePickupFx


# 전환 조건
def is_moving(box, event):
    return event[0] == 'KEY' and box.dir != 0


def is_stopped(box, event):
    return event[0] == 'KEY' and box.dir == 0


def done_moving(box, event):
    return event[0] == 'DONE' and box.dir != 0


def done_stopped(box, event):
    return event[0] == 'DONE' and box.dir == 0


def space_down(box, event):
    return event[0] == 'KEY' and event[1].type == SDL_KEYDOWN and event[1].key == SDLK_SPACE


def space_up(box, event):
    return event[0] == 'KEY' and event[1].type == SDL_KEYUP and event[1].key == SDLK_SPACE


def shift_down(box, event):
    return event[0] == 'KEY' and event[1].type == SDL_KEYDOWN and event[1].key in (SDLK_LSHIFT, SDLK_RSHIFT)


def can_pick_tape(box, event):
    return shift_down(box, event) and box.zone == 'chase' and box.near_tape is not None and not box.hud.is_full()


def can_slam(box, event):
    return shift_down(box, event) and box.zone == 'boss' and box.slam_cooldown <= 0


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


class Charge:
    @staticmethod
    def enter(box, event):
        box.charge_time = 0.0

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        dt = game_framework.frame_time
        box.charge_time += dt
        box.x += box.dir * box.charge_speed() * dt
        box.clamp_x()

    @staticmethod
    def draw(box):
        c = box.charge_ratio()
        draw_box(box.sheet, 'charge', 0, box.x, box.y, flip=box.face_dir < 0,
                 sx=1 + config.CHARGE_SQUASH_X * c, sy=1 - config.CHARGE_SQUASH_Y * c)


class Jump:
    @staticmethod
    def enter(box, event):
        height = config.JUMP_MIN_H + (config.JUMP_MAX_H - config.JUMP_MIN_H) * box.charge_ratio()
        box.vy = math.sqrt(2 * config.GRAVITY * height)
        box.vx = box.dir * box.charge_speed()   # 시작 가로 속도 = 그때의 이동 속도
        box.frame = 0

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        dt = game_framework.frame_time
        # 공중 좌우 조작: 입력이 있으면 목표 속도로 천천히 변함, 없으면 유지
        if box.dir != 0:
            diff = box.dir * config.WALK_SPEED - box.vx
            change = config.AIR_ACCEL * dt
            box.vx += diff if abs(diff) <= change else math.copysign(change, diff)
        box.x += box.vx * dt
        box.clamp_x()
        # 프레임 속도와 상관없이 같은 높이가 되도록 등가속도 공식으로 계산
        box.y += box.vy * dt - 0.5 * config.GRAVITY * dt * dt
        box.vy -= config.GRAVITY * dt
        box.frame = (box.frame + config.ANIM_FPS_MOVE * dt) % 2
        if box.y <= config.GROUND_Y:
            box.y = config.GROUND_Y
            box.vy = 0
            box.state_machine.handle_event(('DONE', None))

    @staticmethod
    def sheet_frame(box):
        # 상승은 jump 1~2, 하강은 jump 3~4
        first = 0 if box.vy > 0 else 2
        return first + int(box.frame)

    @staticmethod
    def draw(box):
        draw_box(box.sheet, 'jump', Jump.sheet_frame(box), box.x, box.y, flip=box.face_dir < 0)


class Get:
    FRAMES = BOX_ANIM['get'][1]

    @staticmethod
    def enter(box, event):
        box.get_time = 0.0
        tape = box.near_tape
        game_world.remove_object(tape)
        box.near_tape = None
        game_world.add_object(TapePickupFx(tape.x, tape.y, box, box.hud), game_world.LAYER_FX)

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        box.get_time += game_framework.frame_time
        if box.get_time >= config.TAPE_PICKUP_TIME:
            box.state_machine.handle_event(('DONE', None))

    @staticmethod
    def draw(box):
        # 시간 동안 한 번 재생하고 마지막 장에서 멈춤 (정면이라 반전 없음)
        frame = min(int(box.get_time / config.TAPE_PICKUP_TIME * Get.FRAMES), Get.FRAMES - 1)
        draw_box(box.sheet, 'get', frame, box.x, box.y)


class Slam:
    @staticmethod
    def enter(box, event):
        box.slam_time = 0.0
        box.slam_start_x = box.x
        box.slam_dir = box.face_dir
        box.slam_hit = False    # 돌진 한 번에 1회만 맞음

    @staticmethod
    def exit(box, event):
        box.slam_cooldown = config.SLAM_COOLDOWN    # 돌진 끝난 뒤부터 쿨타임

    @staticmethod
    def do(box):
        box.slam_time += game_framework.frame_time
        p = min(box.slam_time / config.SLAM_TIME, 1)
        box.x = box.slam_start_x + box.slam_dir * config.SLAM_DIST * p
        box.clamp_x()
        if p >= 1:
            box.state_machine.handle_event(('DONE', None))

    @staticmethod
    def draw(box):
        # 진행 방향으로 기울임 (rot 양수가 반시계)
        draw_box(box.sheet, 'slam', 0, box.x, box.y, flip=box.slam_dir < 0,
                 sx=config.SLAM_SX, sy=config.SLAM_SY, rot=-box.slam_dir * config.SLAM_ROT)


class Box:
    def __init__(self, hud):
        self.sheet = load_image('resource/box_sheet.png')
        self.hud = hud
        self.zone = 'chase'
        self.x, self.y = config.BOX_START_X, config.GROUND_Y    # 발 위치
        self.left_down, self.right_down = False, False
        self.last_dir = 0       # 마지막에 누른 방향
        self.dir = 0            # 지금 이동할 방향 (-1, 0, 1)
        self.face_dir = 1       # 바라보는 방향
        self.frame = 0
        self.charge_time = 0.0
        self.vx, self.vy = 0.0, 0.0
        self.near_tape = None   # 지금 겹쳐 있는 테이프
        self.slam_cooldown = 0.0
        self.on_accel_ground = False    # 가속 지형 위 여부 (1주차엔 항상 False)
        self.state_machine = StateMachine(self, Idle, {
            Idle: [(space_down, Charge), (can_pick_tape, Get), (can_slam, Slam), (is_moving, Walk)],
            Walk: [(space_down, Charge), (can_pick_tape, Get), (can_slam, Slam), (is_stopped, Idle)],
            Slam: [(done_moving, Walk), (done_stopped, Idle)],
            Charge: [(space_up, Jump)],
            Jump: [(done_moving, Walk), (done_stopped, Idle)],
            Get: [(done_moving, Walk), (done_stopped, Idle)],
        })

    def reset(self):
        # 위치·상태를 처음으로 (키 눌림 상태와 구간은 유지)
        self.x, self.y = config.BOX_START_X, config.GROUND_Y
        self.vx, self.vy = 0.0, 0.0
        self.face_dir = self.dir if self.dir != 0 else 1
        self.near_tape = None
        self.slam_cooldown = 0.0
        self.state_machine.reset(Walk if self.dir != 0 else Idle)

    def update(self):
        self.near_tape = None   # 이번 프레임의 충돌 처리에서 다시 기록됨
        self.slam_cooldown = max(self.slam_cooldown - game_framework.frame_time, 0)
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()

    def get_bb(self):
        half = config.BOX_BB_W / 2
        return self.x - half, self.y, self.x + half, self.y + config.BOX_BB_H

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        if event.key in (SDLK_LEFT, SDLK_RIGHT):
            self.update_dir(event)
        self.state_machine.handle_event(('KEY', event))

    def charge_ratio(self):
        # 차지 비율 c (0~1)
        return min(self.charge_time / config.CHARGE_MAX_TIME, 1)

    def charge_speed(self):
        # 차지 중 이동 속도 (가속 지형 위에서는 감속 없음)
        if self.on_accel_ground:
            return config.WALK_SPEED
        return config.WALK_SPEED * config.CHARGE_SPEED_RATE

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
        if group == 'box:tape':
            self.near_tape = other
        elif group == 'box:dummy':
            if self.state_machine.cur is Slam and not self.slam_hit:
                self.slam_hit = True
                other.on_hit()
