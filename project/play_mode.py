# 플레이 모드
from pico2d import *

import camera
import config
import day
import game_framework
import game_world
from box import Box
from dummy import Dummy
from hud import Background, Hud
from level import Level
from map_data import DAY_MAP
from tape import TapeItem

# 디버그: 지금 x에서 이 높이로 옮겨 떨어뜨림
DROP_KEYS = {SDLK_1: config.ROAD_Y, SDLK_2: config.LEDGE_Y, SDLK_3: config.ROOF_Y}


def apply_zone():
    # 진행 상태에 맞는 구간(추격·보스)을 HUD와 박스에 알림
    zone = 'boss' if day.phase == 'boss' else 'chase'
    hud.set_zone(zone)
    box.zone = zone


def toggle_zone():
    day.phase = 'chase' if day.phase == 'boss' else 'boss'
    apply_zone()


def spawn_items():
    for x in config.TAPE_XS:
        tape = TapeItem(x)
        game_world.add_object(tape, game_world.LAYER_ITEM)
        game_world.add_collision_pair('box:tape', None, tape)
    dummy = Dummy()
    game_world.add_object(dummy, game_world.LAYER_ITEM)
    game_world.add_collision_pair('box:dummy', None, dummy)


def reset():
    # 박스 위치·생명·테이프 3개·허수아비 횟수·점수를 처음으로, 구간은 추격
    game_world.remove_layer(game_world.LAYER_ITEM)
    game_world.remove_layer(game_world.LAYER_FX)
    spawn_items()
    hud.reset_lives()
    box.reset()
    camera.reset()
    day.reset()
    apply_zone()


def init():
    global hud, box, level, show_collision_boxes
    show_collision_boxes = False
    day.reset()
    hud = Hud()
    game_world.add_object(Background(), game_world.LAYER_BG)
    game_world.add_object(hud, game_world.LAYER_UI)
    level = Level(DAY_MAP)
    game_world.add_object(level, game_world.LAYER_MAP)
    box = Box(hud, level)
    game_world.add_object(box, game_world.LAYER_BOX)
    game_world.add_collision_pair('box:tape', box, None)
    game_world.add_collision_pair('box:dummy', box, None)
    spawn_items()
    camera.init(level.right)


def finish():
    game_world.clear()


def update():
    game_world.update()
    game_world.handle_collisions()
    camera.follow(box.x)
    day.update(box.x, level)


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
        elif event.type == SDL_KEYDOWN and event.key == SDLK_b:
            toggle_zone()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            show_collision_boxes = not show_collision_boxes
        elif event.type == SDL_KEYDOWN and event.key == SDLK_r:
            reset()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_n:
            next_left = level.next_tile_left(box.x)
            if next_left is not None:
                box.warp(next_left)
        elif event.type == SDL_KEYDOWN and event.key in DROP_KEYS:
            box.drop_to(DROP_KEYS[event.key])
        else:
            box.handle_event(event)
