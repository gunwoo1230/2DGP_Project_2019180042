# 방해 요소: 물웅덩이(도로), 살아 있는 창문(창틀), 비둘기(지붕)
enabled = True      # 디버그 H로 끄면 감속·창문 열림·비둘기·피격이 모두 없음


class Puddle:
    # 도로 물웅덩이: 밟는 동안과 나온 뒤 잠깐 느려짐
    def __init__(self, x):
        self.x = x      # 왼쪽 끝 월드 x

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class LiveWindow:
    # 살아 있는 창문: 처음부터 불이 켜져 있고, 그 창틀에 박스가 서면 덜컹 -> 열림
    def __init__(self, x, y, box):
        self.x, self.y = x, y   # 창틀 왼쪽 끝 월드 x, 창틀 높이
        self.box = box

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class PigeonSpawner:
    # 박스가 평평한 지붕에 있는 시간이 쌓이면 확률로 비둘기를 부름 (한 번에 하나)
    def __init__(self, box, level):
        self.box = box
        self.level = level

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass


class Pigeon:
    # 박스 앞 지붕에 앉아 "!" -> 왼쪽으로 낮게 돌진
    def __init__(self, x, perched, spawner):
        self.x = x
        self.perched = perched      # 앉은 자리 아래에 지붕이 있는지 (없으면 떠 있음, 진짜 그림에서 씀)
        self.spawner = spawner

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
