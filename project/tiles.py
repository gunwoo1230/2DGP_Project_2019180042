# 건물 타일: 타일 정의, 발판, 타일 그리기
import math

from pico2d import load_image

import camera
import config
import parts
from config import ROAD_Y, ROOF_Y, TILE_W

# 건물 양식 후보 (그림만 바뀜, 발판은 같음)
WIDE_STYLES = ('wide_a', 'wide_b')
NARROW_STYLES = ('narrow_a', 'narrow_b')
ACCEL_STYLES = ('accel_a', 'accel_b')
STYLES = WIDE_STYLES + NARROW_STYLES + ACCEL_STYLES

# 양식 -> 건물 그림 (b 양식 그림이 오면 여기만 고침)
STYLE_PARTS = {'wide_a': 'building_wide_a', 'wide_b': 'building_wide_a',
               'narrow_a': 'building_narrow_a', 'narrow_b': 'building_narrow_a',
               'accel_a': 'building_accel_a', 'accel_b': 'building_accel_a'}


def roof_top_row(part):
    # 그림에서 지붕 높이(570) 줄: 평평한 지붕은 roof_top_row, 가속 지붕은 오른쪽 끝(낮은 쪽)
    info = parts.INFO[part]
    return info['roof_top_row'] if 'roof_top_row' in info else info['roof_right_top_row']


# 가속 지붕 왼쪽 높이: 그림의 왼쪽·오른쪽 지붕 줄 차이만큼 570보다 높음 (618)
_accel = parts.INFO[STYLE_PARTS['accel_a']]
ACCEL_LEFT_Y = ROOF_Y + _accel['roof_right_top_row'] - _accel['roof_left_top_row']

TILES = {
    # 'walls': 벽(건물 몸통) x 범위, 'styles': 양식 후보, 'roof': 지붕 발판 선분,
    # 'zone': 창문 구역 x 범위, 'windows': 창문 수,
    # 'pipe': 왼쪽 벽 배수관, 'pole': 왼쪽 빈터 전봇대 (타일 안 좌표)
    'start': {'walls': [], 'styles': (), 'roof': None, 'zone': None, 'windows': 0},
    'basic': {'walls': [(40, 560)], 'styles': WIDE_STYLES, 'roof': ('roof', 40, ROOF_Y, 560, ROOF_Y),
              'zone': (60, 540), 'windows': 3},
    'pipe':  {'walls': [(40, 560)], 'styles': WIDE_STYLES, 'roof': ('roof', 40, ROOF_Y, 560, ROOF_Y),
              'zone': (60, 540), 'windows': 3, 'pipe': True},
    'accel': {'walls': [(40, 560)], 'styles': ACCEL_STYLES, 'roof': ('accel', 40, ACCEL_LEFT_Y, 560, ROOF_Y),
              'zone': (60, 540), 'windows': 3},
    'gap':   {'walls': [(240, 560)], 'styles': NARROW_STYLES, 'roof': ('roof', 240, ROOF_Y, 560, ROOF_Y),
              'zone': (260, 540), 'windows': 2},
    'pole':  {'walls': [(200, 560)], 'styles': NARROW_STYLES, 'roof': ('roof', 200, ROOF_Y, 560, ROOF_Y),
              'zone': (220, 540), 'windows': 2, 'pole': True},
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
    # 리셋·재시작해도 한 번만 불러옴 (건물·창문 등 진짜 그림은 parts가 처음 그릴 때 불러옴)
    if not images:
        images['road'] = load_image('resource/placeholder/ph_ground.png')
        images['line'] = load_image('resource/placeholder/ph_rope.png')


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
            'pegs': [],         # 받침·못 (x0, y, x1, 그림, 좌우 뒤집기)
            'deco': []}         # 밟지 않는 배수관·전봇대 (그림, 왼쪽 x, 윗변 y)
    if tile_def['walls']:
        tile['style'] = rng.choice(tile_def['styles'])
        tile['windows'] = make_windows(tile_def, rng)
    if tile_def.get('pipe'):
        add_parts(tile, *pipe_parts(tile_def['walls'][0][0]))
    if tile_def.get('pole'):
        add_parts(tile, *pole_parts())
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
    platforms += [('peg', peg[0], peg[1], peg[2], peg[1]) for peg in tile['pegs']]
    tile['platforms'] = platforms


def add_parts(tile, deco, pegs):
    tile['deco'] += deco
    tile['pegs'] += pegs


def pipe_parts(w0):
    # 왼쪽 벽(x = w0) 바깥에 붙은 배수관: 아랫변 = 도로, 오른쪽 끝 = 벽 왼쪽 + PIPE_OVERLAP
    # 받침은 배수관 가운데에 가로 가운데를 맞추고, 발판 x 범위 = 받침 그림 x 범위
    pipe_w, pipe_h = parts.size('pipe')
    left = w0 + config.PIPE_OVERLAP - pipe_w
    center = left + pipe_w / 2
    half = parts.size('pipe_bracket')[0] / 2
    deco = [('pipe', left, ROAD_Y + pipe_h)]
    pegs = [(center - half, y, center + half, 'pipe_bracket', False) for y in config.PIPE_PEGS_Y]
    return deco, pegs


def pole_parts():
    # 왼쪽 빈터 전봇대 (기둥 가운데 = POLE_X 가운데, 땅 = 도로), 못은 높이마다 오른쪽·왼쪽
    # 오른쪽 못은 왼쪽 끝을, 왼쪽 못(좌우 뒤집음)은 오른쪽 끝을 기둥 가운데 너머 POLE_PEG_IN에 맞춤
    info = parts.INFO['pole']
    cx = sum(config.POLE_X) / 2
    deco = [('pole', cx - info['center_x'], ROAD_Y + info['base_row'])]
    peg_w = parts.size('pole_peg')[0]
    pegs = []
    for y, side in zip(config.POLE_PEGS_Y, config.POLE_PEG_SIDES):
        if side == 'R':
            x0 = cx - config.POLE_PEG_IN
            pegs.append((x0, y, x0 + peg_w, 'pole_peg', False))
        else:
            x1 = cx + config.POLE_PEG_IN
            pegs.append((x1 - peg_w, y, x1, 'pole_peg', True))
    return deco, pegs


def climb_x(name):
    # 오르는 곳(배수관 받침·전봇대 못)의 x 범위 (타일 안), 없으면 None
    tile_def = TILES[name]
    if tile_def.get('pipe'):
        pegs = pipe_parts(tile_def['walls'][0][0])[1]
    elif tile_def.get('pole'):
        pegs = pole_parts()[1]
    else:
        return None
    return min(peg[0] for peg in pegs), max(peg[2] for peg in pegs)


def draw_tile(tile, left):
    # 순서: 도로 → 건물 → 배수관·전봇대 → 받침·못 → 창문 → 창틀 (빨랫줄은 Level이 타일 다음에)
    screen_left = camera.to_screen(left)
    draw_rect(images['road'], screen_left, config.PLAY_BOTTOM, screen_left + TILE_W, ROAD_Y)
    if tile['walls']:
        # 건물 그림 한 장: 가로는 벽 x 범위에 맞춤 (그림 폭과 다르면 가로만 늘림, pole 360 <- 320)
        # 세로는 그대로, 지붕 줄 = 570 (아랫변 줄이 도로에 옴)
        part = STYLE_PARTS[tile['style']]
        x0, x1 = tile['walls'][0]
        parts.draw_top_left(part, screen_left + x0, ROOF_Y + roof_top_row(part), w=x1 - x0)
    for part, x, top in tile['deco']:
        parts.draw_top_left(part, screen_left + x, top)
    for x0, y, x1, part, flip in tile['pegs']:
        # 판 윗면 줄 = 발판 높이
        parts.draw_top_left(part, screen_left + x0, y + parts.INFO[part]['plate_top_row'], flip)
    for x, y in tile['windows']:
        parts.draw_window('window', screen_left + x, y)
    for x, y in tile['windows']:
        parts.draw_sill(screen_left + x, y)
