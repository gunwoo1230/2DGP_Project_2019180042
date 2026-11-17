# 그림 칸 배경 여러 겹: 하늘(고정) → (해) → 구름 → 먼 산 → 먼 동네 → 가까운 동네, 멀수록 카메라를 천천히 따라감
# 그림은 resource/parts/bg_*.png, 크기·속도는 bg.json, 모두 게임 크기 그대로 그림
import json

from pico2d import load_image

import camera
import config
import day
import game_framework

with open('resource/parts/bg.json', encoding='utf-8') as f:
    INFO = json.load(f)

# 좌우가 이어지는 띠 (먼 것부터), 보스 무대에서는 산만
STRIPS = ('bg_mountain', 'bg_city', 'bg_town')
BOSS_STRIPS = ('bg_mountain',)
# 구름 (이름, 윗변 y)
CLOUDS = (('bg_cloud_1', 790), ('bg_cloud_2', 780), ('bg_cloud_3', 770))


def load(name):
    return load_image('resource/parts/' + name + '.png')


class Sky:
    # 그림 칸 전체를 덮는 하늘 (고정), 일기장 틀 바로 위에 그림
    def __init__(self):
        self.image = load('bg_sky')

    def update(self):
        pass

    def draw(self):
        self.image.draw((config.PLAY_LEFT + config.PLAY_RIGHT) / 2, (config.PLAY_BOTTOM + config.PLAY_TOP) / 2)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class Cloud:
    def __init__(self, name, top, x):
        self.image = load(name)
        self.top = top
        self.x = x      # 왼쪽 끝 화면 x

    def move(self, dx):
        # 그림 칸 왼쪽 밖으로 다 나가면 오른쪽 밖으로 (반대도), 한 바퀴 = 그림 칸 폭 + 구름 폭
        start = config.PLAY_LEFT - self.image.w
        span = config.PLAY_RIGHT - start
        self.x = start + (self.x + dx - start) % span

    def draw(self):
        self.image.draw(round(self.x) + self.image.w / 2, self.top - self.image.h / 2)


class Scenery:
    # 구름과 먼 산·동네 띠 (해 다음, 건물·도로 전에 그림)
    def __init__(self):
        self.strips = [(load(name), INFO[name]['speed']) for name in STRIPS]
        self.boss_strips = self.strips[:len(BOSS_STRIPS)]
        # 구름 처음 x는 그림 칸 안에 고르게
        play_w = config.PLAY_RIGHT - config.PLAY_LEFT
        self.clouds = [Cloud(name, top, config.PLAY_LEFT + play_w * (i + 0.3) / len(CLOUDS))
                       for i, (name, top) in enumerate(CLOUDS)]
        self.cloud_speed = INFO['bg_cloud_1']['speed']
        self.camera_x = camera.x

    def update(self):
        # 구름: 카메라가 움직인 만큼 × 속도 + 스스로 왼쪽으로 흐름
        dx = -(camera.x - self.camera_x) * self.cloud_speed - config.CLOUD_DRIFT * game_framework.frame_time
        self.camera_x = camera.x
        for cloud in self.clouds:
            cloud.move(dx)

    def draw(self):
        for cloud in self.clouds:
            cloud.draw()
        for image, speed in (self.boss_strips if day.phase == 'boss' else self.strips):
            self.draw_strip(image, speed)

    @staticmethod
    def draw_strip(image, speed):
        # 그림 칸 왼쪽 - offset부터 그림 폭 간격으로 그림 칸 오른쪽을 넘을 때까지 (아랫변 = 도로)
        # 그림 칸 밖으로 나온 부분은 Hud의 테두리 덮개가 덮음
        offset = round(camera.x * speed) % image.w
        x = config.PLAY_LEFT - offset
        while x < config.PLAY_RIGHT:
            image.draw(x + image.w / 2, config.ROAD_Y + image.h / 2)
            x += image.w

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
