# 방해 요소: 물웅덩이(도로), 살아 있는 창문(창틀), 비둘기(지붕)
import random

import camera
import config
import day
import game_framework
import game_world
import parts
from map_data import difficulty

enabled = True      # 디버그 H로 끄면 감속·창문 열림·비둘기·피격이 모두 없음


def frame(time, step, names):
    # step초마다 번갈아 보여 줄 그림 이름
    return names[int(time / step) % len(names)]


class Puddle:
    # 도로 물웅덩이: 밟는 동안과 나온 뒤 잠깐 느려짐
    def __init__(self, x):
        self.x = x      # 왼쪽 끝 월드 x
        self.time = 0.0     # 그림 두 장을 번갈아 보여 주는 데 씀

    def update(self):
        self.time += game_framework.frame_time

    def draw(self):
        # 판정 크기(PUDDLE_W)는 그대로, 그림은 가로 가운데를 맞춤
        left, bottom, right, top = self.get_bb()
        if camera.visible(left) or camera.visible(right):
            name = frame(self.time, config.PUDDLE_FRAME, ('puddle_1', 'puddle_2'))
            parts.draw_center(name, camera.to_screen((left + right) / 2), config.PUDDLE_DRAW_Y)

    def get_bb(self):
        # 도로 윗면에 걸친 웅덩이 사각형 (박스 쪽에서 발 위치로 다시 판정)
        top = config.ROAD_Y + config.PUDDLE_RISE
        return self.x, top - config.PUDDLE_H, self.x + config.PUDDLE_W, top

    def handle_collision(self, group, other):
        pass


class LiveWindow:
    # 살아 있는 창문: 처음부터 불이 켜져 있고, 그 창틀에 박스가 서면 덜컹 -> 열림
    def __init__(self, x, y, box):
        self.x, self.y = x, y   # 창틀 왼쪽 끝 월드 x, 창틀 높이
        self.box = box
        self.state = 'lit'      # 'lit' 불 켜짐 -> 'shake' 덜컹 -> 'open' 열림 -> 'done' 보통 창문
        self.time = 0.0         # 지금 상태가 된 뒤 지난 시간

    def update(self):
        self.time += game_framework.frame_time
        if self.state == 'lit':
            # 방해 요소가 켜진 추격 중에 박스가 이 창틀에 서 있으면 (점프로 지나가면 안 열림)
            if enabled and day.phase == 'chase' and self.box.stands_on('ledge', self.x):
                self.set_state('shake')
        elif self.state == 'shake' and self.time >= config.WINDOW_SHAKE_TIME:
            self.set_state('open')      # 박스가 떠났어도 열림
        elif self.state == 'open' and self.time >= config.WINDOW_OPEN_TIME:
            self.set_state('done')

    def set_state(self, state):
        self.state = state
        self.time = 0.0

    def draw(self):
        # 창문 그림 자리 (draw_tile과 같은 위치), done이면 타일의 보통 창문이 보임
        if self.state == 'done' or not (camera.visible(self.x) or camera.visible(self.x + config.WINDOW_W)):
            return
        x = camera.to_screen(self.x)
        if self.state == 'open':
            parts.draw_window('window_open', x, self.y)     # 문짝 포함, 가운데는 같음
        else:
            # lit, shake (shake는 좌우로 흔들림, 그림만)
            dx = 0
            if self.state == 'shake':
                dx = config.WINDOW_SHAKE_PX if int(self.time / config.WINDOW_SHAKE_STEP) % 2 == 0 \
                    else -config.WINDOW_SHAKE_PX
            parts.draw_window('window_lit', x, self.y, dx)
        # 타일이 먼저 그린 창틀을 창문이 덮으므로 창틀을 다시 그림
        parts.draw_sill(x, self.y)

    def get_bb(self):
        # 열린 문짝까지 포함한 창문 범위 (열려 있을 때만 박스를 맞춤)
        return self.x - config.WINDOW_DOOR_W, self.y, self.x + config.WINDOW_W + config.WINDOW_DOOR_W,             self.y + config.WINDOW_H

    def handle_collision(self, group, other):
        pass


class PigeonSpawner:
    # 박스가 평평한 지붕에 있는 시간이 쌓이면 확률로 비둘기를 부름 (한 번에 하나)
    # 맵 배치 난수가 아니라 random 모듈을 씀 (같은 시드여도 비둘기 시점은 다를 수 있음)
    def __init__(self, box, level):
        self.box = box
        self.level = level
        self.pigeon = None      # 지금 공격 중인 비둘기
        self.new_wait()

    def new_wait(self):
        self.time = 0.0
        self.wait = random.uniform(*config.PIGEON_CHECK_TIME)

    def update(self):
        # 공격 중이 아니고, 첫 건물 몇 채를 지나 평평한 지붕(roof)에 서 있는 시간만 쌓음
        if not enabled or day.phase != 'chase' or self.pigeon is not None:
            return
        tile_i = self.level.tile_index(self.box.x)
        if self.box.standing_kind() != 'roof' or tile_i <= config.HAZARD_FREE:
            return
        self.time += game_framework.frame_time
        if self.time >= self.wait:
            if random.random() < config.HAZARD_CHANCE[difficulty(tile_i - 1)]:
                self.start_attack()
            self.new_wait()

    def start_attack(self):
        # 화면 오른쪽 밖, 그 뒤로 처음 나오는 지붕(가속 지붕 포함) 위에 미리 앉혀 둠
        # 박스가 다가오면서 앉아 있는 비둘기가 보이고, PIGEON_ALERT_DX 안에 들어오면 "!" -> 돌진
        half = config.PIGEON_W / 2
        x = camera.x + config.SCREEN_W + config.PIGEON_SPAWN_MARGIN + half
        roofs = sorted((p for p in self.level.platforms
                        if p.kind in ('roof', 'accel') and p.x1 - half >= x and p.x1 - p.x0 >= 2 * half),
                       key=lambda p: p.x0)
        if not roofs:
            return      # 앞에 지붕이 없음 (맵 끝)
        roof = roofs[0]
        x = max(x, roof.x0 + half)
        self.pigeon = Pigeon(x, roof.surface_y(x), self.box, self)
        game_world.add_object(self.pigeon, game_world.LAYER_ITEM)
        game_world.add_collision_pair('box:pigeon', None, self.pigeon)

    def attack_done(self):
        self.pigeon = None
        self.new_wait()

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class Pigeon:
    # 앞쪽 지붕에 앉아 있다가 박스가 다가오면 "!" -> 왼쪽으로 낮게 돌진 (높이 고정, 박스를 따라가지 않음)
    def __init__(self, x, seat_y, box, spawner, ready=None):
        self.x = x                  # 가운데 월드 x
        self.seat_y = seat_y        # 앉은 지붕 높이 (그림 아랫변)
        self.y = seat_y + config.PIGEON_H / 2   # 충돌 박스 가운데
        self.box = box
        self.spawner = spawner
        self.state = 'sit'          # 'sit' 앉아 기다림 -> 'alert' "!" -> 'dash' 돌진 (이때만 박스를 맞춤)
        self.ready = ready          # 있으면 거리 대신 이 조건이 참일 때 "!" (데모 맵)
        self.time = 0.0

    def update(self):
        dt = game_framework.frame_time
        self.time += dt
        if self.state == 'sit':
            # 박스가 지붕 층(3층, 발이 ROOF_Y 이상)에 있고 PIGEON_ALERT_DX 안으로 다가오면 (지나쳤어도) "!"
            # 도로·창틀 층에서는 계속 앉아 있음, "!" 뒤에는 박스가 내려가도 끝까지 돌진
            if self.ready is not None:
                alert = self.ready()
            else:
                on_roof_floor = self.box.y >= config.ROOF_Y - 1
                alert = on_roof_floor and self.x - self.box.x <= config.PIGEON_ALERT_DX
            if alert:
                self.state = 'alert'
                self.time = 0.0
        elif self.state == 'alert':
            if self.time >= config.PIGEON_ALERT_TIME:
                self.state = 'dash'
                self.y = config.ROOF_Y + config.PIGEON_FLY_H
        else:
            self.x -= config.PIGEON_SPEED * dt
            # 화면 왼쪽 밖으로 나가면 사라짐
            if camera.to_screen(self.x + config.PIGEON_W / 2) < -config.DRAW_MARGIN:
                self.finish()

    def finish(self):
        game_world.remove_object(self)
        if self.spawner is not None:    # 데모용으로 미리 앉힌 비둘기는 부른 쪽이 없음
            self.spawner.attack_done()

    def draw(self):
        if not camera.visible(self.x):
            return
        # 그림은 왼쪽을 봄 (돌진도 왼쪽이라 뒤집지 않음), 충돌 박스 크기는 그림과 따로
        x = camera.to_screen(self.x)
        if self.state in ('sit', 'alert'):
            # 아랫변 = 앉은 지붕, alert면 머리 위 "!"
            parts.draw_bottom_center('pigeon_sit', x, self.seat_y)
            if self.state == 'alert':
                top = self.seat_y + parts.size('pigeon_sit')[1]
                parts.draw_bottom_center('alert', x, top + config.ALERT_GAP)
        else:
            name = frame(self.time, config.PIGEON_FLAP, ('pigeon_fly1', 'pigeon_fly2'))
            parts.draw_center(name, x, self.y)

    def get_bb(self):
        hw, hh = config.PIGEON_W / 2, config.PIGEON_H / 2
        return self.x - hw, self.y - hh, self.x + hw, self.y + hh

    def handle_collision(self, group, other):
        pass
