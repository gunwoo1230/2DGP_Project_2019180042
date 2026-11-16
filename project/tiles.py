# 건물 타일: 타일 정의, 발판, 타일 그리기
import math

from pico2d import load_image

import camera
import config
from config import ROAD_Y, ROOF_Y, TILE_W

# 건물 양식 후보 (그림만 바뀜, 발판은 같음)
WIDE_STYLES = ('wide_a', 'wide_b')
NARROW_STYLES = ('narrow_a', 'narrow_b')
ACCEL_STYLES = ('accel_a', 'accel_b')
STYLES = WIDE_STYLES + NARROW_STYLES + ACCEL_STYLES

TILES = {
    # 'walls': 벽(건물 몸통) x 범위, 'styles': 양식 후보, 'roof': 지붕 발판 선분,
    # 'zone': 창문 구역 x 범위, 'windows': 창문 수, 'deco': 밟지 않는 장식(배수관·전봇대) 사각형,
    # 'pegs': 받침·못 (x0, y, x1), 'pipe': 왼쪽 벽 배수관, 'pole': 왼쪽 빈터 전봇대 (타일 안 좌표)
    'start': {'walls': [], 'styles': (), 'roof': None, 'zone': None, 'windows': 0, 'deco': [], 'pegs': []},
    'basic': {'walls': [(40, 560)], 'styles': WIDE_STYLES, 'roof': ('roof', 40, ROOF_Y, 560, ROOF_Y),
              'zone': (60, 540), 'windows': 3, 'deco': [], 'pegs': []},
    'pipe':  {'walls': [(40, 560)], 'styles': WIDE_STYLES, 'roof': ('roof', 40, ROOF_Y, 560, ROOF_Y),
              'zone': (60, 540), 'windows': 3, 'deco': [], 'pegs': [], 'pipe': True},
    'accel': {'walls': [(40, 560)], 'styles': ACCEL_STYLES, 'roof': ('accel', 40, 630, 560, ROOF_Y),
              'zone': (60, 540), 'windows': 3, 'deco': [], 'pegs': []},
    'gap':   {'walls': [(240, 560)], 'styles': NARROW_STYLES, 'roof': ('roof', 240, ROOF_Y, 560, ROOF_Y),
              'zone': (260, 540), 'windows': 2, 'deco': [], 'pegs': []},
    'pole':  {'walls': [(200, 560)], 'styles': NARROW_STYLES, 'roof': ('roof', 200, ROOF_Y, 560, ROOF_Y),
              'zone': (220, 540), 'windows': 2, 'deco': [], 'pegs': [], 'pole': True},
}

images = {}


class Platform:
    # 윗면이 밟히는 선분 (월드 좌표)
    def __init__(self, kind, x0, y0, x1, y1):
        self.kind = kind
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1

    def surface_y(self, x):
        # x에서의 윗면 높이, 발판 밖 x는 가까운 끝의 높이
        x = max(self.x0, min(x, self.x1))
        return self.y0 + (self.y1 - self.y0) * (x - self.x0) / (self.x1 - self.x0)

    def covers(self, x):
        # 박스 발 폭이 발판 x 범위와 겹치는지
        return x + config.FOOT_HALF >= self.x0 and x - config.FOOT_HALF <= self.x1


def load_images():
    # 리셋·재시작해도 한 번만 불러옴
    if not images:
        images['road'] = load_image('resource/placeholder/ph_ground.png')
        for style in STYLES:
            images['wall_' + style] = load_image(f'resource/placeholder/ph_wall_{style}.png')
        images['window'] = load_image('resource/placeholder/ph_window.png')
        images['deco'] = load_image('resource/placeholder/ph_pipe.png')
        images['roof'] = load_image('resource/placeholder/ph_roof.png')
        images['ledge'] = load_image('resource/placeholder/ph_ledge.png')
        images['peg'] = load_image('resource/placeholder/ph_peg.png')
        images['accel'] = load_image('resource/placeholder/ph_accel.png')


def draw_rect(image, x0, y0, x1, y1):
    image.draw((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0)


def draw_slope(image, x0, y0, x1, y1, thick):
    # 윗면이 선분에 오도록, 가운데를 두께의 절반만큼 선분 아래쪽 수직 방향으로 내림
    dx, dy = x1 - x0, y1 - y0
    length = math.hypot(dx, dy)
    cx = (x0 + x1) / 2 + dy / length * thick / 2
    cy = (y0 + y1) / 2 - dx / length * thick / 2
    image.composite_draw(math.atan2(dy, dx), '', cx, cy, length, thick)


def build_tile(name, rng):
    # 타일 하나를 만듦: 그릴 것과 발판 (타일 안 좌표), 난수는 양식·창문에 씀
    tile_def = TILES[name]
    tile = {'name': name, 'style': None, 'roof': tile_def['roof'],
            'walls': list(tile_def['walls']),
            'windows': [],      # 창문 (왼쪽 끝 x, 창틀 y)
            'pegs': list(tile_def['pegs']),     # 받침·못 하나씩
            'deco': list(tile_def['deco'])}
    if tile_def['walls']:
        tile['style'] = rng.choice(tile_def['styles'])
        tile['windows'] = make_windows(tile_def, rng)
    if tile_def.get('pipe'):
        add_pipe(tile)
    if tile_def.get('pole'):
        add_pole(tile)
    make_platforms(tile)
    return tile


def make_windows(tile_def, rng):
    # 창문 위치·높이를 랜덤으로: 남는 폭을 창문 앞·사이·뒤 빈칸에 랜덤하게 나눠 줌
    z0, z1 = tile_def['zone']
    n = tile_def['windows']
    free = (z1 - z0) - n * config.WINDOW_W - (n - 1) * config.WINDOW_GAP_MIN
    cuts = sorted(rng.random() * free for _ in range(n))
    windows = []
    x, prev = z0, 0
    for cut in cuts:
        x += cut - prev
        prev = cut
        windows.append((round(x), rng.choice(config.WINDOW_YS)))
        x += config.WINDOW_W + config.WINDOW_GAP_MIN
    return windows


def make_platforms(tile):
    # 발판 목록 (도로 → 지붕 → 창틀 → 받침·못), 받침을 빼면 다시 만듦
    platforms = [('road', 0, ROAD_Y, TILE_W, ROAD_Y)]
    if tile['roof']:
        platforms.append(tile['roof'])
    platforms += [('ledge', x, y, x + config.WINDOW_W, y) for x, y in tile['windows']]
    platforms += [('peg', x0, y, x1, y) for x0, y, x1 in tile['pegs']]
    tile['platforms'] = platforms


def add_pipe(tile):
    # 왼쪽 벽 바깥에 바짝 붙은 배수관, 받침은 앞 타일과의 틈 쪽으로 튀어나옴
    w0 = tile['walls'][0][0]
    tile['deco'].append(('pipe', w0 - config.PIPE_W, ROAD_Y, w0, ROOF_Y))
    tile['pegs'] += [(w0 - config.PIPE_PEG_W, y, w0) for y in config.PIPE_PEGS_Y]


def add_pole(tile):
    # 왼쪽 빈터 전봇대와 못 (570 못에서 양옆 지붕으로 건너감)
    x0, x1 = config.POLE_X
    tile['deco'].append(('pole', x0, ROAD_Y, x1, config.POLE_TOP))
    tile['pegs'] += [(config.POLE_PEG_X[0], y, config.POLE_PEG_X[1]) for y in config.POLE_PEGS_Y]


def draw_tile(tile, left):
    # 진짜 타일 그림이 오면 이 함수 안에서 교체
    # 순서: 도로 → 벽 → 창문 → 배수관·전봇대 → 발판
    screen_left = camera.to_screen(left)
    draw_rect(images['road'], screen_left, config.PLAY_BOTTOM, screen_left + TILE_W, ROAD_Y)
    for x0, x1 in tile['walls']:
        draw_rect(images['wall_' + tile['style']], screen_left + x0, ROAD_Y, screen_left + x1, ROOF_Y)
    inset = config.WINDOW_INSET
    for x, y in tile['windows']:
        draw_rect(images['window'], screen_left + x + inset, y, screen_left + x + config.WINDOW_W - inset,
                  y + config.WINDOW_H)
    for _, x0, y0, x1, y1 in tile['deco']:
        draw_rect(images['deco'], screen_left + x0, y0, screen_left + x1, y1)
    for kind, x0, y0, x1, y1 in tile['platforms']:
        if kind in ('roof', 'ledge', 'peg'):
            # 윗면이 발판 선에 오도록 두께만큼 아래로
            draw_rect(images[kind], screen_left + x0, y0 - config.PLATFORM_THICK[kind], screen_left + x1, y0)
        elif kind == 'accel':
            draw_slope(images[kind], screen_left + x0, y0, screen_left + x1, y1, config.PLATFORM_THICK[kind])
