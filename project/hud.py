# 그림일기 화면: 배경(맨 아래), 해, 지금·도망친 지, 원고지 팁, 테이프 생명 칸(맨 위)
from pico2d import load_image

import camera
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
    # 하늘의 해: 진행률에 따라 플레이 칸 맨 위를 왼쪽 -> 오른쪽 일직선으로 (화면 좌표)
    def __init__(self):
        self.image = load_image('resource/placeholder/ph_sun.png')

    def update(self):
        pass

    def draw(self):
        if day.phase == 'boss':
            return
        x = config.SUN_LEFT_X + (config.SUN_RIGHT_X - config.SUN_LEFT_X) * day.sun_p
        s = config.SUN_SCALE
        self.image.draw(x, config.SUN_Y, self.image.w * s, self.image.h * s)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class GuardMarker:
    # 화면 왼쪽 밖 경비원 표시: 가까울수록 크게, 아주 가까우면 깜빡임 (모자 그림 대신 임시 네모)
    def __init__(self, guard):
        self.image = load_image('resource/placeholder/ph_guard.png')
        self.font = load_image('resource/font_sheet.png')
        self.guard = guard

    def update(self):
        pass

    def offscreen(self):
        # 경비원 오른쪽 끝이 플레이 칸 왼쪽 끝보다 얼마나 밖에 있는지 (0 이하면 화면 안)
        return config.PLAY_LEFT - camera.to_screen(self.guard.x + config.GUARD_W / 2)

    def scale(self, off):
        # 막 들어오기 직전 1배, MARKER_FAR 이상 떨어지면 MARKER_MIN_SCALE배
        t = min(off / config.MARKER_FAR, 1)
        return 1 - (1 - config.MARKER_MIN_SCALE) * t

    def draw(self):
        if not self.guard.enabled or day.phase in ('boss', 'day_end'):
            return
        off = self.offscreen()
        if off <= 0:
            return
        size = config.MARKER_SIZE * self.scale(off)
        self.image.draw(config.MARKER_X, config.MARKER_Y, size, size)
        # 네모 왼쪽에 붙는 ← (크기는 그대로)
        l, b, w, h = font_data.CELL_RECT['←']
        s = config.MARKER_ARROW_SCALE
        arrow_x = config.MARKER_X - size / 2 - config.MARKER_ARROW_GAP - w * s / 2
        self.font.clip_draw(l, b, w, h, arrow_x, config.MARKER_Y, w * s, h * s)

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
