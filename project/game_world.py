# 게임 월드: 레이어별 객체 목록과 충돌 처리
from pico2d import draw_rectangle

# 그리기 레이어 (아래부터)
LAYER_HUD, LAYER_GROUND, LAYER_ITEM, LAYER_BOX, LAYER_FX = range(5)

objects = [[] for _ in range(5)]
collision_pairs = {}    # 그룹 이름: (a 목록, b 목록)


def add_object(obj, layer):
    objects[layer].append(obj)


def remove_object(obj):
    for layer in objects:
        if obj in layer:
            layer.remove(obj)
            remove_from_collisions(obj)
            return
    raise ValueError('게임 월드에 없는 객체입니다')


def remove_layer(layer):
    for obj in objects[layer][:]:
        remove_object(obj)


def remove_from_collisions(obj):
    for pair in collision_pairs.values():
        for group in pair:
            if obj in group:
                group.remove(obj)


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
    collision_pairs.clear()


def add_collision_pair(group, a, b):
    # a 또는 b만 넘겨 그룹의 한쪽 목록에 추가할 수 있음
    pair = collision_pairs.setdefault(group, ([], []))
    if a:
        pair[0].append(a)
    if b:
        pair[1].append(b)


def draw_collision_boxes():
    # 충돌 쌍에 등록된 객체의 충돌 박스를 그림
    drawn = []
    for pair in collision_pairs.values():
        for group in pair:
            for obj in group:
                if obj not in drawn:
                    draw_rectangle(*obj.get_bb())
                    drawn.append(obj)


def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()
    if right_a < left_b or left_a > right_b:
        return False
    if top_a < bottom_b or bottom_a > top_b:
        return False
    return True


def handle_collisions():
    for group, (group_a, group_b) in collision_pairs.items():
        for a in group_a[:]:
            for b in group_b[:]:
                if collide(a, b):
                    a.handle_collision(group, b)
                    b.handle_collision(group, a)
