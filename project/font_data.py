# 박스야, 도망쳐! — 손글씨 폰트 시트 정보 (pico2d)
# font_sheet.png : Gaegu Bold 손글씨를 미리 그려 둔 이미지 (글자색 연필색, 배경 투명)
# 좌표는 모두 pico2d 기준 (left, bottom, w, h) — 이미지 왼쪽 아래가 (0, 0)
# 글자는 화면 크기 그대로(1배) 그려져 있음 → 배율 없이 그리면 됨

TITLE_RECT = (6, 252, 686, 96)          # '박스야, 도망쳐!' (타이틀 화면용 큰 글씨)

WORD_RECT = {                       # 위쪽 '지금' 칸 낱말 (크기 38, 모두 높이 50·기준선 같음)
    '낮': (6, 196, 40, 50),
    '밤': (52, 196, 40, 50),
    '저녁': (98, 196, 70, 50),
    '주택가': (174, 196, 101, 50),
    '공원': (281, 196, 70, 50),
    'comma': (357, 196, 21, 50),
}

DIGIT_W, DIGIT_H = 28, 44           # 숫자 이미지 칸 크기 (모두 같은 폭 → 자릿수가 바뀌어도 흔들리지 않음)
DIGIT_ADV = 21                      # 숫자 사이 간격
DIGIT_RECT = {
    '0': (6, 146, 28, 44),
    '1': (40, 146, 28, 44),
    '2': (74, 146, 28, 44),
    '3': (108, 146, 28, 44),
    '4': (142, 146, 28, 44),
    '5': (176, 146, 28, 44),
    '6': (210, 146, 28, 44),
    '7': (244, 146, 28, 44),
    '8': (278, 146, 28, 44),
    '9': (312, 146, 28, 44),
}

CELL_W, CELL_H = 64, 64             # 원고지 한 칸 글자 (크기 44, 화살표는 손글씨 느낌으로 직접 그림)
CELL_RECT = {
    '←': (6, 76, 64, 64),
    '→': (76, 76, 64, 64),
    '방': (146, 76, 64, 64),
    '향': (216, 76, 64, 64),
    '키': (286, 76, 64, 64),
    '로': (356, 76, 64, 64),
    '움': (426, 76, 64, 64),
    '직': (496, 76, 64, 64),
    '여': (566, 76, 64, 64),
    '요': (636, 76, 64, 64),
    '스': (706, 76, 64, 64),
    '페': (776, 76, 64, 64),
    '이': (846, 76, 64, 64),
    '뛰': (916, 76, 64, 64),
    '어': (6, 6, 64, 64),
    '쉬': (76, 6, 64, 64),
    '프': (146, 6, 64, 64),
    '트': (216, 6, 64, 64),
    '주': (286, 6, 64, 64),
    '워': (356, 6, 64, 64),
    '공': (426, 6, 64, 64),
    '격': (496, 6, 64, 64),
    '해': (566, 6, 64, 64),
}

# 팁 문장 (원고지 한 칸에 한 글자, 띄어쓰기는 빈 칸)
TIPS = {
    'move': '← → 방향키로 움직여요',
    'jump': '스페이스로 뛰어요',
    'pick': '쉬프트로 주워요',
    'attack': '쉬프트로 공격해요',
}
TIP_LIST = {
    'day':  ['move', 'jump', 'pick'],      # 점프맵 (낮·밤)
    'boss': ['move', 'jump', 'attack'],    # 보스전
}


def _draw(sheet, rect, x, y):
    l, b, w, h = rect
    sheet.clip_draw(l, b, w, h, x, y)


def draw_title(sheet, x, y):
    """(x, y) = 제목 가운데"""
    _draw(sheet, TITLE_RECT, x, y)


def draw_now(sheet, time_word, place_word, x, y, gap=10):
    """'지금' 칸: 예) draw_now(font, '낮', '주택가', 868, 856) → '낮, 주택가' 를 (x, y) 가운데에"""
    # 낱말 이미지는 모두 높이 50, 글자 기준선이 같은 높이 → y만 같게 그리면 줄이 맞음
    parts = [WORD_RECT[time_word], WORD_RECT['comma'], WORD_RECT[place_word]]
    total = sum(r[2] for r in parts) + gap - 8
    cx = x - total / 2
    for i, r in enumerate(parts):
        if i == 1:
            cx -= 8          # 쉼표는 앞 낱말에 붙여 씀
        if i == 2:
            cx += gap
        _draw(sheet, r, cx + r[2] / 2, y)
        cx += r[2]


def draw_number(sheet, n, x, y):
    """숫자 n 을 (x, y) 가운데에 (예: 도망친 지 칸의 일·시간·분)"""
    s = str(int(n))
    cx = x - DIGIT_ADV * (len(s) - 1) / 2
    for ch in s:
        _draw(sheet, DIGIT_RECT[ch], cx, y)
        cx += DIGIT_ADV


def draw_tip(sheet, text, first_x, y, cell_w=65, count=None):
    """원고지 한 줄: text 를 한 칸에 한 글자씩. count = 지금까지 써진 글자 수(써지는 효과), None 이면 전부"""
    for i, ch in enumerate(text):
        if count is not None and i >= count:
            break
        if ch != ' ' and ch in CELL_RECT:
            _draw(sheet, CELL_RECT[ch], first_x + i * cell_w, y)
