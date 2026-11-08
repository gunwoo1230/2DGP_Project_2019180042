# 경비원 (임시 사각형): 도로를 따라 박스를 쫓아옴
from pico2d import load_image

import camera
import config
import day
import game_framework


class Guard:
    image = None

    def __init__(self):
        if Guard.image is None:
            Guard.image = load_image('resource/placeholder/ph_guard.png')
        self.enabled = True     # 디버그로 끌 수 있음
        self.reset()

    def reset(self):
        self.x = config.BOX_START_X - config.GUARD_START_GAP    # 발 가운데, 화면 왼쪽 밖에서 시작
        self.wait_time = config.GUARD_START_DELAY

    def update(self):
        # 추격 중에만 움직임, 기다리는 시간이 끝난 프레임은 남은 만큼만 감
        if not self.enabled or day.phase != 'chase':
            return
        dt = game_framework.frame_time
        self.wait_time -= dt
        if self.wait_time < 0:
            self.x += config.GUARD_SPEED * min(-self.wait_time, dt)

    def draw(self):
        if day.phase == 'boss' or not camera.visible(self.x):
            return
        self.image.draw(camera.to_screen(self.x), config.ROAD_Y + config.GUARD_H / 2, config.GUARD_W, config.GUARD_H)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
