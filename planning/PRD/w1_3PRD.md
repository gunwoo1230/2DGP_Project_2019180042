# 박스야, 도망쳐! — 1주차_3 커밋 계획 (w1_3PRD)

> `week1_3` 브랜치에 실제로 올릴 커밋을 순서대로 정리한 문서입니다. 1주차 기간 안에 3주차 일부(경비원·해·점수)를 먼저 진행합니다.
> 동작·수치의 원본은 [`w1_3PREPRD.md`](w1_3PREPRD.md)이고, 이 문서는 **무엇을 어떤 순서로 커밋할지**를 다룹니다. `§7.4`는 PREPRD의 7.4장을 뜻합니다.

- 작업 시점: 11/8 ~ (1주차 기간). 계획상으로는 3주차(11/18 ~ 11/24) 일부
- 목표: 61칸 낮 맵에서 사각형 경비원에게 쫓기며 새 건물마다 10분씩 점수가 오르고 해가 움직이며, 해가 오른쪽에 닿으면 보스 구간으로 넘어간다. 조금 일찍 누른 키가 씹히지 않고, 왔던 길로 되돌아갈 수 있다
- 범위 밖: 진짜 경비원·해 그림, 보스·밤, 물웅덩이·창문·비둘기, 테이프 층별 배치, 최고 기록 저장 (PREPRD §2)

## 1. 작업 규칙

[전체 PRD 6장의 공통 작업 규칙](00_전체PRD.md#모든-주차-공통-작업-규칙)을 따릅니다. 이 주차에만 다른 점은 아래와 같습니다.

- 커밋 메시지 접두어는 `[week1_3]`입니다.
- 커밋마다 프로그램이 오류 없이 도는지 보고, 각 `확인` 항목은 **M 단계가 끝날 때마다** 키 입력을 넣는 스크립트로 한꺼번에 확인합니다. 스크립트는 저장소 밖에 둡니다. 마지막(C22)에는 2주차 검사도 다시 돌립니다.
- 푸시는 마지막에 요청이 있을 때 합니다.

### 시작 전 상태

| 항목 | 상태 | 할 일 |
|---|---|---|
| `week1_2` | `main`에 병합함 (fast-forward, `7775fae`) | 없음. `week1_3`는 이 커밋에서 시작 |
| 임시 그림 4장 (`ph_guard`, `ph_gauge_bg`, `ph_gauge` 4×4, `ph_sun` 96×96) | `resource/placeholder/`에 있음, 커밋 안 됨 | C00에 포함 |
| `planning/preview/tile_guide.png`, `planning/preview/test_map_preview.png` | 문서 정리 커밋에 포함 | 없음. `test_map_preview.png`는 지금 `TEST_MAP` 모양과 같음을 눈으로 확인함 |
| `w1_3PREPRD.md`, `00_전체PRD.md` 수정분 (점수 규칙·BOX-12 추가), 이 문서 | 문서 정리 커밋에 포함 | 없음 |
| 문서 위치 | `planning/PRD/`(문서), `planning/preview/`(참고 그림)로 정리하고 브랜치 순서대로 이름 변경 (`w1_1` = `week1`, `w1_2` = `week1_2`) | 없음 |

## 2. PREPRD와 다르게 잡은 부분

### 기존 동작이 바뀌는 것

| 지금 | 이 문서 | 이유 |
|---|---|---|
| R은 구간(`chase`/`boss`)을 유지하고 박스·생명·테이프만 처음으로 | R은 **완전히 처음부터**: 레벨 `DAY_MAP`, 구간 `chase`, 점수·해·경비원 포함 | PREPRD §9. 잡혔을 때와 같은 함수 `restart()`를 씀 |
| `Box.update` 맨 앞에서 `near_tape = None` | `update` **맨 끝**에서 지움 | 남은 Shift를 `update` 안에서 처리할 때 직전 충돌 결과가 남아 있어야 함 (Q2) |
| 박스 왼쪽 한계 = 화면 왼쪽 끝 | 맵 왼쪽 끝 `MAP_LEFT + BOX_BB_W/2` | PREPRD §6.2 |

### 진행 순서를 바꾼 것

| PREPRD §12 | 이 문서 | 이유 |
|---|---|---|
| 3단계에서 낮 맵·점수, 7단계에서 디버그 키 | `day.py`의 `phase`(구간)를 M3에서 먼저 만들고, B키가 이것을 바꾸게 함 | 경비원(M5)이 "추격 중에만 움직임"을 확인하려면 구간 상태가 먼저 있어야 함 |
| 7단계에서 E키 | E키는 M6 앞(C18)에서 추가 | 낮 끝을 확인하려면 60칸까지 빨리 가는 수단이 먼저 필요함. G·M은 C20 |

### 결정한 것 (PREPRD에 정해지지 않았던 항목)

| # | 질문 | 결정 |
|---|---|---|
| Q1 | 남은 입력을 상태 머신에 어떻게 넣나? | 새 이벤트 `('BUFFER', None)`. `Box.update`에서 발밑 검사 다음, 상태가 Idle·Walk면 보냄. Idle·Walk 규칙: `space_ready` → Charge, `can_pick_tape` → Get, `can_slam` → Slam. Charge로 들어갔는데 Space를 이미 뗐으면 같은 프레임에 `BUFFER`를 한 번 더 보내 Jump (차지 0 = 최소 높이). `Jump.enter`는 `KEY`와 `BUFFER`를 차지 점프로 처리 |
| Q2 | 남은 Shift를 처리할 때 `near_tape`가 비어 있음 | `near_tape = None`을 `update` 끝으로 옮김. 순서: 쿨타임 감소 → 상태 `do` → 발밑 검사 → 남은 입력 처리 → 입력 기억 시간 감소 → `near_tape` 지움 |
| Q3 | 몸통박치기가 끝나기 직전 Shift | 쿨타임(0.5초)이 기억 시간(0.15초)보다 길어서, 쿨타임이 끝나기 0.15초 안에 누른 것만 이어짐. 쿨타임은 그대로 둠. Space는 PREPRD대로 이어짐 |
| Q4 | 낮 진행 상태를 어디서 관리하나? | `day.py` 모듈 변수 `phase` = `'chase'`(추격) / `'caught'`(잡힘 멈춤) / `'day_end'`(경비원 지침) / `'boss'`, 그리고 `best_tile`, `sun_p`, `timer`. 전환은 `play_mode`가 함. `box.zone`·`hud.zone`은 `phase == 'boss'`면 `'boss'`, 나머지는 `'chase'` |
| Q5 | 잡힘을 박스 상태로 어떻게 표현하나? | 새 상태 `Caught` (hit 1장, 움직이지 않음, 규칙 없음 = 입력 무시). `box.catch()`가 `state_machine.reset(Caught)`. 공중에서 잡히면 그 자리에 멈춤. 좌우 눌림 기록은 계속 |
| Q6 | 경비원은 리셋 때 다시 만드나? | 한 번 만들고 `reset()`으로 처음 위치로. `restart()`가 ITEM 레이어를 지운 뒤 다시 넣음. 게이지가 경비원을 계속 참조할 수 있음. 보스 구간으로 갈 때는 다시 넣지 않음 |
| Q7 | 보스 구간 전환 때 FX 레이어는? | **지우지 않음.** 날아가는 중인 테이프 연출을 지우면 생명이 들어오지 않고 `hud.reserved`가 남음. 도는 별은 박스 상태가 바뀌면 스스로 지워짐 |
| Q8 | "마지막 칸 번호"는? | 지금 레벨의 `len(tiles) - 1` (`DAY_MAP`이면 60). `TEST_MAP`에서는 10칸째에서 낮 끝이 됨 |
| Q9 | N·E로 크게 건너뛰면 해가 한참 늦게 따라옴 (초당 0.05) | N·E·`restart()`는 `sun_p`를 목표로 바로 맞춤. 걸어서 새 칸에 들어갈 때만 부드럽게 움직임 |
| Q10 | G로 끈 경비원은? | 멈추고, 잡힘 판정 없고, **게이지도 숨김**. G 상태는 R·잡힘 뒤에도 유지 (F1처럼 디버그 설정) |
| Q11 | M으로 바꾼 레벨에서 R·잡힘이 일어나면? | PREPRD대로 `DAY_MAP`으로 돌아감. M은 "다른 맵으로 `restart()`" |
| Q12 | 잡힘·낮 끝 중 디버그 키 | 잡힘 중에는 R, F1, ESC만 받음. B는 잡힘·낮 끝 중 무시. 낮 끝 중에도 N·1/2/3은 그대로 |
| Q13 | 게이지는 언제 보이나? | `chase`, `caught`, `day_end`에서 보임 (경비원이 켜져 있을 때). `boss`에서 숨김 |

### 플레이하며 확인할 위험

| 항목 | 내용 | 확인 커밋 |
|---|---|---|
| 해가 플레이 칸 위로 나감 | 가운데 y가 최대 780, 그림 반지름 48 → 위 끝 828. 플레이 칸 위(810)와 테두리 덮개 위(820)를 넘어 헤더를 약간 가림. 수치는 바꾸지 않고 보고 판단 (방법: `SUN_RY`를 줄이거나 해를 잘라 그림) | C12 |
| 추락 멈춤과 경비원 | 지붕 → 도로 2초 멈춤 동안 경비원이 560px 다가옴. 시작 거리 600에서 크게 벌리지 못했으면 바로 잡힘. 의도한 위험인지 판단 | C16 |
| 배수관 오르기 | 도로 → 지붕 오르기에 점프 여러 번이 들어가 그동안 가로로 거의 못 감. 경비원 280px/s가 따라잡는지 확인 | C16 |
| 레벨 크기 | 61칸 발판 약 330개를 매 프레임 착지·발밑 검사에서 모두 훑음. 느려지면 타일 번호로 범위를 좁힘 | C06 |

## 3. 파일 구조

```
project/
├─ day.py        # 새로, C07: phase, best_tile, sun_p, timer, reset, update, minutes
├─ guard.py      # 새로, C13: Guard (임시 사각형, 쫓아오기, 지침)
├─ box.py        # 수정: 입력 기억, BUFFER 이벤트, Caught 상태, 왼쪽 한계
├─ camera.py     # 수정: 양방향 따라가기
├─ level.py      # 수정: load(tile_names)로 레벨 교체, tile_index(x)
├─ hud.py        # 수정: 도망친 지 숫자, Sun, Gauge
├─ game_world.py # 수정: LAYER_SKY 추가 (7개)
├─ map_data.py   # 수정: DAY_PATTERN, DAY_MAP, BOSS_ARENA (TEST_MAP 유지)
├─ play_mode.py  # 수정: restart, 잡힘·낮 끝·보스 전환, G·E·M 키
├─ state_machine.py  # 수정: 이벤트 형식 주석에 BUFFER
└─ config.py     # 수정: PREPRD §10 설정값
```

- `day`는 `camera`처럼 **모듈 변수**로 둡니다. `hud`(숫자·해)와 `guard`(움직일지)가 읽고, `play_mode`만 바꿉니다. `day.py`는 `config`만 가져오므로 순환 import가 없습니다.
- `Level`은 박스가 참조를 들고 있으므로 새로 만들지 않고 `load(tile_names)`로 내용만 바꿉니다.

**그리기 레이어** (아래부터): `0` BG 배경 → `1` SKY 해 → `2` MAP 맵 → `3` ITEM 테이프·허수아비·경비원 → `4` BOX 박스 → `5` FX 줍기 연출·도는 별 → `6` UI 테두리 덮개·생명 칸·글씨·게이지

**상태 전환** (2주차 규칙에 추가되는 것)

| 상태 | 추가 규칙 |
|---|---|
| Idle, Walk | `BUFFER` + Space 남음 → Charge, `BUFFER` + Shift 남음 → Get / Slam (기존 조건 그대로) |
| Charge | `BUFFER` + Space 이미 뗌 → Jump (차지 0) |
| Caught | 규칙 없음. `box.catch()`로만 들어가고 `restart()`로만 나옴 |

**한 프레임 순서** (`play_mode.update`): `game_world.update` → 충돌 처리 → `camera.follow` → `day.update` → 잡힘 검사 → 낮 끝·보스 전환

## 4. 커밋 목록

전체 23개. `[뼈대]`는 빈 정의와 호출 연결, `[채움]`은 실제 구현입니다.

### M0. 시작 전

#### C00 `[week1_3] 임시 그림 추가`
- 내용: 임시 그림 4장 (문서는 앞의 문서 정리 커밋에서 올림)
- 확인: `week1_3` 브랜치에서 `python project/main.py` 실행 → `week1_2`와 동작이 같음

### M1. 입력 버퍼 (BOX-12)

#### C01 `[week1_3] Space·Shift 입력 기억` [채움] — §5.2
- `INPUT_BUFFER_TIME = 0.15`
- `Box`: `space_waiting`, `space_held`, `space_buffer`, `shift_buffer`. `handle_event`에서 Space 누름·뗌, Shift 누름을 기록
- `update`에서 두 기억 시간을 `frame_time`만큼 줄임 (0 아래로 안 감)
- `Charge.enter`에서 `space_waiting = False`, `Get.enter`·`Slam.enter`에서 `shift_buffer = 0`, `reset`에서 모두 지움
- 확인: 동작 변화 없음. 임시 `print`로 공중에서 Space를 누르면 기록되고 0.15초 뒤 0이 되는지 확인 후 삭제

#### C02 `[week1_3] 땅에 서면 남은 Space 처리` [채움] — §5.2
- `state_machine.py` 주석에 `('BUFFER', None)` 추가
- `Box.use_buffer()`: Idle·Walk면 `space_waiting`이 남았는지 보고, 누르고 있지도 않고 기억 시간도 0이면 버림. 남았으면 `('BUFFER', None)` (Q1)
- 조건 `space_ready`: `BUFFER`이고 `space_waiting`. Idle·Walk 규칙에 `(space_ready, Charge)`
- 조건 `space_tapped`: `BUFFER`이고 `not space_held`. Charge 규칙에 `(space_tapped, Jump)`. `use_buffer`에서 Charge로 들어갔고 이미 뗐으면 한 번 더 보냄
- `Jump.enter`: `KEY`와 `BUFFER`를 차지 점프로
- `Box.update` 순서를 Q2대로
- 확인: 착지 0.1초 전 Space를 누르고 있으면 착지하자마자 Charge, 톡 치면 최소 높이 점프. 0.3초 전에 톡 치면 착지 후 그대로 Idle. 회복·줍기·몸통박치기 끝나기 직전 Space가 이어짐. 땅 위 Space는 그 프레임에 바로 Charge

#### C03 `[week1_3] 남은 Shift로 줍기·몸통박치기` [채움] — §5.2
- 조건 `shift_ready`: Shift 누름 `KEY`, 또는 `BUFFER`이고 `shift_buffer > 0`. `can_pick_tape`, `can_slam`이 이것을 씀
- `use_buffer`가 `shift_buffer > 0`일 때도 `BUFFER`를 보냄 (Space가 먼저)
- `near_tape = None`을 `update` 끝으로 (Q2)
- 확인: 테이프에 닿기 0.1초 전 Shift로 줍기. 테이프 위에서 바로 누른 Shift도 그대로. 추격 구간에서 Shift를 누른 뒤 0.15초 지나 닿으면 줍지 않음

### M2. 되돌아가기 (CORE-7)

#### C04 `[week1_3] 카메라 양방향 따라가기` [채움] — §6.1
- `CAMERA_BACK_X = 400`, `CAMERA_FOLLOW_X` 주석을 "이 화면 x보다 오른쪽이면 카메라가 오른쪽으로"로
- `follow`: 화면 x가 640보다 크면 `box.x - 640`, 400보다 작으면 `box.x - 400`, 그 외 그대로. `0 ~ max_x`로 자름
- `camera.py` 첫 줄 주석 갱신
- 확인: 오른쪽으로 갔다가 왼쪽으로 걸으면 화면 x 400에서 카메라가 왼쪽으로 따라옴. 시작 칸에서는 카메라 0

#### C05 `[week1_3] 박스 왼쪽 한계를 맵 왼쪽 끝으로` [채움] — §6.2
- `clamp_x`: 왼쪽 `MAP_LEFT + BOX_BB_W/2`
- 확인: 왔던 길로 시작 칸까지 돌아가고, 맵 왼쪽 끝에서 막힘. 테두리 밖으로 삐져나오지 않음

### M3. 낮 맵·점수 (MAP-3, DAY-1·3)

#### C06 `[week1_3] 낮 맵 61칸` [채움] — §7.2
- `map_data.py`: `DAY_PATTERN`, `DAY_MAP`, `BOSS_ARENA`
- `play_mode`: `Level(DAY_MAP)`로 시작
- 확인: N으로 끝까지 가면 61칸, 맵 끝에서 카메라와 박스가 멈춤. 걷는 동안 프레임이 떨어지지 않음 (2장 위험)

#### C07 `[week1_3] 낮 진행 상태 뼈대 추가` [뼈대] — §7.1
- `day.py`: `phase = 'chase'`, `best_tile = 0`, `sun_p = 0.0`, `timer = 0.0`. `reset`, `update(box_x, level)` → `pass`, `minutes()`는 정의만 (반환값을 쓰므로 호출은 C09에서)
- `play_mode`: `init`·`reset`에서 `day.reset()`, `update`에서 `day.update(box.x, level)`
- 확인: 동작 변화 없음

#### C08 `[week1_3] 최고 도달 타일과 구간 상태` [채움] — §7.1
- `MINUTES_PER_TILE = 10`
- `Level.tile_index(x)` = `int((x - MAP_LEFT) // TILE_W)`, 0 ~ 마지막 칸으로 자름
- `day.update`: `phase == 'chase'`일 때만 `best_tile = max(best_tile, tile_index)`. `minutes() = best_tile × 10`
- B키 `toggle_zone`이 `day.phase`를 `chase` ↔ `boss`로 바꾸고, 박스·HUD 구간은 여기서 정함 (Q4)
- 확인: 임시 `print`로 새 칸에 들어갈 때만 오르고, 뒤로 가거나 떨어져도 줄지 않으며, B로 보스 구간이면 오르지 않음을 확인 후 삭제

#### C09 `[week1_3] 도망친 지 칸 표시` [채움] — §7.1
- `hud.draw_time`: `day.minutes()`로 `일 = 분 // 1440`, `시간 = 분 // 60 % 24`, `분 = 분 % 60`
- 확인: 6칸째에 `0일 1시간 0분`, 13칸째에 `0일 2시간 10분`

### M4. 해 (DAY-2)

#### C10 `[week1_3] 하늘 레이어 추가` [채움] — §7.3
- `game_world`: `LAYER_BG, LAYER_SKY, LAYER_MAP, LAYER_ITEM, LAYER_BOX, LAYER_FX, LAYER_UI` (7개)
- 확인: 화면 변화 없음

#### C11 `[week1_3] 해 그리기` [채움] — §7.3
- `SUN_CENTER_X, SUN_CENTER_Y = 800, 640`, `SUN_RX, SUN_RY = 720, 140`
- `hud.py`의 `Sun`: `ph_sun.png`를 1배로, `x = 800 - 720·cos(π·p)`, `y = 640 + 140·sin(π·p)`, `p = day.sun_p`. `boss`면 그리지 않음. `LAYER_SKY`
- `day.update`: 이 커밋에서는 `sun_p = best_tile / 마지막 칸` (Q8)
- 확인: 시작 칸에서 왼쪽 아래, 30칸에서 가운데 위, 건물이 해를 가림. B로 보스면 해가 없음

#### C12 `[week1_3] 해가 부드럽게 따라감` [채움] — §7.3
- `SUN_SPEED = 0.05`
- `day.target_p()`, `sun_p`가 목표를 향해 초당 0.05씩 움직이고 넘치지 않음. `day.snap_sun()`: 바로 맞춤 (`reset`·N에서 사용, Q9)
- 확인: 새 칸에 들어가면 해가 툭 끊기지 않고 미끄러짐. 해 위 끝이 헤더를 얼마나 가리는지 스크린샷으로 기록 (2장 위험)

### M5. 경비원 (CHASE-1·2, UI-4, BOX-11)

#### C13 `[week1_3] 경비원 뼈대 추가` [뼈대] — §8.1
- `guard.py`: `Guard`의 `reset`, `update`, `draw` → `pass`, `get_bb`, `handle_collision` → `pass`
- `play_mode`: 한 번 만들어 `LAYER_ITEM`에 넣고, `reset`에서 ITEM 레이어를 지운 뒤 다시 넣음 (Q6)
- 확인: 동작 변화 없음

#### C14 `[week1_3] 경비원 쫓아오기` [채움] — §8.1
- `GUARD_W, GUARD_H = 90, 170`, `GUARD_START_GAP = 600`, `GUARD_START_DELAY = 1`, `GUARD_SPEED = 280`
- 시작 x = `BOX_START_X - 600`, 1초 기다린 뒤 오른쪽으로 280px/s. 발은 `ROAD_Y`. `day.phase == 'chase'`이고 `enabled`일 때만 움직임
- `ph_guard.png`를 90×170으로 늘려 그림, 카메라 반영, 화면 밖이면 건너뜀
- 확인: 1초 뒤 출발해 도로를 따라 오고 박스 뒤에 그려짐. 계속 걸으면 거리가 초당 30씩 벌어짐. B로 보스면 멈춤

#### C15 `[week1_3] 잡힘 상태 뼈대 추가` [뼈대] — §8.2
- `box.py`의 `Caught`: `enter`, `exit`, `do`, `draw` → `pass`, `Box.catch()`
- `play_mode.restart()`: 지금 `reset()`의 내용을 옮기고 이름만 바꿈 (R이 호출)
- 확인: 동작 변화 없음

#### C16 `[week1_3] 잡힘 판정과 처음부터 다시` [채움] — §8.2
- `CATCH_DIST = 90`, `CAUGHT_TIME = 1`
- `play_mode.update`: `phase == 'chase'`, 경비원 켜짐, `box.x - guard.x ≤ 90`이면 `phase = 'caught'`, `box.catch()`
- `Caught`: hit 1장, 움직이지 않음. `caught` 중 경비원도 멈춤. `CAUGHT_TIME` 뒤 `restart()`
- `restart()`: ITEM·FX 레이어 비우고 테이프·허수아비·경비원 다시, 생명, 박스, 카메라, `day.reset()`, 구간 `chase` (2장 R 변경)
- 잡힘 중 디버그 키는 R, F1, ESC만 (Q12)
- 확인: 도로에서 멈춰 있으면 잡힘. 지붕 위에서도 가로 거리 90이면 잡힘. 1초 hit 그림 후 점수·해·생명·테이프 모두 처음. 지붕 → 도로 추락 멈춤 중에 잡히는지 기록 (2장 위험)

#### C17 `[week1_3] 거리 게이지` [채움] — §8.3
- `GAUGE_X, GAUGE_Y, GAUGE_W, GAUGE_H = 1420, 772, 240, 18`
- `hud.py`의 `Gauge(box, guard)`: `ph_gauge_bg` 위에 `ph_gauge`를 왼쪽 정렬로, 비율 = `(거리 - 90) / (600 - 90)`을 0 ~ 1로. `LAYER_UI`, 보이는 때는 Q13
- 확인: 시작할 때 꽉 참, 걸으면 늘고 멈추면 줄어듦, 잡히는 순간 빔. B로 보스면 숨김

### M6. 낮 끝 → 보스 구간 (MAP-6, FX-4 임시)

#### C18 `[week1_3] E키 마지막 칸 앞으로 이동` [채움] — §9
- `play_mode`: E → `level.tiles[-2]` 왼쪽 끝 도로로 `box.warp`, 해는 `snap_sun` (Q9). N도 `snap_sun`
- 확인: E 한 번에 59칸 도로, `0일 9시간 50분`, 해가 거의 오른쪽

#### C19 `[week1_3] 낮 끝과 경비원 지침` [채움] — §7.4
- `DAY_END_TIME = 2`
- `day.update`: `chase`에서 `best_tile`이 마지막 칸이 되면 `phase = 'day_end'`, `timer = 0`
- `Guard`: `day_end`면 멈추고 높이 절반으로 바닥에 붙여 그림. 잡힘 판정 없음
- 이 커밋에서는 2초 뒤 아무 일도 없음 (다음 커밋에서 연결)
- 확인: 60칸째에 들어가면 `0일 10시간 0분`, 해가 오른쪽 끝, 경비원이 주저앉고 박스는 계속 움직임

#### C20 `[week1_3] 보스 구간으로 전환` [채움] — §7.4
- `Level.load(tile_names)`: 타일·발판·오른쪽 끝을 다시 만듦
- `play_mode.to_boss()`: `DAY_END_TIME` 뒤 호출. `phase = 'boss'`, 구간 `boss`, `level.load(BOSS_ARENA)`, `camera.init`, `box.reset()`, ITEM 레이어를 비우고 허수아비만 다시 (FX 레이어는 유지, Q7). 생명은 그대로
- `restart()`: 레벨이 `DAY_MAP`이 아니면 `load(DAY_MAP)`, `camera.init`
- 확인: 2초 뒤 `저녁, 공원`, 빈터에 허수아비, 생명 수 유지, Shift가 몸통박치기. 점수 600분 고정, 경비원·게이지·해 없음. R로 낮 맵 처음

### M7. 마무리

#### C21 `[week1_3] G·M 디버그 키` [채움] — §9
- G: `guard.enabled` 토글, 꺼지면 멈추고 잡힘 판정·게이지 없음 (Q10)
- M: 지금이 `DAY_MAP`이면 `TEST_MAP`으로, 아니면 `DAY_MAP`으로 `restart()` (Q11)
- 확인: G로 끄면 도로에 서 있어도 잡히지 않음. M으로 테스트 맵 11칸, 다시 M으로 낮 맵

#### C22 `[week1_3] 1주차_3 코드 정리와 전체 PRD 갱신` [채움]
- 남은 임시 코드·`print` 삭제, 파일 첫 줄 주석 갱신
- 프레임 독립 확인 (20 / 60 / 240fps): 경비원 속도, 잡히는 시점, 입력 기억 시간, 해 속도. 2주차 검사(M2 ~ M7)도 다시 돌림
- `00_전체PRD.md`: 기능 상태, 7장 기록. 이 문서 5장 결과 기록
- 확인: 5장 완료 기준 전체 통과, 문서 내용이 실제 결과와 같음

## 5. 완료 기준

PREPRD §11의 기준을 어느 커밋에서 처음 확인할 수 있는지 정리한 표입니다. 최종 확인은 C22에서 전부 다시 합니다.

| 완료 기준 | 커밋 | 결과 |
|---|---|---|
| 착지 0.15초 전에 Space를 누르고 있으면 착지하자마자 차지 | C02 | ⬜ |
| 착지 0.15초 전에 Space를 톡 치면 착지하자마자 낮게 뜀 | C02 | ⬜ |
| 회복·줍기·몸통박치기가 끝나기 직전 Space가 씹히지 않음 | C02 | ⬜ |
| 테이프에 닿기 직전 Shift로 테이프를 주움 | C03 | ⬜ |
| 훨씬 일찍 톡 친 Space는 무시됨 | C02 | ⬜ |
| 땅 위의 Space·Shift는 지금처럼 바로 반응 | C03 | ⬜ |
| 왼쪽으로 걸어 되돌아가고 카메라가 왼쪽으로도 따라옴 | C04 | ⬜ |
| 맵 왼쪽 끝(시작 칸)에서 막힘 | C05 | ⬜ |
| 1초 뒤 경비원이 출발해 도로를 따라 쫓아옴 | C14 | ⬜ |
| 계속 걸으면 거리가 벌어지고, 줍기·추락 멈춤이면 줄어듦 | C14 | ⬜ |
| 지붕 위에서도 가로 거리 90 이하면 잡힘 | C16 | ⬜ |
| 잡히면 1초 멈춘 뒤 처음부터 (점수·해·생명) | C16 | ⬜ |
| 거리 게이지가 거리에 따라 줄고 늚 | C17 | ⬜ |
| 새 타일마다 10분씩 오름 (6칸 = `0일 1시간 0분`) | C09 | ⬜ |
| 뒤로 가거나 떨어져도 점수가 줄지 않음 | C08 | ⬜ |
| 해가 왼쪽 → 오른쪽으로 부드럽게, 건물 뒤에 그려짐 | C12 | ⬜ |
| 60칸째에 `0일 10시간 0분`, 해 오른쪽 끝, 경비원 주저앉음 | C19 | ⬜ |
| 2초 뒤 `저녁, 공원`, 빈터에 허수아비, 생명 유지 | C20 | ⬜ |
| 보스 구간에서 점수가 오르지 않고 경비원·게이지·해가 없음 | C20 | ⬜ |
| G·E·M 디버그 키 동작 | C21 | ⬜ |
| 2주차 기능(발판·추락·멈춤·가속)이 그대로 동작 | C22 | ⬜ |
| 프레임 속도가 달라도 경비원 속도·잡힘 시점·입력 기억 시간이 같음 | C22 | ⬜ |

## 6. 끝난 뒤 정리할 것

- 완료 기준 결과를 위 표에 기록
- 2장 위험 항목의 측정값과 플레이 판단을 기록
- 3주차로 넘길 항목 확인 (PREPRD §13: 물웅덩이·창문·비둘기, 테이프 층별 배치, 진짜 경비원 그림)
