# 방해 요소: 물웅덩이(도로), 살아 있는 창문(창틀), 비둘기(지붕)
import random

from pico2d import load_image

import camera
import config
import day
import game_framework
import game_world
from map_data import difficulty

images = {}
enabled = True      # 디버그 H로 끄면 감속·창문 열림·비둘기·피격이 모두 없음


def load_images():
    # 다시 시작해도 한 번만 불러옴
    if not images:
        images['puddle'] = load_image('resource/placeholder/ph_puddle.png')
        images['window_lit'] = load_image('resource/placeholder/ph_window_lit.png')
        images['window_open'] = load_image('resource/placeholder/ph_window_open.png')
        images['pigeon'] = load_image('resource/placeholder/ph_pigeon.png')
        images['alert'] = load_image('resource/placeholder/ph_alert.png')


def draw_rect(image, x0, y0, x1, y1):
    # 월드 x 범위·화면 y 범위의 사각형으로 그림
    image.draw((camera.to_screen(x0) + camera.to_screen(x1)) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0)


class Puddle:
    # 도로 물웅덩이: 밟는 동안과 나온 뒤 잠깐 느려짐
    def __init__(self, x):
        load_images()
        self.x = x      # 왼쪽 끝 월드 x

    def update(self):
        pass

    def draw(self):
        left, bottom, right, top = self.get_bb()
        if camera.visible(left) or camera.visible(right):
            draw_rect(images['puddle'], left, bottom, right, top)

    def get_bb(self):
        # 도로 윗면에 걸친 웅덩이 사각형 (박스 쪽에서 발 위치로 다시 판정)
        top = config.ROAD_Y + config.PUDDLE_RISE
        return self.x, top - config.PUDDLE_H, self.x + config.PUDDLE_W, top

    def handle_collision(self, group, other):
        pass


class LiveWindow:
    # 살아 있는 창문: 처음부터 불이 켜져 있고, 그 창틀에 박스가 서면 덜컹 -> 열림
    def __init__(self, x, y, box):
        load_images()
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
        x0, x1 = self.x + config.WINDOW_INSET, self.x + config.WINDOW_W - config.WINDOW_INSET
        y0, y1 = self.y, self.y + config.WINDOW_H
        if self.state == 'shake':
            # 좌우로 흔들림 (그림만)
            dx = config.WINDOW_SHAKE_PX if int(self.time / config.WINDOW_SHAKE_STEP) % 2 == 0 else -config.WINDOW_SHAKE_PX
            x0, x1 = x0 + dx, x1 + dx
        draw_rect(images['window_lit'], x0, y0, x1, y1)
        if self.state == 'open':
            # 양옆 바깥으로 열린 문짝
            draw_rect(images['window_open'], x0 - config.WINDOW_DOOR_W, y0, x0, y1)
            draw_rect(images['window_open'], x1, y0, x1 + config.WINDOW_DOOR_W, y1)

    def get_bb(self):
        # 열린 문짝까지 포함한 창문 범위 (열려 있을 때만 박스를 맞춤)
        return self.x - config.WINDOW_DOOR_W, self.y, self.x + config.WINDOW_W + config.WINDOW_DOOR_W,             self.y + config.WINDOW_H

    def handle_collision(self, group, other):
        pass


class PigeonSpawner:
    # 박스가 평평한 지붕에 있는 시간이 쌓이면 확률로 비둘기를 부름 (한 번에 하나)
    # 맵 배치 난수가 아니라 random 모듈을 씀 (같은 시드여도 비둘기 시점은 다를 수 있음)
    def __init__(self, box, level):
        load_images()
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
        # 박스 앞 지붕 높이에 앉음 (화면 오른쪽 밖으로 나가지 않게)
        screen_right = camera.x + config.SCREEN_W - config.PIGEON_SIT_MARGIN
        x = min(self.box.x + config.PIGEON_SIT_DX, screen_right)
        perched = any(p.kind in ('roof', 'accel') and p.x0 <= x <= p.x1 for p in self.level.platforms)
        self.pigeon = Pigeon(x, perched, self)
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
    # 박스 앞 지붕에 앉아 "!" -> 왼쪽으로 낮게 돌진 (높이 고정, 박스를 따라가지 않음)
    def __init__(self, x, perched, spawner):
        load_images()
        self.x = x                  # 가운데 월드 x
        self.y = config.ROOF_Y + config.PIGEON_H / 2    # 가운데, 앉으면 아래 끝이 지붕 높이
        self.perched = perched      # 앉은 자리 아래에 지붕이 있는지 (없으면 떠 있음, 진짜 그림에서 씀)
        self.spawner = spawner
        self.state = 'sit'          # 'sit' 앉아서 "!" -> 'dash' 돌진 (이때만 박스를 맞춤)
        self.time = 0.0

    def update(self):
        dt = game_framework.frame_time
        self.time += dt
        if self.state == 'sit':
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
        self.spawner.attack_done()

    def draw(self):
        if not camera.visible(self.x):
            return
        hw, hh = config.PIGEON_W / 2, config.PIGEON_H / 2
        draw_rect(images['pigeon'], self.x - hw, self.y - hh, self.x + hw, self.y + hh)
        if self.state == 'sit':
            # 머리 위 "!"
            bottom = self.y + hh + config.ALERT_GAP
            draw_rect(images['alert'], self.x - config.ALERT_W / 2, bottom, self.x + config.ALERT_W / 2,
                      bottom + config.ALERT_H)

    def get_bb(self):
        hw, hh = config.PIGEON_W / 2, config.PIGEON_H / 2
        return self.x - hw, self.y - hh, self.x + hw, self.y + hh

    def handle_collision(self, group, other):
        pass
