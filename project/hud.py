# 그림일기 화면: 배경, 지금·도망친 지, 원고지 팁, 테이프 생명 칸


class Hud:
    def __init__(self):
        pass

    def update(self):
        pass

    def draw(self):
        self.draw_now()
        self.draw_time()
        self.draw_tip()
        self.draw_lives()

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass

    def set_zone(self, zone):
        pass

    def add_life(self):
        pass

    def is_full(self):
        pass

    def draw_now(self):
        pass

    def draw_time(self):
        pass

    def draw_tip(self):
        pass

    def draw_lives(self):
        pass
