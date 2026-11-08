# 그림일기 화면: 배경(맨 아래), 해, 지금·도망친 지, 원고지 팁, 테이프 생명 칸(맨 위)
import math

from pico2d import load_image

import config
import day
import font_data
import game_framework
from sprite_data import draw_item

# 구간별 지금 칸 낱말
NOW_WORDS = {'chase': ('낮', '주택가'), 'boss': ('저녁', '공원')}
# 구간별 팁 목록
TIP_LISTS = {'chase': font_data.TIP_LIST['day'], 'boss': font_data.TIP_LIST['boss']}


class Background:
    def __init__(self):
        self.image = load_image('resource/diary_frame.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(config.SCREEN_W / 2, config.SCREEN_H / 2)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class Sun:
    # 하늘의 해: 진행률에 따라 타원 길을 따라 왼쪽 아래 -> 위 -> 오른쪽 아래 (화면 좌표)
    def __init__(self):
        self.image = load_image('resource/placeholder/ph_sun.png')

    def update(self):
        pass

    def draw(self):
        if day.phase == 'boss':
            return
        a = math.pi * day.sun_p
        x = config.SUN_CENTER_X - config.SUN_RX * math.cos(a)
        y = config.SUN_CENTER_Y + config.SUN_RY * math.sin(a)
        self.image.draw(x, y)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class Gauge:
    # 경비원과의 거리 (임시 막대): 꽉 차면 안전, 비면 잡힘
    def __init__(self, box, guard):
        self.bg = load_image('resource/placeholder/ph_gauge_bg.png')
        self.fill = load_image('resource/placeholder/ph_gauge.png')
        self.box = box
        self.guard = guard

    def update(self):
        pass

    def ratio(self):
        dist = self.box.x - self.guard.x
        r = (dist - config.CATCH_DIST) / (config.GUARD_START_GAP - config.CATCH_DIST)
        return min(max(r, 0), 1)

    def draw(self):
        if not self.guard.enabled or day.phase == 'boss':
            return
        w, h = config.GAUGE_W, config.GAUGE_H
        self.bg.draw(config.GAUGE_X, config.GAUGE_Y, w, h)
        fill_w = w * self.ratio()
        if fill_w > 0:
            # 왼쪽 끝에 맞춰 채움
            self.fill.draw(config.GAUGE_X - w / 2 + fill_w / 2, config.GAUGE_Y, fill_w, h)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class Hud:
    def __init__(self):
        self.frame = load_image('resource/diary_frame.png')
        self.font = load_image('resource/font_sheet.png')
        self.items = load_image('resource/item_sheet.png')
        self.lives = config.TAPE_START
        self.reserved = 0       # 날아오는 중인 테이프 수
        self.zone = 'chase'
        self.tip_index = 0
        self.tip_time = 0.0

    def update(self):
        self.tip_time += game_framework.frame_time
        if self.tip_time >= config.TIP_INTERVAL:
            self.tip_time -= config.TIP_INTERVAL
            self.tip_index = (self.tip_index + 1) % len(TIP_LISTS[self.zone])

    def draw(self):
        self.draw_frame_strips()
        self.draw_now()
        self.draw_time()
        self.draw_tip()
        self.draw_lives()

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass

    def set_zone(self, zone):
        # 구간이 바뀌면 팁을 첫 문장부터 다시 씀
        self.zone = zone
        self.tip_index = 0
        self.tip_time = 0.0

    def reset_lives(self):
        self.lives = config.TAPE_START
        self.reserved = 0

    def reserve_slot(self):
        # 날아오는 중인 테이프의 칸을 미리 잡아 둠, 그 칸 번호를 돌려줌
        slot = self.lives + self.reserved
        self.reserved += 1
        return slot

    def add_life(self):
        self.lives = min(self.lives + 1, config.TAPE_MAX)
        self.reserved = max(self.reserved - 1, 0)

    def is_full(self):
        return self.lives + self.reserved >= config.TAPE_MAX

    def draw_frame_strips(self):
        # 플레이 칸 밖으로 삐져나온 맵을 배경의 좌우 띠로 다시 덮음
        w, h = config.FRAME_STRIP_W, config.FRAME_STRIP_TOP - config.FRAME_STRIP_BOTTOM
        y = (config.FRAME_STRIP_BOTTOM + config.FRAME_STRIP_TOP) / 2
        for left in (0, config.SCREEN_W - w):
            self.frame.clip_draw(left, config.FRAME_STRIP_BOTTOM, w, h, left + w / 2, y)

    def draw_now(self):
        time_word, place_word = NOW_WORDS[self.zone]
        font_data.draw_now(self.font, time_word, place_word, config.UI_NOW_X, config.UI_HEADER_Y)

    def draw_time(self):
        # 도망친 지 N일 N시간 N분
        m = day.minutes()
        for n, x in ((m // 1440, config.UI_DAY_X), (m // 60 % 24, config.UI_HOUR_X), (m % 60, config.UI_MIN_X)):
            font_data.draw_number(self.font, n, x, config.UI_HEADER_Y)

    def draw_tip(self):
        tip_key = TIP_LISTS[self.zone][self.tip_index]
        count = int(self.tip_time / config.TIP_CHAR_TIME)      # 지금까지 써진 글자 수
        font_data.draw_tip(self.font, font_data.TIPS[tip_key], config.UI_TIP_X, config.UI_TIP_Y, count=count)

    def draw_lives(self):
        for i in range(config.TAPE_MAX):
            alpha = 1 if i < self.lives else config.UI_LIFE_EMPTY_ALPHA
            self.items.opacify(alpha)
            draw_item(self.items, 'tape_ui', 0, config.UI_LIFE_X + config.UI_LIFE_GAP * i, config.UI_LIFE_Y, scale=1)
        # 같은 시트의 다른 그림이 흐려지지 않도록 복구
        self.items.opacify(1)
