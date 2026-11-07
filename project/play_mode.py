# 플레이 모드
from pico2d import *

import camera
import config
import game_framework
import game_world
from box import Box
from dummy import Dummy
from ground import Ground
from hud import Background, Hud
from tape import TapeItem


def toggle_zone():
    global zone
    zone = 'boss' if zone == 'chase' else 'chase'
    hud.set_zone(zone)
    box.zone = zone


def spawn_items():
    for x in config.TAPE_XS:
        tape = TapeItem(x)
        game_world.add_object(tape, game_world.LAYER_ITEM)
        game_world.add_collision_pair('box:tape', None, tape)
    dummy = Dummy()
    game_world.add_object(dummy, game_world.LAYER_ITEM)
    game_world.add_collision_pair('box:dummy', None, dummy)


def reset():
    # 박스 위치·생명·테이프 3개·허수아비 횟수를 처음으로 (구간은 유지)
    game_world.remove_layer(game_world.LAYER_ITEM)
    game_world.remove_layer(game_world.LAYER_FX)
    spawn_items()
    hud.reset_lives()
    box.reset()
    camera.reset()


def init():
    global hud, zone, box, show_collision_boxes
    show_collision_boxes = False
    zone = 'chase'
    hud = Hud()
    game_world.add_object(Background(), game_world.LAYER_BG)
    game_world.add_object(hud, game_world.LAYER_UI)
    game_world.add_object(Ground(), game_world.LAYER_MAP)
    box = Box(hud)
    game_world.add_object(box, game_world.LAYER_BOX)
    game_world.add_collision_pair('box:tape', box, None)
    game_world.add_collision_pair('box:dummy', box, None)
    spawn_items()
    camera.init(config.MAP_LEFT + config.TILE_W * 11)   # 임시: 레벨이 생기면 레벨 끝으로 교체


def finish():
    game_world.clear()


def update():
    game_world.update()
    game_world.handle_collisions()
    camera.follow(box.x)


def draw():
    clear_canvas()
    game_world.draw()
    if show_collision_boxes:
        game_world.draw_collision_boxes()
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
        else:
            box.handle_event(event)
