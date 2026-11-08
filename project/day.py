# 낮 진행 상태: 구간, 최고 도달 타일(점수), 해 위치
import config

phase = 'chase'     # 'chase' 추격, 'caught' 잡힘, 'day_end' 경비원 지침, 'boss' 보스 구간
best_tile = 0       # 지금까지 들어간 가장 먼 타일 번호
sun_p = 0.0         # 그리는 해의 진행률 (0 ~ 1)
timer = 0.0         # 잡힘·낮 끝이 이어진 시간


def reset():
    global phase, best_tile, sun_p, timer
    phase = 'chase'
    best_tile = 0
    sun_p = 0.0
    timer = 0.0


def update(box_x, level):
    # 추격 중에만 점수가 오름, 뒤로 가거나 떨어져도 줄지 않음
    global best_tile
    if phase == 'chase':
        best_tile = max(best_tile, level.tile_index(box_x))


def minutes():
    # 점수 = 최고 도달 타일 × 10분
    return best_tile * config.MINUTES_PER_TILE
