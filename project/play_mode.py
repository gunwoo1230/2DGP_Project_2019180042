# 플레이 모드
from pico2d import *

import game_framework
import game_world
from hud import Hud


def toggle_zone():
    global zone
    zone = 'boss' if zone == 'chase' else 'chase'
    hud.set_zone(zone)


def init():
    global hud, zone
    zone = 'chase'
    hud = Hud()
    game_world.add_object(hud, game_world.LAYER_HUD)


def finish():
    game_world.clear()


def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.draw()
    update_canvas()


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_b:
            toggle_zone()
