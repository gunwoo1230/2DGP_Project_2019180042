# 경비원: 도로를 따라 박스를 쫓아옴 (resource/parts/guard_run.png 4장 시트, 오른쪽을 봄)
import json

from pico2d import load_image

import camera
import config
import day
import game_framework

# 시트 정보 (한 장 크기·장 수), 게임 크기 그대로 그림
with open('resource/parts/guard.json', encoding='utf-8') as f:
    INFO = json.load(f)
RUN_FRAMES = INFO['guard_run']['frames']
CELL_W, CELL_H = INFO['guard_run']['cell']
HAT_W, HAT_H = INFO['guard_hat']['size']


class Guard:
    image = None

    def __init__(self):
        if Guard.image is None:
            Guard.image = load_image('resource/parts/guard_run.png')
        self.enabled = True     # 디버그로 끌 수 있음
        self.reset()

    def reset(self, gap=config.GUARD_START_GAP, speed=config.GUARD_SPEED):
        self.x = config.BOX_START_X - gap   # 발 가운데, 화면 왼쪽 밖에서 시작 (데모 맵은 더 멀리)
        self.speed = speed      # 데모 맵은 따로 (추락 기절 뒤 빨라짐)
        self.wait_time = config.GUARD_START_DELAY
        self.frame = 0.0

    def update(self):
        # 추격 중에만 움직임, 기다리는 시간이 끝난 프레임은 남은 만큼만 감
        # 멈춰 있으면 (끄기·잡힘·출발 전) 1장
        if not self.enabled or day.phase != 'chase':
            self.frame = 0.0
            return
        dt = game_framework.frame_time
        self.wait_time -= dt
        if self.wait_time < 0:
            run_dt = min(-self.wait_time, dt)
            self.x += self.speed * run_dt
            self.frame = (self.frame + run_dt / config.GUARD_RUN_FRAME_TIME) % RUN_FRAMES

    def draw(self):
        if day.phase == 'boss' or not camera.visible(self.x):
            return
        left = int(self.frame) * CELL_W
        # 아랫변 = 도로, 가로 가운데 = x
        # 낮 끝에는 지쳐 주저앉음 (임시: 1장을 높이 절반으로, 바닥에 붙임)
        h = CELL_H / 2 if day.phase == 'day_end' else CELL_H
        self.image.clip_draw(left, 0, CELL_W, CELL_H, camera.to_screen(self.x), config.ROAD_Y + h / 2, CELL_W, h)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
