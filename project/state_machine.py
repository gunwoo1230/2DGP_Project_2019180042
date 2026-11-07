# 이벤트 기반 상태 머신
# 규칙 형식: {상태: [(조건 함수, 다음 상태), ...]}
# 이벤트 형식: ('KEY', sdl_event), ('DONE', None)


class StateMachine:
    def __init__(self, owner, start, rules):
        pass

    def update(self):
        pass

    def draw(self):
        pass

    def handle_event(self, event):
        pass
