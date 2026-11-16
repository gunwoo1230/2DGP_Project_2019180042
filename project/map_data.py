# 맵 = 타일 이름 순서 목록
import config

TEST_MAP = ['start', 'basic', 'pipe', 'basic', 'accel', 'gap', 'pole', 'basic', 'accel', 'gap', 'basic']
BOSS_ARENA = ['start', 'start', 'start']        # 임시 보스 무대 (빈터)

# 낮 맵 조각: 'climb' = 오르는 곳 (pipe 또는 pole)
# 지킬 것: gap은 accel 바로 다음에만, climb은 accel과 gap 사이에 넣지 않음, 조각마다 climb 1개 이상
EASY = [['basic', 'climb', 'basic'],
        ['basic', 'basic', 'climb', 'basic'],
        ['basic', 'accel', 'basic', 'climb']]
NORMAL = [['basic', 'accel', 'gap', 'climb'],
          ['climb', 'basic', 'accel', 'gap'],
          ['basic', 'climb', 'accel', 'basic', 'basic']]
HARD = [['accel', 'gap', 'accel', 'gap', 'climb'],
        ['basic', 'accel', 'gap', 'basic', 'accel', 'gap', 'climb'],
        ['climb', 'accel', 'gap', 'basic', 'accel', 'basic']]


def make_day_map(rng):
    # 시작 칸 + 건물 60칸: 건물 수에 맞는 난이도의 조각을 랜덤으로 이어 붙임 (바로 앞 조각은 피함)
    names = ['start']
    last = None
    while len(names) - 1 < config.DAY_BUILDINGS:
        built = len(names) - 1
        pool = EASY if built < config.CHUNK_LEVELS[0] else NORMAL if built < config.CHUNK_LEVELS[1] else HARD
        chunk = rng.choice([c for c in pool if c is not last])
        last = chunk
        for name in chunk:
            if len(names) - 1 >= config.DAY_BUILDINGS:
                break       # 60칸이 되면 조각 나머지는 버림
            names.append(rng.choice(config.CLIMB_TILES) if name == 'climb' else name)
    return names
