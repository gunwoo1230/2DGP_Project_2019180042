# 플레이 모드
import random

from pico2d import *

import camera
import config
import day
import game_framework
import game_world
import hazard
from box import Box, Recover
from dummy import Dummy
from guard import Guard
from hazard import LiveWindow, Pigeon, PigeonSpawner, Puddle
from hud import Background, GuardMarker, Hud, Sun
from level import Level
from map_data import BOSS_ARENA, DEMO_SEED, TEST_MAP, make_day_map, make_demo_map, test_chunks
from scenery import Scenery, Sky
from tape import TapeItem

pit_stunned = False     # 데모 맵: 틈 추락으로 기절했는지 (그 뒤 경비원이 빨라짐)

# 디버그: 지금 x에서 이 높이로 옮겨 떨어뜨림
DROP_KEYS = {SDLK_1: config.ROAD_Y, SDLK_2: config.LEDGE_Y, SDLK_3: config.ROOF_Y}


def apply_zone():
    # 진행 상태에 맞는 구간(추격·보스)을 HUD와 박스에 알림
    zone = 'boss' if day.phase == 'boss' else 'chase'
    hud.set_zone(zone)
    box.zone = zone
    sync_dummy(zone)


def sync_dummy(zone):
    # 몸통박치기 시험용 허수아비는 보스 구간에만 (점프맵에는 없음)
    dummies = [o for o in game_world.objects[game_world.LAYER_ITEM] if isinstance(o, Dummy)]
    if zone == 'boss' and not dummies:
        spawn_dummy()
    elif zone != 'boss':
        for dummy in dummies:
            game_world.remove_object(dummy)


def toggle_zone():
    # 디버그 구간 전환 (레벨은 그대로), 낮 끝 중에는 무시
    if day.phase == 'day_end':
        return
    if day.phase == 'boss' and level.names == BOSS_ARENA:
        restart('day')  # 보스 무대에는 추격할 맵이 없으므로 낮 맵 처음부터
        return
    day.phase = 'chase' if day.phase == 'boss' else 'boss'
    apply_zone()


def spawn_tapes():
    # 레벨이 정한 자리마다 (조각당 1개, 보스 무대에는 없음)
    for x, y in level.tapes:
        tape = TapeItem(x, y)
        game_world.add_object(tape, game_world.LAYER_ITEM)
        game_world.add_collision_pair('box:tape', None, tape)


def spawn_hazards():
    # 레벨이 정한 자리에 물웅덩이·살아 있는 창문
    # 비둘기: 데모면 레벨이 정한 지붕마다 미리 앉힘, 아니면 조각이 있는 맵에 비둘기 부르는 것 하나
    for i, spots in enumerate(level.hazards):
        tile, left = level.tiles[i]
        for kind, value in spots:
            if kind == 'window':
                x, y = tile['windows'][value]
                window = LiveWindow(left + x, y, box)
                game_world.add_object(window, game_world.LAYER_ITEM)
                game_world.add_collision_pair('box:window', None, window)
            else:
                puddle = Puddle(left + value)
                game_world.add_object(puddle, game_world.LAYER_ITEM)
                game_world.add_collision_pair('box:puddle', None, puddle)
    if level.layout is not None:
        # 데모 맵: 정해진 칸 지붕에 앉아 있다가, 박스가 그 칸 지붕에 서면 바로 "!" (시간·확률 굴림 없음)
        def ready():
            return box.standing_kind() == 'roof' and level.tile_index(box.x) == level.pigeon_tile
        for x, y in level.pigeons:
            pigeon = Pigeon(x, y, box, None, ready)
            game_world.add_object(pigeon, game_world.LAYER_ITEM)
            game_world.add_collision_pair('box:pigeon', None, pigeon)
    elif config.DEMO_HAZARDS:
        for x, y in level.pigeons:
            pigeon = Pigeon(x, y, box, None)
            game_world.add_object(pigeon, game_world.LAYER_ITEM)
            game_world.add_collision_pair('box:pigeon', None, pigeon)
    elif level.chunks:
        game_world.add_object(PigeonSpawner(box, level), game_world.LAYER_ITEM)


def spawn_dummy():
    dummy = Dummy()
    game_world.add_object(dummy, game_world.LAYER_ITEM)
    game_world.add_collision_pair('box:dummy', None, dummy)


def new_seed():
    # 시험용 고정 시드가 있으면 그 값, 없으면 랜덤
    return config.FIXED_SEED if config.FIXED_SEED is not None else random.randrange(100000)


def new_map(kind, same_seed=False):
    # 맵 종류('day' 낮 맵 / 'test' 시험 맵 / 'demo' 데모 맵)에 맞는 타일 목록·조각 범위와,
    # 이어서 양식·창문·빨랫줄을 정할 난수, 데모 맵의 고정 배치 (Level 인자 순서)
    # 같은 시드면 같은 맵 (버그 재현용), 데모 맵은 항상 DEMO_SEED
    global map_kind, seed
    map_kind = kind
    if kind == 'demo':
        print('demo')
        names, layout = make_demo_map()
        return names, [], random.Random(DEMO_SEED), layout
    if not same_seed:
        seed = new_seed()
    print(f'seed = {seed}')
    rng = random.Random(seed)
    if kind == 'day':
        names, chunks = make_day_map(rng)
    else:
        names, chunks = TEST_MAP, test_chunks(TEST_MAP)
    return names, chunks, rng, None


def restart(kind=None, same_seed=False):
    # 처음부터 (맵 종류는 그대로, 보스 무대에서는 낮 맵·데모 맵): 박스·경비원·생명·테이프·허수아비·점수·해, 구간은 추격
    if kind is None:
        kind = 'day' if level.names == BOSS_ARENA and map_kind != 'demo' else map_kind
    game_world.remove_layer(game_world.LAYER_ITEM)
    game_world.remove_layer(game_world.LAYER_FX)
    level.load(*new_map(kind, same_seed))
    camera.init(level.right)
    spawn_tapes()
    spawn_hazards()
    reset_guard()
    game_world.add_object(guard, game_world.LAYER_ITEM)
    hud.reset_lives()
    box.reset()
    day.reset()
    apply_zone()


def reset_guard():
    # 데모 맵은 화면 밖(모자만 보임)에서 데모 속도로 시작, 추락 기절 전
    global pit_stunned
    pit_stunned = False
    if level.layout is not None:
        guard.reset(config.DEMO_GUARD_HIDE_GAP, config.DEMO_GUARD_SPEED)
    else:
        guard.reset()


def update_demo_guard():
    # 데모 맵 경비원: 틈 추락 기절 전에는 화면 밖에 머묾, 그 기절이 끝나면 빨라짐, 박스를 잡지 않음
    global pit_stunned
    pit = level.layout['pit']
    if not pit_stunned and box.state_machine.cur is Recover and level.tile_index(box.x) in (pit, pit + 1):
        pit_stunned = True
    if pit_stunned and box.state_machine.cur is not Recover:
        guard.speed = config.DEMO_GUARD_SPEED * config.DEMO_GUARD_BOOST
    gap = config.DEMO_GUARD_MIN_GAP if pit_stunned else config.DEMO_GUARD_HIDE_GAP
    guard.x = min(guard.x, box.x - gap)


def to_boss():
    # 낮 끝 -> 보스 구간 (임시 빈터 무대), 생명은 그대로 이어짐
    # 날아가는 중인 테이프 연출은 생명 칸에 들어가야 하므로 FX 레이어는 지우지 않음
    day.phase = 'boss'
    apply_zone()
    level.load(BOSS_ARENA, [], None)     # 빈터는 조각·난수를 쓰지 않음
    camera.init(level.right)
    game_world.remove_layer(game_world.LAYER_ITEM)     # 바닥 테이프·경비원
    spawn_dummy()
    box.reset()


def init():
    global hud, box, level, guard, show_collision_boxes
    show_collision_boxes = False
    day.reset()
    hud = Hud()
    game_world.add_object(Background(), game_world.LAYER_BG)
    game_world.add_object(Sky(), game_world.LAYER_BG)          # 일기장 틀 다음: 그림 칸을 덮음
    game_world.add_object(Sun(), game_world.LAYER_SKY)
    game_world.add_object(Scenery(), game_world.LAYER_SKY)     # 해 다음: 구름·산·동네
    game_world.add_object(hud, game_world.LAYER_UI)
    level = Level(*new_map('day'))
    game_world.add_object(level, game_world.LAYER_MAP)
    box = Box(hud, level)
    game_world.add_object(box, game_world.LAYER_BOX)
    game_world.add_collision_pair('box:tape', box, None)
    game_world.add_collision_pair('box:dummy', box, None)
    game_world.add_collision_pair('box:puddle', box, None)
    game_world.add_collision_pair('box:window', box, None)
    game_world.add_collision_pair('box:pigeon', box, None)
    spawn_tapes()
    spawn_hazards()
    # 경비원은 한 번 만들고 리셋 때 처음 위치로
    guard = Guard()
    game_world.add_object(guard, game_world.LAYER_ITEM)
    game_world.add_object(GuardMarker(guard), game_world.LAYER_UI)    # Hud 다음: 테두리 덮개 위에 그림
    camera.init(level.right)


def finish():
    game_world.clear()


def update():
    game_world.update()
    game_world.handle_collisions()
    camera.follow(box.x)
    day.update(box.x, level)
    update_chase()


def update_chase():
    # 가로 거리만 보고 잡힘 (지붕 위에서도), 잡히면 잠깐 멈춘 뒤 처음부터
    # 낮 끝에는 경비원이 지친 모습을 잠깐 보여 준 뒤 보스 구간으로
    if day.phase == 'chase' and guard.enabled and level.layout is not None:
        update_demo_guard()     # 데모 맵은 잡히지 않음
    elif day.phase == 'chase' and guard.enabled and box.x - guard.x <= config.CATCH_DIST:
        day.phase = 'caught'
        day.timer = 0.0
        box.catch()
    elif day.phase == 'caught':
        day.timer += game_framework.frame_time
        if day.timer >= config.CAUGHT_TIME:
            restart()
    elif day.phase == 'day_end':
        day.timer += game_framework.frame_time
        if day.timer >= config.DAY_END_TIME:
            to_boss()


def warp(x):
    # 디버그: 그 x의 도로로 옮기고, 건너뛴 칸도 점수에 넣고 해도 바로 맞춤
    box.warp(x)
    day.snap(box.x, level)


def draw():
    clear_canvas()
    game_world.draw()
    if show_collision_boxes:
        game_world.draw_collision_boxes()
        level.draw_debug()
    update_canvas()


def handle_events():
    global show_collision_boxes
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            show_collision_boxes = not show_collision_boxes
        elif event.type == SDL_KEYDOWN and event.key == SDLK_r:
            restart()       # 새 시드 (새 맵), 데모 맵이면 데모 맵 처음부터
        elif event.type == SDL_KEYDOWN and event.key == SDLK_d:
            restart('demo')     # 발표 녹화용 데모 맵 처음부터
        elif event.type == SDL_KEYDOWN and event.key == SDLK_t:
            restart(same_seed=True)     # 같은 시드 (같은 맵 다시)
        elif event.type == SDL_KEYDOWN and day.phase == 'caught':
            box.handle_event(event)     # 잡힘 중에는 나머지 디버그 키를 받지 않음
        elif event.type == SDL_KEYDOWN and event.key == SDLK_b:
            toggle_zone()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_n:
            next_left = level.next_tile_left(box.x)
            if next_left is not None:
                warp(next_left)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_e:
            warp(level.tiles[-2][1])    # 마지막 칸 앞 (낮 끝 시험용)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_g:
            guard.enabled = not guard.enabled   # 끄면 멈추고 잡힘·게이지 없음 (맵 시험용)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_h:
            hazard.enabled = not hazard.enabled     # 끄면 감속·창문·비둘기·피격 없음 (맵 시험용)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_m:
            restart('test' if map_kind == 'day' else 'day', same_seed=True)
        elif event.type == SDL_KEYDOWN and event.key in DROP_KEYS:
            box.drop_to(DROP_KEYS[event.key])
        else:
            box.handle_event(event)
