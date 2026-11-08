# 구르박스 스프라이트 시트 정보 (pico2d)
# 좌표는 모두 pico2d 기준: 이미지 왼쪽 아래가 (0, 0)
# 시트는 크게(2배 기준) 그려져 있음 -> 게임에서는 SCALE=0.6으로 그림 (박스 약 107 x 81)

import math

from config import SPRITE_SCALE

SCALE = SPRITE_SCALE

# ---------- box_sheet.png (940 x 1224) ----------
# 한 행 = 한 애니메이션, 한 칸 = 235 x 204, 모든 칸의 기준점이 같은 자리
BOX_W, BOX_H = 235, 204
BOX_ANCHOR = (111, 29)      # 칸 왼쪽 아래에서 잰 '박스 바닥 가운데' 위치
BOX_ANIM = {                # 이름: (행의 bottom, 프레임 수)
    'idle':    (1020, 3),
    'hit':     (816, 1),
    'jump':    (612, 4),    # 걷기는 1~4 반복, 점프는 1~2 상승, 3~4 정점, 하강은 4 유지
    'fall':    (408, 4),
    'recover': (204, 3),
    'get':     (0, 3),      # 정면
}
BOX_TEMP_POSE = {           # 진짜 그림이 오면 BOX_ANIM에 행을 추가하고 여기서 삭제
    'charge': ('idle', 0),  # 기모으기
    'slam':   ('jump', 0),  # 몸통박치기
}

# ---------- item_sheet.png (468 x 421) ----------
# 프레임별 (left, bottom, w, h)
ITEM_RECT = {
    'sparkle': [(0, 228, 234, 193), (234, 228, 234, 193)],   # 테이프 획득 반짝이 (2장 번갈아)
    'dizzy':   [(0, 112, 194, 116), (194, 112, 194, 116)],   # 회복 중 도는 별 (2장 번갈아)
    'tape':    [(0, 0, 130, 112)],                           # 맵 아이템
    'tape_ui': [(130, 71, 48, 41)],                          # 생명 칸
}


def draw_box(sheet, anim, frame, x, y, flip=False, scale=SCALE, sx=1, sy=1, rot=0):
    """(x, y) = 박스 바닥 가운데. 발 위치에 맞춰 그리면 됨. flip=True면 왼쪽을 봄.
    sx, sy = 가로·세로 배율, rot = 회전(rad, 양수가 반시계). 기준점은 움직이지 않음."""
    if anim in BOX_TEMP_POSE:       # 그림이 아직 없는 동작
        anim, frame = BOX_TEMP_POSE[anim]
    bottom, n = BOX_ANIM[anim]
    left = (int(frame) % n) * BOX_W
    w, h = BOX_W * scale * sx, BOX_H * scale * sy
    ax, ay = BOX_ANCHOR
    # 그림은 가운데를 중심으로 회전하므로, 기준점에서 가운데까지의 거리도 함께 돌림
    dx = (BOX_W / 2 - ax) * scale * sx * (-1 if flip else 1)
    dy = (BOX_H / 2 - ay) * scale * sy
    cx = x + dx * math.cos(rot) - dy * math.sin(rot)
    cy = y + dx * math.sin(rot) + dy * math.cos(rot)
    if flip or rot:
        sheet.clip_composite_draw(left, bottom, BOX_W, BOX_H, rot, 'h' if flip else '', cx, cy, w, h)
    else:
        sheet.clip_draw(left, bottom, BOX_W, BOX_H, cx, cy, w, h)


def draw_item(sheet, name, frame, x, y, scale=SCALE):
    """(x, y) = 그림의 가운데."""
    rects = ITEM_RECT[name]
    l, b, w, h = rects[int(frame) % len(rects)]
    sheet.clip_draw(l, b, w, h, x, y, w * scale, h * scale)
