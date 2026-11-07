# 확인용: python project/test_font.py  (저장소 루트에서 실행)
from pico2d import *
from font_data import *
open_canvas(1600, 900)
frame = load_image('resource/diary_frame.png')
font = load_image('resource/font_sheet.png')
t = 0.0; tip_i = 0; tip_t = 0.0
tips = TIP_LIST['day']
running = True
while running:
    for e in get_events():
        if e.type == SDL_QUIT or (e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE): running = False
    clear_canvas()
    frame.draw(800, 450)
    draw_now(font, '낮', '주택가', 868, 856)
    minutes = int(t * 30)                       # 확인용: 1초에 30분씩
    draw_number(font, minutes // 1440, 1218, 856)
    draw_number(font, minutes // 60 % 24, 1328, 856)
    draw_number(font, minutes % 60, 1474, 856)
    draw_title(font, 800, 450)
    text = TIPS[tips[tip_i]]
    draw_tip(font, text, 52.5, 54, count=int(tip_t / 0.05))   # 한 글자씩 써지는 효과
    update_canvas(); delay(0.016); t += 0.016; tip_t += 0.016
    if tip_t > 6: tip_t = 0; tip_i = (tip_i + 1) % len(tips)
close_canvas()
