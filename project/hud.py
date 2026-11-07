# 그림일기 화면: 배경, 지금·도망친 지, 원고지 팁, 테이프 생명 칸
from pico2d import load_image

import config
import font_data
import game_framework

# 구간별 지금 칸 낱말
NOW_WORDS = {'chase': ('낮', '주택가'), 'boss': ('저녁', '공원')}


class Hud:
    def __init__(self):
        self.frame = load_image('resource/diary_frame.png')
        self.font = load_image('resource/font_sheet.png')
        self.zone = 'chase'
        self.tip_index = 0
        self.tip_time = 0.0

    def update(self):
        self.tip_time += game_framework.frame_time
        if self.tip_time >= config.TIP_INTERVAL:
            self.tip_time -= config.TIP_INTERVAL
            self.tip_index = (self.tip_index + 1) % len(font_data.TIP_LIST['day'])

    def draw(self):
        self.frame.draw(config.SCREEN_W / 2, config.SCREEN_H / 2)
        self.draw_now()
        self.draw_time()
        self.draw_tip()
        self.draw_lives()

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass

    def set_zone(self, zone):
        pass

    def add_life(self):
        pass

    def is_full(self):
        pass

    def draw_now(self):
        time_word, place_word = NOW_WORDS[self.zone]
        font_data.draw_now(self.font, time_word, place_word, config.UI_NOW_X, config.UI_HEADER_Y)

    def draw_time(self):
        # 1주차는 0일 0시간 0분 고정 (시계는 3주차)
        for x in (config.UI_DAY_X, config.UI_HOUR_X, config.UI_MIN_X):
            font_data.draw_number(self.font, 0, x, config.UI_HEADER_Y)

    def draw_tip(self):
        tip_key = font_data.TIP_LIST['day'][self.tip_index]
        count = int(self.tip_time / config.TIP_CHAR_TIME)      # 지금까지 써진 글자 수
        font_data.draw_tip(self.font, font_data.TIPS[tip_key], config.UI_TIP_X, config.UI_TIP_Y, count=count)

    def draw_lives(self):
        pass
