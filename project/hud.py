# 그림일기 화면: 배경, 지금·도망친 지, 원고지 팁, 테이프 생명 칸
from pico2d import load_image

import config
import font_data
import game_framework
from sprite_data import draw_item

# 구간별 지금 칸 낱말
NOW_WORDS = {'chase': ('낮', '주택가'), 'boss': ('저녁', '공원')}
# 구간별 팁 목록
TIP_LISTS = {'chase': font_data.TIP_LIST['day'], 'boss': font_data.TIP_LIST['boss']}


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

    def draw_now(self):
        time_word, place_word = NOW_WORDS[self.zone]
        font_data.draw_now(self.font, time_word, place_word, config.UI_NOW_X, config.UI_HEADER_Y)

    def draw_time(self):
        # 1주차는 0일 0시간 0분 고정 (시계는 3주차)
        for x in (config.UI_DAY_X, config.UI_HOUR_X, config.UI_MIN_X):
            font_data.draw_number(self.font, 0, x, config.UI_HEADER_Y)

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
