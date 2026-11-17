# 맵 = 타일 이름 순서 목록
import config

TEST_MAP = ['start', 'basic', 'pipe', 'basic', 'accel', 'gap', 'pole', 'basic', 'accel', 'gap', 'basic']
BOSS_ARENA = ['start', 'start', 'start']        # 임시 보스 무대 (빈터)

# 발표 녹화용 데모 맵 (D 키): 항상 같은 맵·같은 배치, 대본 순서
# 도로 달리기 → 웅덩이 걸림 → 배수관 → 창틀 테이프 → 창문 열림 피하기 → 빨랫줄 가속 → 전봇대 → 가속 지붕 → 틈 건너기
# → 비둘기 피하기 → 틈으로 추락·기절 → 모자 커짐·깜빡 → 경비원 등장 → 해 끝 → 공원 → 허수아비 몸통박치기
# 건물 양식·창문 위치만 DEMO_SEED로 정하고, 빨랫줄·방해 요소·테이프·비둘기는 DEMO_LAYOUT만 씀
# 앞쪽 소개 구간(start + basic)은 config.DEMO_INTRO_TILES칸, 아래 칸 번호는 소개 구간이 2칸일 때 기준 (늘리면 자동으로 밀림)
DEMO_BODY = ['basic', 'pipe', 'basic', 'basic', 'basic', 'pole', 'accel', 'gap', 'basic', 'gap', 'basic']   # 2번 칸부터
DEMO_SEED = 70                  # 배수관 받침 -> 3·4·5·6번 창틀 -> 전봇대 못을 점프로 이어 갈 수 있는 창문 배치 (창틀 사이 최대 137px)
DEMO_LAYOUT = {
    'tapes': [],                    # 지붕 가운데 테이프 (칸)
    'ledge_tapes': [(4, 1)],        # 창틀 가운데 테이프 (칸, 창문 번호)
    'lines': [(5, 6)],              # 원래 규칙(gap 앞) 말고 더 거는 빨랫줄 (앞 칸 마지막 창틀 -> 다음 칸 첫 창틀)
    'no_lines': [(10, 11)],         # gap 앞이어도 걸지 않는 빨랫줄 (가속 없이 못 건너 떨어지는 틈)
    'windows': [(5, 0)],            # 살아 있는 창문 (칸, 창문 번호)
    'puddles': [(2, 260)],          # 물웅덩이 (칸, 왼쪽 끝 타일 안 x): 걸려서 느려짐
    'pigeon': 10,                   # 박스가 이 칸 지붕에 처음 서면 바로 비둘기 "!" (시간·확률 굴림 없이)
    'pigeon_seat': (11, 300),       # 비둘기가 앉아 있는 곳 (칸, 지붕 위 타일 안 x)
    'pit': 10,                      # 이 칸과 다음 칸 사이 틈으로 떨어져 기절 (그 기절이 끝나면 경비원이 빨라짐)
}


def make_demo_map():
    # 소개 구간 칸 수(DEMO_INTRO_TILES)에 맞춘 데모 맵 타일 목록과 배치 (칸 번호를 그만큼 밈)
    shift = config.DEMO_INTRO_TILES - 2
    names = ['start'] + ['basic'] * (config.DEMO_INTRO_TILES - 1) + DEMO_BODY
    layout = {
        'tapes': [i + shift for i in DEMO_LAYOUT['tapes']],
        'ledge_tapes': [(i + shift, j) for i, j in DEMO_LAYOUT['ledge_tapes']],
        'lines': [(a + shift, b + shift) for a, b in DEMO_LAYOUT['lines']],
        'no_lines': [(a + shift, b + shift) for a, b in DEMO_LAYOUT['no_lines']],
        'windows': [(i + shift, j) for i, j in DEMO_LAYOUT['windows']],
        'puddles': [(i + shift, x) for i, x in DEMO_LAYOUT['puddles']],
        'pigeon': DEMO_LAYOUT['pigeon'] + shift,
        'pigeon_seat': (DEMO_LAYOUT['pigeon_seat'][0] + shift, DEMO_LAYOUT['pigeon_seat'][1]),
        'pit': DEMO_LAYOUT['pit'] + shift,
        'extra_intro': list(range(2, 2 + shift)),   # 더 붙인 소개 칸: 본편 창문 배치가 바뀌지 않게 따로 만듦
    }
    return names, layout


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


def difficulty(built):
    # 앞까지의 건물 수로 난이도 구간 (0 쉬움, 1 보통, 2 어려움)
    return 0 if built < config.CHUNK_LEVELS[0] else 1 if built < config.CHUNK_LEVELS[1] else 2


def make_day_map(rng):
    # 시작 칸 + 건물 60칸: 건물 수에 맞는 난이도의 조각을 랜덤으로 이어 붙임 (바로 앞 조각은 피함)
    # 타일 이름 목록과 조각 범위 목록 [(첫 타일 번호, 마지막 타일 번호)]을 돌려줌
    names = ['start']
    chunks = []
    last = None
    while len(names) - 1 < config.DAY_BUILDINGS:
        pool = (EASY, NORMAL, HARD)[difficulty(len(names) - 1)]
        chunk = rng.choice([c for c in pool if c is not last])
        last = chunk
        first = len(names)
        for name in chunk:
            if len(names) - 1 >= config.DAY_BUILDINGS:
                break       # 60칸이 되면 조각 나머지는 버림
            names.append(rng.choice(config.CLIMB_TILES) if name == 'climb' else name)
        chunks.append((first, len(names) - 1))     # 60칸 끝에서 잘린 조각은 잘린 데까지
    return names, chunks


def test_chunks(names, size=3):
    # 조각이 없는 맵(TEST_MAP)은 1번 타일부터 size칸씩 묶어 조각으로 침
    return [(i, min(i + size - 1, len(names) - 1)) for i in range(1, len(names), size)]
