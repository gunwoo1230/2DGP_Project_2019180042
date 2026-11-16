# 방해 요소: 물웅덩이(도로), 살아 있는 창문(창틀), 비둘기(지붕)
from pico2d import load_image

import camera
import config
import day
import game_framework

images = {}
enabled = True      # 디버그 H로 끄면 감속·창문 열림·비둘기·피격이 모두 없음


def load_images():
    # 다시 시작해도 한 번만 불러옴
    if not images:
        images['puddle'] = load_image('resource/placeholder/ph_puddle.png')
        images['window_lit'] = load_image('resource/placeholder/ph_window_lit.png')
        images['window_open'] = load_image('resource/placeholder/ph_window_open.png')


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
        pass

    def handle_collision(self, group, other):
        pass


class PigeonSpawner:
    # 박스가 평평한 지붕에 있는 시간이 쌓이면 확률로 비둘기를 부름 (한 번에 하나)
    def __init__(self, box, level):
        self.box = box
        self.level = level

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class Pigeon:
    # 박스 앞 지붕에 앉아 "!" -> 왼쪽으로 낮게 돌진
    def __init__(self, x, perched, spawner):
        self.x = x
        self.perched = perched      # 앉은 자리 아래에 지붕이 있는지 (없으면 떠 있음, 진짜 그림에서 씀)
        self.spawner = spawner

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
