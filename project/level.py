# 레벨: 타일 목록으로 발판과 그릴 것을 만듦
import camera
import config
from tiles import draw_tile, load_images


class Level:
    def __init__(self, tile_names):
        load_images()
        # (타일 이름, 왼쪽 끝 월드 x)
        self.tiles = [(name, config.MAP_LEFT + config.TILE_W * i) for i, name in enumerate(tile_names)]
        self.right = config.MAP_LEFT + config.TILE_W * len(tile_names)

    def update(self):
        pass

    def draw(self):
        for name, left in self.tiles:
            # 타일 양쪽 끝이 모두 화면 밖이면 건너뜀
            if camera.to_screen(left + config.TILE_W) >= -config.DRAW_MARGIN \
                    and camera.to_screen(left) <= config.SCREEN_W + config.DRAW_MARGIN:
                draw_tile(name, left)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
