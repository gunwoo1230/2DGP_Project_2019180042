# 건물 타일: 타일 정의, 발판, 타일 그리기

TILES = {
    'start': {'walls': [], 'deco': [], 'platforms': []},
}


class Platform:
    def __init__(self, kind, x0, y0, x1, y1):
        pass

    def surface_y(self, x):
        pass

    def covers(self, x):
        pass


def draw_tile(name, left):
    pass
