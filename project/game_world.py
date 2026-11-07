# 게임 월드: 레이어별 객체 목록과 충돌 처리

# 그리기 레이어 (아래부터)
LAYER_HUD, LAYER_GROUND, LAYER_ITEM, LAYER_BOX, LAYER_FX = range(5)

objects = [[] for _ in range(5)]


def add_object(obj, layer):
    objects[layer].append(obj)


def remove_object(obj):
    for layer in objects:
        if obj in layer:
            layer.remove(obj)
            return
    raise ValueError('게임 월드에 없는 객체입니다')


def update():
    # update 중에 객체가 자신을 지워도 되도록 복사본으로 순회
    for layer in objects:
        for obj in layer[:]:
            obj.update()


def draw():
    for layer in objects:
        for obj in layer:
            obj.draw()


def clear():
    for layer in objects:
        layer.clear()


def add_collision_pair(group, a, b):
    pass


def handle_collisions():
    pass
