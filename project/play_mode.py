# 플레이 모드
import random

from pico2d import *

import camera
import config
import day
import game_framework
import game_world
from box import Box
from dummy import Dummy
from guard import Guard
from hud import Background, GuardMarker, Hud, Sun
from level import Level
from map_data import BOSS_ARENA, TEST_MAP, make_day_map
from tape import TapeItem

# 디버그: 지금 x에서 이 높이로 옮겨 떨어뜨림
DROP_KEYS = {SDLK_1: config.ROAD_Y, SDLK_2: config.LEDGE_Y, SDLK_3: config.ROOF_Y}


def apply_zone():
    # 진행 상태에 맞는 구간(추격·보스)을 HUD와 박스에 알림
    zone = 'boss' if day.phase == 'boss' else 'chase'
    hud.set_zone(zone)
    box.zone = zone


def toggle_zone():
    # 디버그 구간 전환 (레벨은 그대로), 낮 끝 중에는 무시
    if day.phase == 'day_end':
        return
    if day.phase == 'boss' and level.names == BOSS_ARENA:
        restart('day')  # 보스 무대에는 추격할 맵이 없으므로 낮 맵 처음부터
        return
    day.phase = 'chase' if day.phase == 'boss' else 'boss'
    apply_zone()


def spawn_tapes():
    for x in config.TAPE_XS:
        tape = TapeItem(x)
        game_world.add_object(tape, game_world.LAYER_ITEM)
        game_world.add_collision_pair('box:tape', None, tape)


def spawn_dummy():
    dummy = Dummy()
    game_world.add_object(dummy, game_world.LAYER_ITEM)
    game_world.add_collision_pair('box:dummy', None, dummy)


def new_seed():
    # 시험용 고정 시드가 있으면 그 값, 없으면 랜덤
    return config.FIXED_SEED if config.FIXED_SEED is not None else random.randrange(100000)


def new_map(kind, same_seed=False):
    # 맵 종류('day' 낮 맵 / 'test' 시험 맵)에 맞는 타일 목록과, 이어서 양식·창문·빨랫줄을 정할 난수
    # 같은 시드면 같은 맵 (버그 재현용)
    global map_kind, seed
    map_kind = kind
    if not same_seed:
        seed = new_seed()
    print(f'seed = {seed}')
    rng = random.Random(seed)
    names = make_day_map(rng) if kind == 'day' else TEST_MAP
    return names, rng


def restart(kind=None, same_seed=False):
    # 처음부터 (맵 종류는 그대로, 보스 무대에서는 낮 맵): 박스·경비원·생명·테이프 3개·허수아비·점수·해, 구간은 추격
    if kind is None:
        kind = 'day' if level.names == BOSS_ARENA else map_kind
    game_world.remove_layer(game_world.LAYER_ITEM)
    game_world.remove_layer(game_world.LAYER_FX)
    level.load(*new_map(kind, same_seed))
    camera.init(level.right)
    spawn_tapes()
    spawn_dummy()
    guard.reset()
    game_world.add_object(guard, game_world.LAYER_ITEM)
    hud.reset_lives()
    box.reset()
    day.reset()
    apply_zone()


def to_boss():
    # 낮 끝 -> 보스 구간 (임시 빈터 무대), 생명은 그대로 이어짐
    # 날아가는 중인 테이프 연출은 생명 칸에 들어가야 하므로 FX 레이어는 지우지 않음
    day.phase = 'boss'
    apply_zone()
    level.load(BOSS_ARENA, None)     # 빈터는 난수를 쓰지 않음
    camera.init(level.right)
    game_world.remove_layer(game_world.LAYER_ITEM)     # 바닥 테이프·경비원
    spawn_dummy()
    box.reset()


def init():
    global hud, box, level, guard, show_collision_boxes
    show_collision_boxes = False
    day.reset()
    hud = Hud()
    game_world.add_object(Background(), game_world.LAYER_BG)
    game_world.add_object(Sun(), game_world.LAYER_SKY)
    game_world.add_object(hud, game_world.LAYER_UI)
    level = Level(*new_map('day'))
    game_world.add_object(level, game_world.LAYER_MAP)
    box = Box(hud, level)
    game_world.add_object(box, game_world.LAYER_BOX)
    game_world.add_collision_pair('box:tape', box, None)
    game_world.add_collision_pair('box:dummy', box, None)
    spawn_tapes()
    spawn_dummy()
    # 경비원은 한 번 만들고 리셋 때 처음 위치로
    guard = Guard()
    game_world.add_object(guard, game_world.LAYER_ITEM)
    game_world.add_object(GuardMarker(guard), game_world.LAYER_UI)    # Hud 다음: 테두리 덮개 위에 그림
    camera.init(level.right)


def finish():
    game_world.clear()


def update():
    game_world.update()
    game_world.handle_collisions()
    camera.follow(box.x)
    day.update(box.x, level)
    update_chase()


def update_chase():
    # 가로 거리만 보고 잡힘 (지붕 위에서도), 잡히면 잠깐 멈춘 뒤 처음부터
    # 낮 끝에는 경비원이 지친 모습을 잠깐 보여 준 뒤 보스 구간으로
    if day.phase == 'chase' and guard.enabled and box.x - guard.x <= config.CATCH_DIST:
        day.phase = 'caught'
        day.timer = 0.0
        box.catch()
    elif day.phase == 'caught':
        day.timer += game_framework.frame_time
        if day.timer >= config.CAUGHT_TIME:
            restart()
    elif day.phase == 'day_end':
        day.timer += game_framework.frame_time
        if day.timer >= config.DAY_END_TIME:
            to_boss()


def warp(x):
    # 디버그: 그 x의 도로로 옮기고, 건너뛴 칸도 점수에 넣고 해도 바로 맞춤
    box.warp(x)
    day.snap(box.x, level)


def draw():
    clear_canvas()
    game_world.draw()
    if show_collision_boxes:
        game_world.draw_collision_boxes()
        level.draw_debug()
    update_canvas()


def handle_events():
    global show_collision_boxes
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            show_collision_boxes = not show_collision_boxes
        elif event.type == SDL_KEYDOWN and event.key == SDLK_r:
            restart()       # 새 시드 (새 맵)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_t:
            restart(same_seed=True)     # 같은 시드 (같은 맵 다시)
        elif event.type == SDL_KEYDOWN and day.phase == 'caught':
            box.handle_event(event)     # 잡힘 중에는 나머지 디버그 키를 받지 않음
        elif event.type == SDL_KEYDOWN and event.key == SDLK_b:
            toggle_zone()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_n:
            next_left = level.next_tile_left(box.x)
            if next_left is not None:
                warp(next_left)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_e:
            warp(level.tiles[-2][1])    # 마지막 칸 앞 (낮 끝 시험용)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_g:
            guard.enabled = not guard.enabled   # 끄면 멈추고 잡힘·게이지 없음 (맵 시험용)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_m:
            restart('test' if map_kind == 'day' else 'day', same_seed=True)
        elif event.type == SDL_KEYDOWN and event.key in DROP_KEYS:
            box.drop_to(DROP_KEYS[event.key])
        else:
            box.handle_event(event)
