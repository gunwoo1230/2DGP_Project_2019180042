# 이벤트 기반 상태 머신
# 규칙 형식: {상태: [(조건 함수, 다음 상태), ...]}, 조건 함수는 check(owner, event)
# 이벤트 형식: ('KEY', sdl_event), ('DONE', None), ('AIR', None)


class StateMachine:
    def __init__(self, owner, start, rules):
        self.owner = owner
        self.cur = start
        self.rules = rules
        self.cur.enter(self.owner, None)

    def reset(self, state):
        # 지금 상태의 exit 없이 바로 시작 상태로 (리셋용)
        self.cur = state
        self.cur.enter(self.owner, None)

    def update(self):
        self.cur.do(self.owner)

    def draw(self):
        self.cur.draw(self.owner)

    def handle_event(self, event):
        for check, next_state in self.rules.get(self.cur, []):
            if check(self.owner, event):
                self.cur.exit(self.owner, event)
                self.cur = next_state
                self.cur.enter(self.owner, event)
                return
