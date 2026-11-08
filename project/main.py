from pico2d import open_canvas, close_canvas

import config
import game_framework
import play_mode

open_canvas(config.SCREEN_W, config.SCREEN_H)
game_framework.run(play_mode)
close_canvas()
