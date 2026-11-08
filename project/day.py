# 낮 진행 상태: 구간, 최고 도달 타일(점수), 해 위치
import math

import config
import game_framework

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
    # 해는 목표 진행률을 향해 초당 SUN_SPEED씩 따라감
    global sun_p
    record(box_x, level)
    diff = progress(level) - sun_p
    move = config.SUN_SPEED * game_framework.frame_time
    sun_p += diff if abs(diff) <= move else math.copysign(move, diff)


def snap(box_x, level):
    # 디버그로 크게 건너뛰었을 때: 점수를 바로 반영하고 해도 바로 맞춤
    global sun_p
    record(box_x, level)
    sun_p = progress(level)


def record(box_x, level):
    # 추격 중에만 점수가 오름, 뒤로 가거나 떨어져도 줄지 않음
    global best_tile
    if phase == 'chase':
        best_tile = max(best_tile, level.tile_index(box_x))


def progress(level):
    # 진행률 = 최고 도달 타일 / 마지막 칸 번호 (0 ~ 1)
    return min(best_tile / (len(level.tiles) - 1), 1)


def minutes():
    # 점수 = 최고 도달 타일 × 10분
    return best_tile * config.MINUTES_PER_TILE
