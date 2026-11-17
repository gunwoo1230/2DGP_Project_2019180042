# w2_1 규칙 시험용 참고 구현 (게임 코드 아님) — 11/16 수정판
import random
ROAD, LEDGE_MIN, ROOF, TILE_W = 210, 375, 570, 600
WIN_W, WIN_GAP, WIN_YS = 90, 50, (380, 385, 390, 395, 400, 405)
PIPE_W, PIPE_OVERLAP, PIPE_PEG_W, PIPE_PEGS = 28, 2, 51, (300, 390, 480)    # 11/17 진짜 그림 폭 (배수관 28, 받침 51)
POLE_PEGS = (300, 390, 480, 570)
POLE_PEG_X = {'R': (97, 154), 'L': (46, 103)}     # 11/17 못 그림 폭 57, 높이마다 오른쪽·왼쪽 번갈아
POLE_PEG_SIDES = ('R', 'L', 'R', 'L')
WIDE_STYLES, NARROW_STYLES, ACCEL_STYLES = ('wide_a', 'wide_b'), ('narrow_a', 'narrow_b'), ('accel_a', 'accel_b')
TILES = {
 'start': dict(wall=None),
 'basic': dict(wall=(40, 560), roof=('roof', 40, ROOF, 560, ROOF), zone=(60, 540), windows=3, styles=WIDE_STYLES),
 'pipe':  dict(wall=(40, 560), roof=('roof', 40, ROOF, 560, ROOF), zone=(60, 540), windows=3, styles=WIDE_STYLES, pipe=True),
 'accel': dict(wall=(40, 560), roof=('accel', 40, 618, 560, ROOF), zone=(60, 540), windows=3, styles=ACCEL_STYLES),
 'gap':   dict(wall=(240, 560), roof=('roof', 240, ROOF, 560, ROOF), zone=(260, 540), windows=2, styles=NARROW_STYLES),
 'pole':  dict(wall=(200, 560), roof=('roof', 200, ROOF, 560, ROOF), zone=(220, 540), windows=2, styles=NARROW_STYLES, pole=True),
}
EASY = [['basic', 'climb', 'basic'], ['basic', 'basic', 'climb', 'basic'], ['basic', 'accel', 'basic', 'climb']]
NORMAL = [['basic', 'accel', 'gap', 'climb'], ['climb', 'basic', 'accel', 'gap'], ['basic', 'climb', 'accel', 'basic', 'basic']]
HARD = [['accel', 'gap', 'accel', 'gap', 'climb'], ['basic', 'accel', 'gap', 'basic', 'accel', 'gap', 'climb'], ['climb', 'accel', 'gap', 'basic', 'accel', 'basic']]
BUILDINGS = 60

def make_day_map(rng):
    out = ['start']; last = None
    while len(out) - 1 < BUILDINGS:
        n = len(out) - 1
        pool = EASY if n < 20 else NORMAL if n < 40 else HARD
        chunk = rng.choice([c for c in pool if c is not last]); last = chunk
        for name in chunk:
            if len(out) - 1 >= BUILDINGS: break
            if name == 'climb': name = rng.choice(('pipe', 'pole'))
            out.append(name)
    return out

def windows(tile, rng):
    z0, z1 = tile['zone']; n = tile['windows']
    free = (z1 - z0) - n * WIN_W - (n - 1) * WIN_GAP
    cuts = sorted(rng.random() * free for _ in range(n)); x = z0; prev = 0; res = []
    for c in cuts:
        x += c - prev; prev = c
        res.append((round(x), rng.choice(WIN_YS))); x += WIN_W + WIN_GAP
    return res

def build(name, rng):
    t = TILES[name]
    plats = [('road', 0, ROAD, TILE_W, ROAD)]; deco = []; wins = []; style = None
    if t['wall']:
        style = rng.choice(t['styles'])
        plats.append(t['roof'])
        for x, y in windows(t, rng):
            plats.append(('ledge', x, y, x + WIN_W, y)); wins.append((x, y))
        w0 = t['wall'][0]
        if t.get('pipe'):
            pc = w0 + PIPE_OVERLAP - PIPE_W / 2     # 배수관 가운데 = 받침 가운데
            deco.append(('pipe', w0 + PIPE_OVERLAP - PIPE_W, ROAD, w0 + PIPE_OVERLAP, 580))
            plats += [('peg', pc - PIPE_PEG_W / 2, y, pc + PIPE_PEG_W / 2, y) for y in PIPE_PEGS]
        if t.get('pole'):
            deco.append(('pole', 83, ROAD, 117, 658))
            plats += [('peg', POLE_PEG_X[s][0], y, POLE_PEG_X[s][1], y) for y, s in zip(POLE_PEGS, POLE_PEG_SIDES)]
    return dict(name=name, wall=t['wall'], style=style, plats=plats, deco=deco, wins=wins)

LINE_RATE = 1.5
CLOTHESLINE_CHANCE = 0.3
LINE_FROM = ('basic', 'pipe', 'accel', 'gap', 'pole')
LINE_TO = ('basic', 'pipe', 'accel')
def clotheslines(names, tiles, rng):
    """이웃한 두 건물: accel→gap은 항상, 그 밖(앞 LINE_FROM, 다음 LINE_TO)은 30%. 앞 마지막 창틀 오른쪽 끝 → 다음 첫 창틀 왼쪽 끝"""
    lines = []
    for i in range(1, len(names)):
        a, b = names[i - 1], names[i]
        if b == 'gap' or (a in LINE_FROM and b in LINE_TO and rng.random() < CLOTHESLINE_CHANCE):
            px, py = tiles[i - 1]['wins'][-1]; gx, gy = tiles[i]['wins'][0]
            lines.append(('line', (i - 1) * TILE_W + px + WIN_W, py, i * TILE_W + gx, gy))
    return lines

def build_level(names, rng):
    tiles = [build(n, rng) for n in names]
    return tiles, clotheslines(names, tiles, rng)
