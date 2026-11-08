# 플레이어 박스
import math

from pico2d import load_image, SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE, SDLK_LSHIFT, SDLK_RSHIFT

import camera
import config
import game_framework
import game_world
from sprite_data import BOX_ANIM, draw_box, draw_item
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


def is_air(box, event):
    return event[0] == 'AIR'


def is_fall(box, event):
    return event[0] == 'FALL'


def is_done(box, event):
    return event[0] == 'DONE'


def space_down(box, event):
    return event[0] == 'KEY' and event[1].type == SDL_KEYDOWN and event[1].key == SDLK_SPACE


def space_up(box, event):
    return event[0] == 'KEY' and event[1].type == SDL_KEYUP and event[1].key == SDLK_SPACE


def space_ready(box, event):
    # 미리 누른 Space가 남아 있음
    return event[0] == 'BUFFER' and box.space_waiting


def space_tapped(box, event):
    # 미리 누른 Space를 이미 뗐음
    return event[0] == 'BUFFER' and not box.space_held


def shift_down(box, event):
    return event[0] == 'KEY' and event[1].type == SDL_KEYDOWN and event[1].key in (SDLK_LSHIFT, SDLK_RSHIFT)


def shift_ready(box, event):
    # 지금 누른 Shift 또는 미리 누른 Shift가 남아 있음
    return shift_down(box, event) or (event[0] == 'BUFFER' and box.shift_buffer > 0)


def can_pick_tape(box, event):
    return shift_ready(box, event) and box.zone == 'chase' and box.near_tape is not None and not box.hud.is_full()


def can_slam(box, event):
    return shift_ready(box, event) and box.zone == 'boss' and box.slam_cooldown <= 0


class Idle:
    @staticmethod
    def enter(box, event):
        box.frame = 0
        box.vx = 0.0

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        n = BOX_ANIM['idle'][1]
        box.frame = (box.frame + config.ANIM_FPS_IDLE * game_framework.frame_time) % n

    @staticmethod
    def draw(box):
        draw_box(box.sheet, 'idle', box.frame, camera.to_screen(box.x), box.y, flip=box.face_dir < 0)


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
        box.vx = box.dir * box.walk_speed()
        box.x += box.vx * dt
        box.clamp_x()
        box.frame = (box.frame + config.ANIM_FPS_MOVE * dt) % Walk.FRAMES
        box.walk_time += dt

    @staticmethod
    def hop_offset(box):
        # 깡충은 그림 위치만 움직임 (실제 y는 그대로)
        return config.HOP_HEIGHT * abs(math.sin(math.pi * box.walk_time / Walk.CYCLE_TIME))

    @staticmethod
    def draw(box):
        draw_box(box.sheet, 'jump', box.frame, camera.to_screen(box.x), box.y + Walk.hop_offset(box), flip=box.face_dir < 0)


class Charge:
    @staticmethod
    def enter(box, event):
        box.charge_time = 0.0
        box.space_waiting = False   # 누른 Space를 처리함

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        dt = game_framework.frame_time
        box.charge_time += dt
        box.vx = box.dir * box.charge_speed()
        box.x += box.vx * dt
        box.clamp_x()

    @staticmethod
    def draw(box):
        c = box.charge_ratio()
        draw_box(box.sheet, 'charge', 0, camera.to_screen(box.x), box.y, flip=box.face_dir < 0,
                 sx=1 + config.CHARGE_SQUASH_X * c, sy=1 - config.CHARGE_SQUASH_Y * c)


class Jump:
    @staticmethod
    def enter(box, event):
        if event and event[0] in ('KEY', 'BUFFER'):
            height = config.JUMP_MIN_H + (config.JUMP_MAX_H - config.JUMP_MIN_H) * box.charge_ratio()
            box.vy = math.sqrt(2 * config.GRAVITY * height)
            box.vx = box.dir * box.charge_speed()   # 시작 가로 속도 = 그때의 이동 속도
        else:
            box.vy = 0      # 발판에서 벗어남: 위로 뛰지 않고 가로 속도 유지
        box.jump_vy = box.vy    # 점프 시작 속도 (높이가 달라도 같은 비율로 그림을 넘기는 기준)
        box.ground = None
        box.on_accel_ground = False
        # 출발 높이가 속한 층이 시작 층 (높이 계산 오차를 막기 위해 +1)
        box.takeoff_y = box.y
        box.floor_y = max(y for y in config.FLOOR_YS if y <= box.takeoff_y + 1)

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        # 착지를 먼저 봄: 시작 층 높이에 내려앉는 순간이 추락이 되지 않게
        if box.move_in_air():
            box.state_machine.handle_event(('DONE', None))
        elif box.y < box.floor_y:
            box.state_machine.handle_event(('FALL', None))

    @staticmethod
    def sheet_frame(box):
        # 상승은 jump 1 -> 2, 정점은 jump 3 -> 4, 하강은 착지까지 jump 4 유지
        if box.vy > config.JUMP_APEX_VY:
            return 0 if box.vy > (box.jump_vy + config.JUMP_APEX_VY) / 2 else 1
        return 2 if box.vy >= 0 else 3

    @staticmethod
    def draw(box):
        draw_box(box.sheet, 'jump', Jump.sheet_frame(box), camera.to_screen(box.x), box.y, flip=box.face_dir < 0)


class Fall:
    LAST_FRAME = BOX_ANIM['fall'][1] - 1

    @staticmethod
    def enter(box, event):
        box.frame = 0

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        # 한 번 재생하고 마지막 장 유지
        box.frame = min(box.frame + config.ANIM_FPS_FALL * game_framework.frame_time, Fall.LAST_FRAME)
        if box.move_in_air():
            box.state_machine.handle_event(('DONE', None))

    @staticmethod
    def draw(box):
        draw_box(box.sheet, 'fall', box.frame, camera.to_screen(box.x), box.y, flip=box.face_dir < 0)


class DizzyFx:
    # 회복 중 머리 위 도는 별
    image = None

    def __init__(self, box):
        if DizzyFx.image is None:
            DizzyFx.image = load_image('resource/item_sheet.png')
        self.box = box
        self.time = 0.0

    def update(self):
        # 디버그 키는 exit 없이 상태를 바꾸므로 직접 확인해서 지움
        if self.box.state_machine.cur is not Recover:
            game_world.remove_object(self)
        self.time += game_framework.frame_time

    def draw(self):
        draw_item(DizzyFx.image, 'dizzy', self.time * config.DIZZY_FPS, camera.to_screen(self.box.x),
                  self.box.y + config.BOX_BODY_H + config.DIZZY_GAP)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class Recover:
    @staticmethod
    def enter(box, event):
        box.frame = 0
        box.vx = 0.0
        box.recover_time = 0.0
        box.stun_time = (box.takeoff_y - box.y) / config.STUN_PX_PER_SEC    # 떨어진 높이만큼 멈춤
        game_world.add_object(DizzyFx(box), game_world.LAYER_FX)

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        dt = game_framework.frame_time
        box.frame = (box.frame + config.ANIM_FPS_RECOVER * dt) % BOX_ANIM['recover'][1]
        box.recover_time += dt
        if box.recover_time >= box.stun_time:
            box.state_machine.handle_event(('DONE', None))

    @staticmethod
    def draw(box):
        draw_box(box.sheet, 'recover', box.frame, camera.to_screen(box.x), box.y, flip=box.face_dir < 0)


class Get:
    FRAMES = BOX_ANIM['get'][1]

    @staticmethod
    def enter(box, event):
        box.get_time = 0.0
        box.vx = 0.0
        box.shift_buffer = 0.0
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
        draw_box(box.sheet, 'get', frame, camera.to_screen(box.x), box.y)


class Slam:
    @staticmethod
    def enter(box, event):
        box.slam_time = 0.0
        box.vx = 0.0
        box.shift_buffer = 0.0
        box.slam_start_x = box.x
        box.slam_dir = box.face_dir
        box.slam_returning = False  # 돌아오는 중에는 맞지 않아서 돌진 한 번에 1회만 맞음

    @staticmethod
    def exit(box, event):
        box.slam_cooldown = config.SLAM_COOLDOWN    # 돌아온 뒤부터 쿨타임

    @staticmethod
    def start_return(box):
        # 지금 위치에서 시작 위치로 튕겨 돌아옴
        box.slam_returning = True
        box.slam_time = 0.0
        box.slam_return_x = box.x

    @staticmethod
    def return_ratio(box):
        return min(box.slam_time / config.SLAM_RETURN_TIME, 1)

    @staticmethod
    def do(box):
        # 돌진 끝 위치의 충돌까지 확인한 다음 프레임에 돌아오기 시작
        if not box.slam_returning and box.slam_time >= config.SLAM_TIME:
            Slam.start_return(box)
        box.slam_time += game_framework.frame_time
        if box.slam_returning:
            t = Slam.return_ratio(box)
            eased = 1 - (1 - t) ** 2    # 처음엔 빠르게 튕기고 갈수록 느려짐
            box.x = box.slam_return_x + (box.slam_start_x - box.slam_return_x) * eased
            if t >= 1:
                box.state_machine.handle_event(('DONE', None))
        else:
            p = min(box.slam_time / config.SLAM_TIME, 1)
            box.x = box.slam_start_x + box.slam_dir * config.SLAM_DIST * p
            box.clamp_x()

    @staticmethod
    def draw(box):
        if box.slam_returning:
            # 튕김은 그림 위치만 움직임 (실제 y는 그대로), 진행 방향 반대로 기울임
            hop = config.SLAM_BOUNCE_H * math.sin(math.pi * Slam.return_ratio(box))
            draw_box(box.sheet, 'slam', 0, camera.to_screen(box.x), box.y + hop, flip=box.slam_dir < 0,
                     rot=box.slam_dir * config.SLAM_ROT)
        else:
            # 진행 방향으로 기울임 (rot 양수가 반시계)
            draw_box(box.sheet, 'slam', 0, camera.to_screen(box.x), box.y, flip=box.slam_dir < 0,
                     sx=config.SLAM_SX, sy=config.SLAM_SY, rot=-box.slam_dir * config.SLAM_ROT)


GROUND_STATES = (Idle, Walk, Charge, Get)   # 발밑 검사를 하는 상태 (Slam은 돌아온 뒤 검사)


class Box:
    def __init__(self, hud, level):
        self.sheet = load_image('resource/box_sheet.png')
        self.hud = hud
        self.level = level
        self.zone = 'chase'
        self.x, self.y = config.BOX_START_X, config.ROAD_Y    # 발 위치
        self.left_down, self.right_down = False, False
        self.last_dir = 0       # 마지막에 누른 방향
        self.dir = 0            # 지금 이동할 방향 (-1, 0, 1)
        self.face_dir = 1       # 바라보는 방향
        self.frame = 0
        self.charge_time = 0.0
        self.vx, self.vy = 0.0, 0.0
        self.ground = None      # 서 있는 발판
        self.near_tape = None   # 지금 겹쳐 있는 테이프
        self.slam_cooldown = 0.0
        self.on_accel_ground = False    # 가속 지붕 위 여부
        self.clear_input()
        self.state_machine = StateMachine(self, Idle, {
            Idle: [(is_air, Jump), (space_down, Charge), (space_ready, Charge), (can_pick_tape, Get), (can_slam, Slam),
                   (is_moving, Walk)],
            Walk: [(is_air, Jump), (space_down, Charge), (space_ready, Charge), (can_pick_tape, Get), (can_slam, Slam),
                   (is_stopped, Idle)],
            Slam: [(done_moving, Walk), (done_stopped, Idle)],
            Charge: [(is_air, Jump), (space_up, Jump), (space_tapped, Jump)],
            Jump: [(is_fall, Fall), (done_moving, Walk), (done_stopped, Idle)],
            Fall: [(is_done, Recover)],
            Recover: [(done_moving, Walk), (done_stopped, Idle)],
            Get: [(done_moving, Walk), (done_stopped, Idle)],
        })

    def reset(self):
        # 위치·상태를 처음으로 (키 눌림 상태와 구간은 유지)
        self.x, self.y = config.BOX_START_X, config.ROAD_Y
        self.vx, self.vy = 0.0, 0.0
        self.ground = None
        self.on_accel_ground = False
        self.face_dir = self.dir if self.dir != 0 else 1
        self.near_tape = None
        self.slam_cooldown = 0.0
        self.clear_input()
        self.state_machine.reset(Walk if self.dir != 0 else Idle)

    def clear_input(self):
        # 미리 누른 키 기억 (Space는 누르고 있는지와 방금 눌렀는지를 따로)
        self.space_waiting = False  # 눌렀는데 아직 처리 안 됨
        self.space_held = False     # 지금 누르고 있음
        self.space_buffer = 0.0     # 누른 뒤 남은 기억 시간
        self.shift_buffer = 0.0

    def warp(self, x):
        # 디버그: 그 x의 도로 위로 옮김
        self.x, self.y = x, config.ROAD_Y
        self.vx, self.vy = 0.0, 0.0
        self.on_accel_ground = False
        self.state_machine.reset(Walk if self.dir != 0 else Idle)

    def drop_to(self, y):
        # 디버그: 그 높이 + 1px에서 공중으로 시작
        self.y = y + 1
        self.vx = 0.0
        self.state_machine.reset(Jump)

    def update(self):
        self.slam_cooldown = max(self.slam_cooldown - game_framework.frame_time, 0)
        self.state_machine.update()
        if self.state_machine.cur in GROUND_STATES:
            self.check_ground()
        self.use_buffer()
        self.space_buffer = max(self.space_buffer - game_framework.frame_time, 0)
        self.shift_buffer = max(self.shift_buffer - game_framework.frame_time, 0)
        # 미리 누른 Shift를 처리할 때까지 직전 충돌 결과를 씀, 다음 충돌 처리에서 다시 기록됨
        self.near_tape = None

    def use_buffer(self):
        # 땅 위에서 움직일 수 있게 되면 미리 누른 키를 처리
        if self.state_machine.cur not in (Idle, Walk):
            return
        if self.space_waiting and not self.space_held and self.space_buffer <= 0:
            self.space_waiting = False  # 너무 일찍 눌렀다 뗀 것은 버림
        if self.space_waiting:
            self.state_machine.handle_event(('BUFFER', None))
            # 이미 뗐으면 차지 0으로 바로 뜀
            if self.state_machine.cur is Charge and not self.space_held:
                self.state_machine.handle_event(('BUFFER', None))
        elif self.shift_buffer > 0:
            self.state_machine.handle_event(('BUFFER', None))

    def move_in_air(self):
        # Jump·Fall 공통 공중 이동, 착지했으면 True
        dt = game_framework.frame_time
        prev_x, prev_y = self.x, self.y
        # 공중 좌우 조작: 입력이 있으면 목표 속도로 천천히 변함, 없으면 유지
        # 같은 방향으로 걷는 속도보다 빠르면 줄이지 않음 (가속 지붕에서 얻은 속도 유지)
        keeps_speed = self.vx * self.dir > 0 and abs(self.vx) > config.WALK_SPEED
        if self.dir != 0 and not keeps_speed:
            diff = self.dir * config.WALK_SPEED - self.vx
            change = config.AIR_ACCEL * dt
            self.vx += diff if abs(diff) <= change else math.copysign(change, diff)
        self.x += self.vx * dt
        self.clamp_x()
        # 프레임 속도와 상관없이 같은 높이가 되도록 등가속도 공식으로 계산
        self.y += self.vy * dt - 0.5 * config.GRAVITY * dt * dt
        self.vy -= config.GRAVITY * dt
        # 내려오는 중에만 밟힘 (아래에서 위로는 통과)
        platform = self.level.find_landing(prev_x, prev_y, self.x, self.y) if self.vy <= 0 else None
        if platform:
            self.y = platform.surface_y(self.x)
            self.vy = 0
            self.ground = platform
        return platform is not None

    def check_ground(self):
        # 발밑에 발판이 있으면 붙고 (경사면을 걸으면 y가 따라감), 없으면 공중에 뜸
        platform = self.level.find_ground(self.x, self.y)
        if platform:
            self.y = platform.surface_y(self.x)
            self.ground = platform
            self.on_accel_ground = platform.kind == 'accel'
        else:
            self.state_machine.handle_event(('AIR', None))

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
        self.remember_input(event)
        self.state_machine.handle_event(('KEY', event))

    def remember_input(self, event):
        # 상태 머신이 받기 전에 기록 (바로 처리되면 Charge·Get·Slam 진입에서 지움)
        pressed = event.type == SDL_KEYDOWN
        if event.key == SDLK_SPACE:
            self.space_held = pressed
            if pressed:
                self.space_waiting = True
                self.space_buffer = config.INPUT_BUFFER_TIME
        elif event.key in (SDLK_LSHIFT, SDLK_RSHIFT) and pressed:
            self.shift_buffer = config.INPUT_BUFFER_TIME

    def charge_ratio(self):
        # 차지 비율 c (0~1)
        return min(self.charge_time / config.CHARGE_MAX_TIME, 1)

    def walk_speed(self):
        # 가속 지붕 위에서 오른쪽으로 갈 때만 빠름
        if self.on_accel_ground and self.dir > 0:
            return config.WALK_SPEED * config.ACCEL_RATE
        return config.WALK_SPEED

    def charge_speed(self):
        # 차지 중 이동 속도 (가속 지형 위에서는 감속 없음)
        if self.on_accel_ground:
            return self.walk_speed()
        return config.WALK_SPEED * config.CHARGE_SPEED_RATE

    def clamp_x(self):
        # 맵 양쪽 끝에 보이지 않는 벽
        half = config.BOX_BB_W / 2
        self.x = max(config.MAP_LEFT + half, min(self.x, self.level.right - half))

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
            if self.state_machine.cur is Slam and not self.slam_returning:
                other.on_hit()
                Slam.start_return(self)
