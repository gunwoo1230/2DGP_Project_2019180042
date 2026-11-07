# 플레이어 박스


class Idle:
    @staticmethod
    def enter(box, event):
        pass

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        pass

    @staticmethod
    def draw(box):
        pass


class Walk:
    @staticmethod
    def enter(box, event):
        pass

    @staticmethod
    def exit(box, event):
        pass

    @staticmethod
    def do(box):
        pass

    @staticmethod
    def draw(box):
        pass


class Box:
    def __init__(self):
        self.on_accel_ground = False    # 가속 지형 위 여부 (1주차엔 항상 False)

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        pass
