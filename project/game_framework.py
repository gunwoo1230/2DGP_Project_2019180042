# 게임 루프와 모드 관리
import time

frame_time = 0.0    # 지난 프레임에 걸린 시간(초)
running = False
stack = []          # 모드 스택, 맨 위 모드가 실행됨


def run(start_mode):
    global running, frame_time
    running = True
    stack.append(start_mode)
    start_mode.init()

    # 시간 측정은 init(리소스 로드) 다음부터
    current_time = time.perf_counter()
    while running:
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()
        now = time.perf_counter()
        frame_time = now - current_time
        current_time = now

    while stack:
        stack.pop().finish()


def quit():
    global running
    running = False


def change_mode(mode):
    if stack:
        stack.pop().finish()
    stack.append(mode)
    mode.init()


def push_mode(mode):
    stack.append(mode)
    mode.init()


def pop_mode():
    # 마지막 모드를 꺼내면 실행할 모드가 없으므로 종료 (정리는 run이 함)
    if len(stack) > 1:
        stack.pop().finish()
    else:
        quit()
