# w2_2 규칙 시험용 참고 구현 (게임 코드 아님): w2_1 맵 + 조각 범위 + 방해 요소 자리 + 테이프 자리
# 난수 쓰는 순서: 맵(조각) -> 타일(양식·창문) -> 빨랫줄 -> 방해 요소 -> 테이프
import random
from w2_1_gen_reference import (TILES, EASY, NORMAL, HARD, BUILDINGS, TILE_W, WIN_W, ROAD, ROOF,
                   build, clotheslines, CLOTHESLINE_CHANCE)

CHUNK_LEVELS = (20, 40)
HAZARD_CHANCE = (0.2, 0.35, 0.5)        # 쉬움·보통·어려움: 건물 한 채에 방해 요소가 나올 확률
HAZARD_FREE = 2                         # 첫 건물 몇 채는 방해 요소 없음
PUDDLE_W = 140
PUDDLE_CLIMB_GAP = 80                   # 배수관·전봇대 받침에서 이만큼 떨어뜨림
CLIMB_X = {'pipe': (2.5, 53.5), 'pole': (46, 154)}  # 오르는 곳 x 범위 (타일 안), 11/17 진짜 그림 받침·못 폭
TAPE_FLOOR_WEIGHT = {'roof': 5, 'ledge': 3}
TAPE_ROOF_INSET = 40

def level_of(built):
    return 0 if built < CHUNK_LEVELS[0] else 1 if built < CHUNK_LEVELS[1] else 2

def make_day_map(rng):
    """(타일 이름 목록, 조각 범위 목록 [(첫 타일 번호, 마지막 타일 번호)])"""
    names = ['start']; chunks = []; last = None
    while len(names) - 1 < BUILDINGS:
        built = len(names) - 1
        pool = (EASY, NORMAL, HARD)[level_of(built)]
        chunk = rng.choice([c for c in pool if c is not last]); last = chunk
        first = len(names)
        for name in chunk:
            if len(names) - 1 >= BUILDINGS: break
            names.append(rng.choice(('pipe', 'pole')) if name == 'climb' else name)
        chunks.append((first, len(names) - 1))
    return names, chunks

def test_chunks(names, size=3):
    return [(i, min(i + size - 1, len(names) - 1)) for i in range(1, len(names), size)]

def puddle_x(name, rng):
    lo, hi = 20, TILE_W - 20 - PUDDLE_W
    blocked = None
    if name in CLIMB_X:
        a, b = CLIMB_X[name]; blocked = (a - PUDDLE_CLIMB_GAP, b + PUDDLE_CLIMB_GAP)
    ok = [x for x in range(lo, hi + 1) if not blocked or x + PUDDLE_W <= blocked[0] or x >= blocked[1]]
    return rng.choice(ok)

def place_hazards(names, tiles, rng):
    """타일 번호마다 None 또는 ('window', 창문 번호) / ('puddle', 타일 안 x)"""
    hz = [None] * len(names); prev_kind = None
    for i, name in enumerate(names):
        kind = None
        if i > HAZARD_FREE and name != 'start' and rng.random() < HAZARD_CHANCE[level_of(i - 1)]:
            kinds = [k for k in ('window', 'puddle') if k != prev_kind]
            kind = rng.choice(kinds)
            hz[i] = ('window', rng.randrange(len(tiles[i]['wins']))) if kind == 'window' else ('puddle', puddle_x(name, rng))
        prev_kind = kind
    return hz

def place_tapes(names, tiles, lines, hz, chunks, rng):
    """조각마다 테이프 1개: (월드 x, 발 높이 y, 층)"""
    tapes = []
    for first, last in chunks:
        spots = {'roof': [], 'ledge': []}
        for i in range(first, last + 1):
            L = i * TILE_W; t = tiles[i]
            for k, x0, y0, x1, y1 in t['plats']:
                if k in ('roof', 'accel'):
                    spots['roof'].append(('roof', L + x0 + TAPE_ROOF_INSET, L + x1 - TAPE_ROOF_INSET, x0, y0, x1, y1, L))
            for j, (x, y) in enumerate(t['wins']):
                if hz[i] != ('window', j):
                    spots['ledge'].append(('pt', L + x + WIN_W / 2, y))
        for k, x0, y0, x1, y1 in lines:
            if first <= int(x0 // TILE_W) <= last:
                spots['ledge'].append(('pt', (x0 + x1) / 2, (y0 + y1) / 2))
        floors = [f for f in ('roof', 'ledge') if spots[f]]
        floor = rng.choices(floors, weights=[TAPE_FLOOR_WEIGHT[f] for f in floors])[0]
        s = rng.choice(spots[floor])
        if s[0] == 'pt':
            tapes.append((s[1], s[2], floor))
        else:
            _, a, b, x0, y0, x1, y1, L = s
            x = rng.uniform(a, b); lx = x - L
            tapes.append((x, y0 + (y1 - y0) * (lx - x0) / (x1 - x0), floor))
    return tapes

def build_all(names, chunks, rng):
    tiles = [build(n, rng) for n in names]
    lines = clotheslines(names, tiles, rng)
    hz = place_hazards(names, tiles, rng)
    tapes = place_tapes(names, tiles, lines, hz, chunks, rng)
    return tiles, lines, hz, tapes
