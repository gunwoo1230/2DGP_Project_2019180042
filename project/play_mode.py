# 플레이 모드
from pico2d import *

import config
import game_framework
import game_world
from box import Box
from dummy import Dummy
from ground import Ground
from hud import Hud
from tape import TapeItem


def toggle_zone():
    global zone
    zone = 'boss' if zone == 'chase' else 'chase'
    hud.set_zone(zone)
    box.zone = zone


def init():
    global hud, zone, box, show_collision_boxes
    show_collision_boxes = False
    zone = 'chase'
    hud = Hud()
    game_world.add_object(hud, game_world.LAYER_HUD)
    game_world.add_object(Ground(), game_world.LAYER_GROUND)
    box = Box(hud)
    game_world.add_object(box, game_world.LAYER_BOX)
    game_world.add_collision_pair('box:tape', box, None)
    game_world.add_collision_pair('box:dummy', box, None)
    for x in config.TAPE_XS:
        tape = TapeItem(x)
        game_world.add_object(tape, game_world.LAYER_ITEM)
        game_world.add_collision_pair('box:tape', None, tape)
    dummy = Dummy()
    game_world.add_object(dummy, game_world.LAYER_ITEM)
    game_world.add_collision_pair('box:dummy', None, dummy)


def finish():
    game_world.clear()


def update():
    game_world.update()
    game_world.handle_collisions()


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
        else:
            box.handle_event(event)
