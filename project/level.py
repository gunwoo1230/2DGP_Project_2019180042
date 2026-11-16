# 레벨: 타일 목록으로 발판과 그릴 것을 만듦
from pico2d import draw_line

import camera
import config
from map_data import difficulty
from tiles import Platform, build_tile, climb_x, draw_slope, draw_tile, images, load_images, make_platforms


class Level:
    def __init__(self, tile_names, chunks, rng):
        load_images()
        self.load(tile_names, chunks, rng)

    def load(self, tile_names, chunks, rng):
        # 레벨 교체 (박스가 이 객체를 들고 있으므로 내용만 바꿈), 난수로 타일마다 양식·창문을 정함
        self.names = tile_names
        self.chunks = chunks    # 조각 범위 (첫 타일 번호, 마지막 타일 번호)
        # (만든 타일, 왼쪽 끝 월드 x)
        self.tiles = [(build_tile(name, rng), config.MAP_LEFT + config.TILE_W * i)
                      for i, name in enumerate(tile_names)]
        self.right = config.MAP_LEFT + config.TILE_W * len(tile_names)
        # 빨랫줄 발판 (두 타일에 걸침), 모든 타일을 만든 뒤 같은 난수로 정함
        self.lines = self.make_lines(rng)
        # 타일의 발판을 왼쪽 끝만큼 옮겨 월드 좌표로
        self.platforms = [Platform(kind, x0 + left, y0, x1 + left, y1)
                          for tile, left in self.tiles
                          for kind, x0, y0, x1, y1 in tile['platforms']] + self.lines
        # 빨랫줄 다음, 같은 난수로 방해 요소 -> 테이프 자리 (같은 시드면 같은 자리)
        self.hazards = self.place_hazards(rng)

    def make_lines(self, rng):
        # 이웃한 두 건물의 창틀을 잇는 빨랫줄: gap 앞은 항상, 그 밖은 가끔
        # 앞 건물 마지막 창틀 오른쪽 끝 -> 다음 건물 첫 창틀 왼쪽 끝
        lines = []
        for (prev, prev_left), (tile, left) in zip(self.tiles, self.tiles[1:]):
            if tile['name'] == 'gap' or (prev['name'] in config.LINE_FROM and tile['name'] in config.LINE_TO
                                         and rng.random() < config.CLOTHESLINE_CHANCE):
                px, py = prev['windows'][-1]
                nx, ny = tile['windows'][0]
                lines.append(Platform('line', prev_left + px + config.WINDOW_W, py, left + nx, ny))
                self.remove_line_pegs(tile)
        return lines

    def place_hazards(self, rng):
        # 타일마다 None / ('window', 창문 번호) / ('puddle', 타일 안 x), 조각이 없는 맵(보스 무대)은 없음
        # 첫 건물 몇 채는 없고, 바로 앞 타일과 같은 종류는 연달아 나오지 않음
        hazards = [None] * len(self.tiles)
        if rng is None:
            return hazards
        prev_kind = None
        for i, (tile, left) in enumerate(self.tiles):
            kind = None
            # 앞 조건이 거짓이면 난수를 쓰지 않음 (참고 구현과 같은 난수 순서)
            if i > config.HAZARD_FREE and tile['name'] != 'start'                     and rng.random() < config.HAZARD_CHANCE[difficulty(i - 1)]:
                kind = rng.choice([k for k in ('window', 'puddle') if k != prev_kind])
                if kind == 'window':
                    hazards[i] = ('window', rng.randrange(len(tile['windows'])))
                else:
                    hazards[i] = ('puddle', self.puddle_x(tile['name'], rng))
            prev_kind = kind
        return hazards

    @staticmethod
    def puddle_x(name, rng):
        # 물웅덩이 왼쪽 끝 x (타일 안): 오르는 곳에서 PUDDLE_CLIMB_GAP 이상 떨어진 자리 중 하나
        lo = config.PUDDLE_EDGE
        hi = config.TILE_W - config.PUDDLE_EDGE - config.PUDDLE_W
        climb = climb_x(name)
        if climb is None:
            return rng.choice(range(lo, hi + 1))
        a, b = climb[0] - config.PUDDLE_CLIMB_GAP, climb[1] + config.PUDDLE_CLIMB_GAP
        return rng.choice([x for x in range(lo, hi + 1) if x + config.PUDDLE_W <= a or x >= b])

    def place_tapes(self, rng):
        pass

    @staticmethod
    def remove_line_pegs(tile):
        # 빨랫줄이 배수관 앞 틈을 지나면 줄 높이(창틀 높이 범위)의 받침을 뺌 (줄이 대신함)
        low, high = min(config.WINDOW_YS), max(config.WINDOW_YS)
        if tile['name'] == 'pipe':
            tile['pegs'] = [peg for peg in tile['pegs'] if not low <= peg[1] <= high]
            make_platforms(tile)

    def update(self):
        pass

    def draw(self):
        for tile, left in self.tiles:
            # 타일 양쪽 끝이 모두 화면 밖이면 건너뜀
            if camera.to_screen(left + config.TILE_W) >= -config.DRAW_MARGIN \
                    and camera.to_screen(left) <= config.SCREEN_W + config.DRAW_MARGIN:
                draw_tile(tile, left)
        self.draw_lines()

    def draw_lines(self):
        # 빨랫줄은 두 타일에 걸치므로 타일을 다 그린 뒤 따로, 두 끝이 모두 화면 한쪽 밖이면 건너뜀
        for line in self.lines:
            x0, x1 = camera.to_screen(line.x0), camera.to_screen(line.x1)
            if x1 < -config.DRAW_MARGIN or x0 > config.SCREEN_W + config.DRAW_MARGIN:
                continue
            draw_slope(images['line'], x0, line.y0, x1, line.y1, config.PLATFORM_THICK['line'])

    def draw_debug(self):
        # F1: 발판 윗면 선 (빨강, 가속 지붕·빨랫줄은 주황)
        for p in self.platforms:
            color = (255, 140, 0) if p.kind in config.ACCEL_RATES else (255, 0, 0)
            draw_line(camera.to_screen(p.x0), p.y0, camera.to_screen(p.x1), p.y1, *color)

    def tile_index(self, x):
        # x가 속한 타일 번호 (시작 칸 = 0)
        i = int((x - config.MAP_LEFT) // config.TILE_W)
        return min(max(i, 0), len(self.tiles) - 1)

    def next_tile_left(self, x):
        # x가 속한 타일의 다음 타일 왼쪽 끝, 마지막 타일이면 None
        i = int((x - config.MAP_LEFT) // config.TILE_W) + 1
        return self.tiles[i][1] if i < len(self.tiles) else None

    def find_landing(self, prev_x, prev_y, x, y):
        # 위에서 윗면을 지나 내려온 발판 중 가장 높은 것 (경사가 있어 각 위치의 윗면과 비교)
        hits = [p for p in self.platforms
                if p.covers(x) and prev_y >= p.surface_y(prev_x) and p.surface_y(x) > y]
        return max(hits, key=lambda p: p.surface_y(x), default=None)

    def find_ground(self, x, y):
        # 발밑에 붙을 수 있는 발판 중 가장 높은 것
        hits = [p for p in self.platforms
                if p.covers(x) and abs(p.surface_y(x) - y) <= config.SNAP]
        return max(hits, key=lambda p: p.surface_y(x), default=None)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
