# 확인용: python project/test_sheet.py  (저장소 루트에서 실행)
from pico2d import *
from sprite_data import *
open_canvas(800, 400)
box = load_image('resource/box_sheet.png'); item = load_image('resource/item_sheet.png')
names = list(BOX_ANIM); t = 0.0
running = True
while running:
    for e in get_events():
        if e.type in (SDL_QUIT,) or (e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE): running = False
    clear_canvas()
    for i, a in enumerate(names):
        draw_box(box, a, t * 8, 70 + i * 130, 220)
    draw_item(item, 'dizzy', t * 6, 70 + 4 * 130 + 4, 220 + 90)
    draw_item(item, 'sparkle', t * 6, 120, 90); draw_item(item, 'tape', 0, 120, 90)
    draw_item(item, 'tape_ui', 0, 300, 90)
    update_canvas(); delay(0.016); t += 0.016
close_canvas()
