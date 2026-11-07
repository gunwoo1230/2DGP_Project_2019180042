# 모든 수치를 한곳에 모음 (초안, 플레이하며 조정)

# 화면
SCREEN_W, SCREEN_H = 1600, 900
PLAY_LEFT, PLAY_RIGHT = 20, 1580        # 플레이 칸 좌우
PLAY_BOTTOM, PLAY_TOP = 110, 810        # 플레이 칸 아래·위
GROUND_Y = 210                          # 테스트 바닥 (도로 높이)
SPRITE_SCALE = 0.6                      # 스프라이트 그리기 배율

# 박스 이동
BOX_START_X = 200                       # 시작 위치
WALK_SPEED = 310                        # px/s
HOP_HEIGHT = 10                         # 걷기 깡충 높이(그림만)
CHARGE_MAX_TIME = 0.6                   # 초
CHARGE_SPEED_RATE = 0.4                 # 차지 중 이동 속도 배율
CHARGE_SQUASH_X, CHARGE_SQUASH_Y = 0.20, 0.25   # 최대 차지 때 가로로 늘고 세로로 주는 비율
JUMP_MIN_H, JUMP_MAX_H = 48, 150        # px
JUMP_APEX_VY = 120                      # 상승 중 vy가 이 값 이하면 정점 그림 시작 (px/s)
GRAVITY = 2400                          # px/s²
AIR_ACCEL = 1080                        # px/s²
BOX_BB_W, BOX_BB_H = 86, 66             # 충돌 박스
BOX_BODY_H = 81                         # 화면에 그려지는 몸통 높이
ANIM_FPS_IDLE, ANIM_FPS_MOVE = 7, 10    # 애니메이션 속도

# 테이프
TAPE_START, TAPE_MAX = 1, 5             # 생명
TAPE_PICKUP_TIME = 0.5                  # 초
TAPE_XS = (500, 900, 1300)              # 바닥 테이프 위치
TAPE_BB_RATE = 0.8                      # 충돌 박스 = 그림 크기의 80%
TAPE_BOB_H, TAPE_BOB_TIME = 4, 1        # 둥실 진폭(px), 주기(초)

# 줍기 연출
FX_RISE_TIME, FX_SPARKLE_TIME, FX_FLY_TIME = 0.25, 0.25, 0.35   # 초
FX_RISE_H, FX_SPARKLE_FPS = 60, 8       # 머리 위 높이(px), 반짝임 속도
FX_END_SCALE = 0.37                     # 생명 칸에 도착할 때 배율

# 몸통박치기
SLAM_DIST, SLAM_TIME, SLAM_COOLDOWN = 130, 0.22, 0.5    # px, 초, 초
SLAM_RETURN_TIME, SLAM_BOUNCE_H = 0.25, 16              # 돌아오는 시간(초), 튕김 높이(px, 그림만)
SLAM_SX, SLAM_SY, SLAM_ROT = 1.2, 0.85, 0.15            # 임시 그림 배율, 기울기(rad)

# 허수아비
DUMMY_X, DUMMY_W, DUMMY_H = 1200, 84, 144
DUMMY_HIT_TIME, DUMMY_SHAKE = 0.15, 4   # 초, px
DUMMY_FONT_SIZE, DUMMY_TEXT_GAP = 32, 24    # 맞은 횟수 글자 크기, 머리 위 간격

# 그림일기 화면
UI_LIFE_X, UI_LIFE_GAP, UI_LIFE_Y = 60, 56, 772         # 생명 칸
UI_LIFE_EMPTY_ALPHA = 0.25              # 빈 생명 칸 불투명도
UI_HEADER_Y, UI_NOW_X = 856, 868                        # 위쪽 칸 글자 높이, 지금 칸 가운데
UI_DAY_X, UI_HOUR_X, UI_MIN_X = 1218, 1328, 1474        # 도망친 지 칸 숫자 가운데
TIP_INTERVAL, TIP_CHAR_TIME = 6, 0.05   # 팁 바뀌는 간격, 한 글자 써지는 시간 (초)
UI_TIP_X, UI_TIP_Y = 52.5, 54           # 원고지 첫 칸 가운데
FRAME_STRIP_W = 27                      # 테두리 덮개 폭
FRAME_STRIP_BOTTOM, FRAME_STRIP_TOP = 100, 820      # 테두리 덮개 위아래
