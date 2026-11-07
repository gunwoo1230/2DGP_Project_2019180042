# 플레이 모드
from pico2d import *

import game_framework


def init():
    pass


def finish():
    pass


def update():
    pass


def draw():
    clear_canvas()
    update_canvas()


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
