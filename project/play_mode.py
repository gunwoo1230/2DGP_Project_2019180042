# 플레이 모드
from pico2d import *

import camera
import config
import day
import game_framework
import game_world
from box import Box
from dummy import Dummy
from guard import Guard
from hud import Background, Gauge, Hud, Sun
from level import Level
from map_data import BOSS_ARENA, DAY_MAP, TEST_MAP
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
        restart()   # 보스 무대에는 추격할 맵이 없으므로 낮 맵 처음부터
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


def restart(tile_names=DAY_MAP):
    # 처음부터 (보통 낮 맵): 박스·경비원·생명·테이프 3개·허수아비·점수·해, 구간은 추격
    game_world.remove_layer(game_world.LAYER_ITEM)
    game_world.remove_layer(game_world.LAYER_FX)
    if level.names != tile_names:
        level.load(tile_names)
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
    level.load(BOSS_ARENA)
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
    level = Level(DAY_MAP)
    game_world.add_object(level, game_world.LAYER_MAP)
    box = Box(hud, level)
    game_world.add_object(box, game_world.LAYER_BOX)
    game_world.add_collision_pair('box:tape', box, None)
    game_world.add_collision_pair('box:dummy', box, None)
    spawn_tapes()
    spawn_dummy()
    # 경비원은 한 번 만들고 리셋 때 처음 위치로 (거리 게이지가 계속 참조)
    guard = Guard()
    game_world.add_object(guard, game_world.LAYER_ITEM)
    game_world.add_object(Gauge(box, guard), game_world.LAYER_UI)
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
            restart()
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
            restart(TEST_MAP if level.names == DAY_MAP else DAY_MAP)
        elif event.type == SDL_KEYDOWN and event.key in DROP_KEYS:
            box.drop_to(DROP_KEYS[event.key])
        else:
            box.handle_event(event)
