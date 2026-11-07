# 박스야, 도망쳐! — 1주차 커밋 계획 (w1PRD)

> `week1` 브랜치에 실제로 올릴 커밋을 순서대로 정리한 문서입니다.
> 동작·수치의 원본은 [`1주차_PREPRD.md`](1주차_PREPRD.md)이고, 이 문서는 **무엇을 어떤 순서로 커밋할지**를 다룹니다. `§7.4`는 PREPRD의 7.4장을 뜻합니다.

- 기간: 11/4 ~ 11/10
- 목표: 프로젝트 골격 + 박스 조작 4가지(이동, 차지 점프, 테이프 줍기, 몸통박치기)를 평평한 바닥에서 플레이
- 범위 밖: 맵·카메라, 경비원, 보스, 타이틀·사운드 (PREPRD §2)

## 1. 작업 규칙

[전체 PRD 6장의 공통 작업 규칙](전체_PRD.md#모든-주차-공통-작업-규칙)을 따릅니다. 이 주차의 임시 규칙은 C22, C40에서 씁니다.

## 2. PREPRD와 다르게 잡은 부분

### 저장소 상태에 맞춘 것

| PREPRD | 이 문서 | 이유 |
|---|---|---|
| `GuruBox/` 폴더, `python main.py` | `project/` 폴더, 루트에서 `python project/main.py` | 코드는 `project/`, 리소스는 루트 `resource/`로 이미 옮겨져 있음 |
| `draw_tip(font, 문장, 52.5, 54, count)` | `draw_tip(font, 문장, 52.5, 54, count=count)` | 실제 함수의 다섯 번째 인자는 `cell_w`라서, 위치 인자로 넘기면 글자 수가 아니라 글자 간격이 바뀜 |
| 커밋 예시 `feat: ...` | `[week1] ...` | 기존 커밋 형식을 따름 |
| 바닥 y (전체 PRD는 310, PREPRD는 210) | **210** | PREPRD가 더 자세하고 도로 높이와 일치. 전체 PRD는 C48에서 수정 |
| 글씨 시트 1024 × 346 | 실제 파일은 1024 × 354 | 좌표는 모두 시트 안이라 동작에는 영향 없음 |

### 구현하며 정한 것

| 항목 | 내용 | 이유 |
|---|---|---|
| `ground.py` 추가 | 테스트 바닥 객체를 담는 파일 | PREPRD 파일 목록에 바닥을 둘 곳이 없음 |
| 디버그 키 순서 | B는 C12, F1은 C29에서 먼저 구현 (R만 마지막) | 테이프·몸통박치기를 확인할 때 필요 |
| `SCALE` 통일 | `sprite_data.SCALE = config.SPRITE_SCALE` | 같은 값이 두 곳에 있으면 어긋날 수 있음 |
| 점프 위치 계산 | `y += vy·dt - ½·g·dt²`, 그다음 `vy -= g·dt` | `y += vy·dt`만 쓰면 프레임 속도에 따라 높이가 달라짐 (20fps에서 최대 점프 기준 약 20px 차이) |
| 객체 참조 | `Box(hud)`처럼 생성자로 전달, 구간은 `box.zone`·`hud.set_zone()`으로 전달 | 모듈 간 순환 import를 피함 |
| 설정값 추가 | C02 표 외에 `BOX_START_X`(200), `BOX_BODY_H`(81), `CHARGE_SQUASH_X/Y`, `FX_END_SCALE`, `TAPE_BOB_H/TIME`, `DUMMY_FONT_SIZE`, `DUMMY_TEXT_GAP`, `UI_LIFE_EMPTY_ALPHA`, 위쪽 칸·팁 글자 위치 | 수치를 코드에 직접 쓰지 않는 규칙 |
| 임시 확인 방법 | C04, C06, C16 등의 임시 키·`print`·`delay`는 프로젝트에 넣지 않고 저장소 밖 확인 스크립트로 대신함 | 커밋에 임시 코드가 섞이지 않음 |
| 문서 커밋 순서 | C00은 C47 다음에 커밋 | M0을 건너뛰고 진행했고, C48의 링크가 저장소 안 문서를 가리켜야 함 |

### 결정한 것 (PREPRD에 정해지지 않았던 항목)

| # | 질문 | 결정 |
|---|---|---|
| Q1 | 줍기·돌진이 끝날 때 방향키가 눌려 있으면? (PREPRD는 무조건 IDLE) | 착지 규칙과 같게: 눌려 있으면 **WALK**, 아니면 IDLE |
| Q2 | ←/→를 동시에 누르면? | **마지막에 누른 방향으로 이동**. 그 키를 떼면 남은 방향으로 이동 |
| Q3 | 반짝임은 몇 초 동안? (떠오름 0.25초, 날아감 0.35초만 정해짐) | 떠오른 뒤 머리 위에서 **0.25초** 반짝이고, 날아갈 때는 끔 |
| Q4 | "박스 위 약 60px"의 기준은? | 박스 머리(발 + 81px)에서 위로 60px |
| Q5 | 걷기 깡충 주기는? | 일단 걷기 애니 한 바퀴(0.4초)에 1번: `HOP_HEIGHT·abs(sin(π·t/0.4))`. 플레이하며 조정 |
| Q6 | R을 누르면 구간도 초기화? | 구간은 유지 |

## 3. 파일 구조

```
2DGP_Project_2019180042/
├─ planning/
├─ resource/             # 이미 있음
└─ project/
   ├─ sprite_data.py     # 이미 있음 (C02, C23에서 수정)
   ├─ font_data.py       # 이미 있음
   ├─ test_sheet.py      # 이미 있음
   ├─ test_font.py       # 이미 있음
   ├─ main.py            # C01
   ├─ game_framework.py  # C01
   ├─ play_mode.py       # C01
   ├─ config.py          # C02
   ├─ game_world.py      # C05
   ├─ hud.py             # C07
   ├─ ground.py          # C14
   ├─ state_machine.py   # C15
   ├─ box.py             # C17
   ├─ tape.py            # C30
   └─ dummy.py           # C38
```

**그리기 레이어** (아래부터): `0` HUD(배경·글씨·생명 칸) → `1` 바닥 → `2` 테이프·허수아비 → `3` 박스 → `4` 줍기 연출

## 4. 커밋 목록

전체 49개. `[뼈대]`는 빈 정의와 호출 연결, `[채움]`은 실제 구현입니다.

### M0. 시작 전

#### C00 `[week1] w1PRD 문서 추가`
- 내용: `planning/w1PRD.md` 추가, `1주차_PRD.md` → `1주차_PREPRD.md` 이름 변경 포함
- 확인: 루트에서 `python project/test_sheet.py`, `python project/test_font.py` 실행 → 스프라이트·글씨가 그려짐

### M1. 골격·화면 틀 (CORE-1·2·4, UI-1~3)

#### C01 `[week1] 게임 루프 뼈대 추가` [뼈대]
- `main.py`: `game_framework.run(play_mode)` 호출
- `game_framework.py`: `run`, `quit`, `change_mode`, `push_mode`, `pop_mode` → `pass`, `frame_time = 0.0`
- `play_mode.py`: `init`, `finish`, `update`, `draw`, `handle_events` → `pass`
- 확인: 오류 없이 바로 종료

#### C02 `[week1] 설정값 파일 추가` [채움]
- `config.py`: PREPRD §8의 값 전부 + 아래 추가분
- `sprite_data.py`: `SCALE`을 `config.SPRITE_SCALE`에서 가져옴

| 추가 설정값 | 값 |
|---|---|
| `TAPE_XS` | (500, 900, 1300) |
| `TAPE_BB_RATE` | 0.8 |
| `FX_RISE_TIME`, `FX_SPARKLE_TIME`, `FX_FLY_TIME` | 0.25, 0.25, 0.35 |
| `FX_RISE_H`, `FX_SPARKLE_FPS` | 60, 8 |
| `DUMMY_X`, `DUMMY_W`, `DUMMY_H` | 1200, 84, 144 |
| `DUMMY_HIT_TIME`, `DUMMY_SHAKE` | 0.15, 4 |
| `SLAM_SX`, `SLAM_SY`, `SLAM_ROT` | 1.2, 0.85, 0.15 |
| `UI_LIFE_X`, `UI_LIFE_GAP`, `UI_LIFE_Y` | 60, 56, 772 |

- 확인: `test_sheet.py`가 그대로 동작

#### C03 `[week1] 게임 루프 구현` [채움]
- `main.py`: `open_canvas(1600, 900)` → `run` → `close_canvas()`
- `run`, `quit`, `frame_time` 계산 (시간 측정은 `init` 다음부터 시작)
- `play_mode.handle_events`: ESC·창 닫기 → `game_framework.quit()`
- `play_mode.draw`: `clear_canvas()` → `update_canvas()`
- 확인: 빈 창이 뜨고 ESC로 종료. 임시 `print`로 `frame_time`이 0보다 큰지 확인

#### C04 `[week1] 모드 전환 구현` [채움]
- 모드 스택으로 `change_mode`, `push_mode`, `pop_mode` 구현 (1주차에는 호출처가 없음)
- 확인: 임시 키에 `change_mode(play_mode)`를 연결해 `finish` → `init` 순서를 `print`로 확인 후 삭제

#### C05 `[week1] 게임 월드 뼈대 추가` [뼈대]
- `game_world.py`: `add_object`, `remove_object`, `update`, `draw`, `clear`, `add_collision_pair`, `handle_collisions` → `pass`
- `play_mode`: `update`와 `draw`에 `game_world.update()`, `game_world.draw()` 연결
- 확인: 빈 창 유지

#### C06 `[week1] 게임 월드 구현` [채움]
- 레이어별 객체 목록, `add_object`, `remove_object`, `update`, `draw`, `clear`
- 순회 중 객체가 자신을 지워도 되도록 복사본으로 순회
- 확인: 임시 객체로 레이어 순서와 삭제를 확인 후 삭제

#### C07 `[week1] HUD 뼈대 추가` [뼈대]
- `hud.py`의 `Hud`: `update`, `draw`, `set_zone`, `add_life`, `is_full`, `draw_now`, `draw_time`, `draw_tip`, `draw_lives` → `pass`
- `play_mode.init`에서 생성해 레이어 0에 등록
- 확인: 빈 창 유지

#### C08 `[week1] 그림일기 배경 표시` [채움] — §7.8
- `diary_frame.png`를 `(800, 450)`에 그림
- 확인: 제목·칸·원고지가 인쇄된 배경이 보임

#### C09 `[week1] 지금·도망친 지 표시` [채움] — §6
- `draw_now(font, '낮', '주택가', 868, 856)`
- `draw_number`로 일·시간·분 = 0, 0, 0 (x = 1218, 1328, 1474, y = 856)
- 확인: `낮, 주택가`, `0일 0시간 0분`이 칸에 맞음

#### C10 `[week1] 원고지 팁 한 문장 표시` [채움] — §7.8
- `TIP_LIST['day']`의 첫 문장을 `draw_tip(font, 문장, 52.5, 54)`으로 전부 표시
- 확인: 칸마다 한 글자씩, 띄어쓰기는 빈 칸

#### C11 `[week1] 원고지 팁 써지는 효과와 교체` [채움] — §7.8
- `count = int(경과 시간 / TIP_CHAR_TIME)`, `count=` 키워드로 전달
- `TIP_INTERVAL`마다 다음 문장, 끝나면 처음으로
- 확인: 한 글자씩 써지고 6초마다 바뀜

#### C12 `[week1] B키 구간 전환` [채움] — §7.9
- `play_mode.zone`을 `'chase'` ↔ `'boss'`로 전환, `hud.set_zone()` 호출
- 추격 = `낮, 주택가` + `TIP_LIST['day']`, 보스 = `저녁, 공원` + `TIP_LIST['boss']`
- 전환 시 팁을 첫 문장부터 다시 씀
- 확인: B를 누르면 지금 칸과 팁이 바뀜

#### C13 `[week1] 테이프 생명 칸 표시` [채움] — §7.8
- `lives = TAPE_START`, 5칸 표시 (x = 60 + 56·i, y = 772, `draw_item`에 `scale=1`)
- 빈 칸은 `opacify(0.25)`, 그린 뒤 **`opacify(1)`로 복구** (같은 시트의 다른 그림까지 흐려지는 것을 방지)
- `add_life`, `is_full` 구현
- 확인: 1칸 진하게, 4칸 흐리게

#### C14 `[week1] 테스트 바닥 추가` [채움]
- `ground.py`: `ph_ground.png`를 가운데 `(800, 160)`, 크기 `1560 × 100`으로 늘려 그림 (y 110 ~ 210)
- 레이어 1에 등록
- 확인: 플레이 칸 아래쪽에 띠가 보이고 윗면이 y = 210

### M2. 박스 서기·걷기 (CORE-3, BOX-1·2)

#### C15 `[week1] 상태 머신 뼈대 추가` [뼈대]
- `state_machine.py`의 `StateMachine(owner, start, rules)`: `update`, `draw`, `handle_event` → `pass`
- 규칙 형식: `{상태: [(조건 함수, 다음 상태), ...]}`
- 이벤트 형식: `('KEY', sdl_event)`, `('DONE', None)`
- 확인: 파일 import 시 오류 없음

#### C16 `[week1] 상태 머신 구현` [채움]
- `handle_event`: 조건이 맞으면 `exit` → 상태 교체 → `enter`
- `update` → 현재 상태의 `do`, `draw` → 현재 상태의 `draw`
- 확인: 임시 상태 2개로 전환을 `print`로 확인 후 삭제

#### C17 `[week1] 박스 뼈대 추가` [뼈대]
- `box.py`의 `Box`: `update`, `draw`, `get_bb`, `handle_event`, `handle_collision` → `pass`
- `Idle`, `Walk`: `enter`, `exit`, `do`, `draw` → `pass`
- 플래그: `on_accel_ground = False` (1주차엔 항상 False)
- `play_mode`: 레이어 3에 등록, `handle_events`에서 `box.handle_event(e)` 호출
- 확인: 화면 변화 없음, 키를 눌러도 오류 없음

#### C18 `[week1] 박스 서 있기` [채움] — §7.2
- `(x, y)`는 발 위치, 시작 `y = GROUND_Y`
- idle 3장 7fps 반복
- 확인: 바닥 위에서 선이 떨리고, 발이 바닥에 붙어 있음

#### C19 `[week1] 좌우 입력 상태 기록` [채움] — §7.1
- 왼쪽·오른쪽 눌림과 마지막에 누른 방향을 기록
- `dir`: 둘 다 눌리면 마지막에 누른 방향, 하나만 눌리면 그 방향, 없으면 0 (Q2)
- `face_dir`: `dir ≠ 0`일 때 `dir`과 같게, `dir = 0`이면 이전 값 유지
- 규칙: `dir ≠ 0`이면 IDLE → WALK, `dir = 0`이면 WALK → IDLE
- 확인: 임시 `print`로 확인 후 삭제. → 누른 채 ← 누름 → 왼쪽, ← 뗌 → 오른쪽, → 뗌 → 정지

#### C20 `[week1] 박스 걷기 이동` [채움] — §7.3
- `x += dir · WALK_SPEED · frame_time`
- 좌우 경계: `PLAY_LEFT + BOX_BB_W/2` ~ `PLAY_RIGHT - BOX_BB_W/2`
- `face_dir`가 왼쪽이면 `flip=True`
- 확인: 끝에서 멈추고 왼쪽으로 가면 반전됨

#### C21 `[week1] 걷기 애니메이션과 깡충` [채움] — §7.3
- jump 4장 10fps 반복, 그림 y에만 `HOP_HEIGHT·abs(sin(π·t/0.4))` 더함 (Q5)
- 실제 `y`는 바꾸지 않음
- 확인: 깡충거리는 동안 `y` 값이 `GROUND_Y`로 유지

### M3. 차지 점프 (CORE-5, BOX-3)

#### C22 `[week1] 차지·점프 상태 뼈대 추가` [뼈대]
- `Charge`, `Jump`: `enter`, `exit`, `do`, `draw` → `pass`
- 규칙: IDLE·WALK에서 Space 누름 → `Charge`
- `임시 규칙`: Charge에서 Space 뗌 → IDLE (C25에서 교체)
- 확인: Space를 누르는 동안 박스가 사라지고(빈 `draw`), 떼면 돌아옴

#### C23 `[week1] draw_box 가로세로 배율과 회전 추가` [채움] — §5
- `draw_box(..., sx=1, sy=1, rot=0)`, 기본값으로 기존 호출을 유지
- `sprite_data.py`에 `'charge'` → idle 1번, `'slam'` → jump 1번 분기를 둠 (진짜 그림이 오면 교체)
- 기준점 유지: `clip_composite_draw`는 **그림 가운데를 중심으로 회전**하므로 기준점까지의 거리도 함께 돌림
  - `dx = (BOX_W/2 - ax)·scale·sx·(반전이면 -1)`, `dy = (BOX_H/2 - ay)·scale·sy`
  - `cx = x + dx·cos(rot) - dy·sin(rot)`, `cy = y + dx·sin(rot) + dy·cos(rot)`
- 확인: `test_sheet.py`가 그대로 동작. 임시로 배율·회전을 줘도 발 위치가 고정됨

#### C24 `[week1] 차지 구현` [채움] — §7.4, §5
- `c = min(차지 시간 / CHARGE_MAX_TIME, 1)`
- 이동 속도 × `CHARGE_SPEED_RATE` (`on_accel_ground`면 감속 없음)
- 그림: `'charge'`, `sx = 1 + 0.20·c`, `sy = 1 - 0.25·c`
- 확인: 누를수록 납작해지고 느려지며, 0.6초 이후 더 변하지 않음

#### C25 `[week1] 수직 점프와 착지` [채움] — §7.4
- 임시 규칙 삭제. Space 뗌 → `Jump`, 높이 = `JUMP_MIN_H + (JUMP_MAX_H - JUMP_MIN_H)·c`
- `vy = sqrt(2·GRAVITY·높이)`, 위치 계산은 2장 방식
- 착지: `y <= GROUND_Y`면 바닥에 붙이고 `('DONE', None)` 전달 → `dir ≠ 0`이면 WALK, 아니면 IDLE
- 임시 그림: jump 1번
- 확인: 임시 `print`로 최고 높이 확인 (짧게 약 48, 길게 약 150) 후 삭제

#### C26 `[week1] 공중 좌우 조작` [채움] — §7.4
- 시작 `vx` = 차지 감속이 적용된 그때 속도
- 입력이 있으면 `vx`가 `dir·WALK_SPEED`로 `AIR_ACCEL`만큼 변함 (목표를 넘지 않게), 입력이 없으면 유지
- 공중에서도 좌우 경계 유지, Space·Shift 무시
- 확인: 공중에서 반대 키를 누르면 천천히 방향이 바뀜

#### C27 `[week1] 점프 그림 연결` [채움] — §7.4
- `vy > 0`이면 jump 1~2, `vy <= 0`이면 jump 3~4, 각 10fps
- 확인: 상승·하강 그림이 구분되고, 착지할 때 발이 튀지 않음

### M4. 테이프 줍기 (CORE-2, CORE-6, BOX-4, FX-1, UI-2)

#### C28 `[week1] 충돌 처리 구현` [채움] — §7.7
- `game_world`: `collide`, `add_collision_pair`, `handle_collisions`, `remove_object`에서 충돌 그룹도 제거
- `Box.get_bb`: `(x-43, y, x+43, y+66)` (`BOX_BB_W`, `BOX_BB_H` 사용)
- `play_mode`: `add_collision_pair('box:tape', box, None)`, `add_collision_pair('box:dummy', box, None)` / `update`에서 `game_world.update()` 다음에 `handle_collisions()`
- 확인: 오류 없이 실행, 동작 변화 없음

#### C29 `[week1] F1 충돌 박스 보기` [채움] — §7.9
- 충돌 쌍에 등록된 객체의 `get_bb()`를 `draw_rectangle`로 그림, F1로 켜고 끔
- 확인: 박스를 따라 빨간 사각형이 움직이고 F1로 사라짐

#### C30 `[week1] 테이프·줍기 뼈대 추가` [뼈대]
- `tape.py`의 `TapeItem`, `TapePickupFx`: `update`, `draw`, `get_bb`, `handle_collision` → `pass`
- `box.py`의 `Get`: `enter`, `exit`, `do`, `draw` → `pass`
- `play_mode.init`: `TAPE_XS`마다 `TapeItem` 생성, 레이어 2에 등록
- 확인: 화면 변화 없음

#### C31 `[week1] 바닥 테이프 표시` [채움] — §7.5
- 그림 `tape`, 크기 78 × 67, 가운데 y = `GROUND_Y + 67/2`
- `get_bb`: 그림의 80% (`TAPE_BB_RATE`)
- `'box:tape'` 쌍에 등록
- 확인: F1에서 테이프 3개의 충돌 박스가 보임

#### C32 `[week1] 테이프 겹침 기록` [채움]
- `Box.update` 시작 시 `near_tape = None`, `handle_collision('box:tape', tape)`에서 `near_tape = tape`
- 처리 순서: 이벤트 → `update` → 충돌. 다음 프레임의 Shift 입력에서 이전 프레임의 겹침 값을 사용
- 확인: 임시 `print`로 겹칠 때만 값이 있는지 확인 후 삭제

#### C33 `[week1] 테이프 줍기 상태` [채움] — §7.5
- `play_mode`의 B키 처리에서 `box.zone`도 함께 갱신
- 규칙: IDLE·WALK에서 Shift, `box.zone == 'chase'`, `near_tape` 있음, 생명 칸 여유 있음 → `Get`
- `enter`: 바닥 테이프 제거
- 0.5초 동안 멈춤·입력 무시 (좌우 눌림 기록은 계속), get 3장을 한 번 재생하고 마지막 장 유지
- 끝나면 `('DONE', None)` → WALK 또는 IDLE (Q1)
- 확인: 테이프 위 Shift → 0.5초 정면 그림, 테이프 사라짐. 떨어진 곳·보스 구간·공중·차지 중에는 반응 없음

#### C34 `[week1] 줍기 연출 떠오름` [채움] — §7.5
- `Get.enter`에서 `TapePickupFx` 생성, 레이어 4에 등록
- 0.25초 동안 머리 위 60px로 상승 (Q4)
- 확인: 테이프가 박스 머리 위로 떠오름 (이 커밋에서는 그 자리에 남음)

#### C35 `[week1] 줍기 연출 반짝임` [채움] — §7.5
- 떠오른 뒤 0.25초 동안 테이프 뒤에 sparkle 2장을 8fps로 번갈아 그림 (Q3)
- 확인: 반짝임이 테이프 뒤에 보임

#### C36 `[week1] 줍기 연출 날아가기와 생명 +1` [채움] — §7.5
- 목표 칸 = `lives + 비행 중인 연출 수`로 생성 시 고정, x = `UI_LIFE_X + UI_LIFE_GAP·칸`, y = `UI_LIFE_Y`
- 0.35초 동안 이동하며 배율 0.6 → 0.37 (생명 칸 크기와 비슷하게)
- 도착 시 `hud.add_life()`, 연출 삭제
- 줍기 조건도 `lives + 비행 중인 연출 수 < TAPE_MAX`로 변경
- 확인: 도착 순간 칸이 채워짐. 5칸이면 Shift에 반응 없고 테이프가 남음

#### C37 `[week1] 바닥 테이프 둥실 효과` [채움] (선택) — §7.5
- 그림만 진폭 4px, 1초 주기로 상하 이동, 충돌 박스는 고정
- 확인: 테이프가 둥실거리고 F1 사각형은 움직이지 않음

### M5. 몸통박치기 (BOX-5)

#### C38 `[week1] 허수아비 뼈대 추가` [뼈대]
- `dummy.py`의 `Dummy`: `update`, `draw`, `get_bb`, `handle_collision`, `on_hit` → `pass`
- `play_mode.init`: 레이어 2에 등록
- 확인: 화면 변화 없음

#### C39 `[week1] 허수아비 표시` [채움] — §7.6
- `ph_dummy.png`, 가운데 `(DUMMY_X, GROUND_Y + DUMMY_H/2)`, 크기 84 × 144
- `get_bb` 구현, `'box:dummy'` 쌍에 등록
- 확인: F1에서 충돌 박스가 보임

#### C40 `[week1] 몸통박치기 상태 뼈대 추가` [뼈대]
- `Slam`: `enter`, `exit`, `do`, `draw` → `pass`
- 규칙: IDLE·WALK에서 Shift, `box.zone == 'boss'` → `Slam`
- `임시 규칙`: Slam에서 Shift 뗌 → IDLE (C41에서 교체)
- 확인: 보스 구간에서 Shift를 누르는 동안 박스가 사라지고, 추격 구간에서는 그대로

#### C41 `[week1] 몸통박치기 돌진` [채움] — §7.6
- 임시 규칙 삭제
- `enter`에서 시작 위치와 방향 고정, `x = 시작 x + 방향·SLAM_DIST·min(t/SLAM_TIME, 1)`, 좌우 경계 유지
- 끝나면 `('DONE', None)` → WALK 또는 IDLE (Q1)
- 돌진 중 이동·점프 입력 무시
- 확인: 임시 `print`로 이동 거리 약 130px 확인 후 삭제

#### C42 `[week1] 몸통박치기 임시 그림` [채움] — §5
- `'slam'`, `sx = SLAM_SX`, `sy = SLAM_SY`
- 기울기: 오른쪽 돌진이면 `rot = -SLAM_ROT`, 왼쪽이면 `+SLAM_ROT` (양수가 반시계 방향)
- 확인: 양쪽 모두 진행 방향으로 기울고 발이 바닥에 붙어 있음

#### C43 `[week1] 몸통박치기 1회 판정과 횟수 표시` [채움] — §7.6
- `Slam.enter`에서 `slam_hit = False`
- `Box.handle_collision('box:dummy', other)`: 돌진 중이고 `slam_hit`이 False면 True로 바꾸고 `other.on_hit()` 호출
- 판정은 박스 쪽에서만, `Dummy.handle_collision`은 `pass` 유지
- `Dummy.on_hit`: 횟수 +1, 머리 위에 표시 (`load_font('resource/font/Gaegu-Bold.ttf', ...)`)
- 확인: 돌진 한 번에 횟수가 1만 오름. 추격 구간에서 걸어서 겹쳐도 오르지 않음

#### C44 `[week1] 허수아비 흔들림` [채움] — §7.6
- 맞은 뒤 `DUMMY_HIT_TIME` 동안 그림만 좌우 ±`DUMMY_SHAKE`px
- 확인: 맞을 때 흔들리고 충돌 박스는 고정

#### C45 `[week1] 몸통박치기 쿨타임` [채움] — §7.6
- `Slam.exit`에서 `SLAM_COOLDOWN` 시작, `Box.update`에서 항상 감소
- Slam 진입 조건에 `쿨타임 <= 0` 추가
- 확인: 끝난 직후 Shift를 연타해도 0.5초 동안 나가지 않음

### M6. 디버그 키·마무리 (CORE-6)

#### C46 `[week1] R키 리셋` [채움] — §7.9
- `play_mode.reset()`: 박스 위치·상태, 생명, 테이프 3개, 허수아비 횟수, 쿨타임, 비행 중인 연출을 처음으로
- 구간은 유지 (Q6), 키를 누른 채 리셋해도 눌림 상태는 유지
- 확인: 줍기·돌진·연출 도중에 R을 눌러도 오류 없이 복구

#### C47 `[week1] 1주차 코드 정리` [채움]
- 남은 임시 코드·`print` 삭제, `test_font.py`의 `GuruBox` 주석을 현재 실행 방법으로 수정
- 프레임 독립 확인: 루프에 임시로 `delay(0.05)`를 넣어 점프 높이·걷기 속도·돌진 거리 비교 후 삭제
- 확인: 5장 완료 기준 전체 통과

#### C48 `[week1] 전체 PRD 진행 상황 갱신`
- `전체_PRD.md`: 1주차 기능 상태 갱신, 테스트 바닥 `y=310` → `y=210`, 주차 PRD 링크를 현재 문서 이름으로 수정, 7장 기록 추가
- 확인: 문서 내용이 실제 결과와 같음

## 5. 완료 기준

PREPRD §9의 기준을 어느 커밋에서 처음 확인할 수 있는지 정리한 표입니다. 최종 확인은 C47에서 전부 다시 합니다.

| 완료 기준 | 커밋 | 결과 |
|---|---|---|
| 1600 × 900 창, 배경, `낮, 주택가`, `0일 0시간 0분` | C09 | ✅ |
| 팁이 한 글자씩 써지고 6초마다 바뀜 | C11 | ✅ |
| 서 있을 때 idle 반복 | C18 | ✅ |
| ←/→로 걷고, 깡충 뛰고, 왼쪽이면 반전 | C21 | ✅ |
| 모든 그림에서 발 높이가 같음 | C27 | 🟨 직접 확인 필요 |
| 짧게 약 48px, 0.6초 이상 약 150px 점프 | C25 | ✅ |
| 차지 중 느려지고 납작해짐 | C24 | ✅ |
| 공중에서 반대 방향으로 천천히 전환 | C26 | ✅ |
| 상승 jump 1~2, 하강 jump 3~4 | C27 | ✅ |
| 테이프 줍기 연출 후 생명 칸이 채워짐 | C36 | ✅ |
| 생명 칸 5개면 줍지 못함 | C36 | ✅ |
| B로 전환, 돌진 한 번에 횟수 1 증가 | C43 | ✅ |
| 쿨타임 동안 몸통박치기 불가 | C45 | ✅ |
| F1 충돌 박스, R 리셋 동작 | C46 | ✅ |
| 프레임 속도와 무관하게 이동·점프 높이가 같음 | C47 | ✅ |

- 결과는 키 입력을 스크립트로 넣어 실제 창에서 확인한 것이고, 직접 플레이 확인은 남아 있습니다.
- 발 높이: 같은 애니메이션 안에서 그림의 가장 아래쪽 위치가 프레임마다 화면 기준 최대 약 4px 다릅니다 (idle, jump, 흰 테두리 포함 측정).
- 프레임 독립: 459fps와 19fps에서 점프 높이 150.0 / 149.7, 걷기 속도 310.1 / 309.9, 돌진 거리 130.0 / 130.0.

## 6. 끝난 뒤 정리할 것

- 완료 기준 결과를 위 표에 기록
- 플레이하며 조정이 필요해 보인 수치 목록을 전체 PRD 5장에 반영
- 2주차 PRD로 넘길 항목 확인 (PREPRD §11)
