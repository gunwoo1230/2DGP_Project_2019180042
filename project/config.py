# 모든 수치를 한곳에 모음 (초안, 플레이하며 조정)

# 화면
SCREEN_W, SCREEN_H = 1600, 900
PLAY_LEFT, PLAY_RIGHT = 20, 1580        # 플레이 칸 좌우
PLAY_BOTTOM, PLAY_TOP = 110, 810        # 플레이 칸 아래·위
ROAD_Y, LEDGE_Y, ROOF_Y = 210, 390, 570 # 층 높이: 도로, 창틀, 지붕
SPRITE_SCALE = 0.6                      # 스프라이트 그리기 배율

# 맵·카메라
TILE_W = 600                            # 타일 폭
MAP_LEFT = 20                           # 첫 타일 왼쪽 끝 월드 x
CAMERA_FOLLOW_X = 640                   # 박스가 이 화면 x보다 오른쪽이면 카메라가 오른쪽으로
CAMERA_BACK_X = 400                     # 박스가 이 화면 x보다 왼쪽이면 카메라가 왼쪽으로
DRAW_MARGIN = 100                       # 화면 밖 이만큼까지는 그림
FOOT_HALF = 20                          # 발 폭의 절반 (발판 위에 서 있는지 판정)
SNAP = 8                                # 발밑 발판에 붙는 허용 오차(px)
LEDGE_FLOOR_Y = 375                     # 창틀 층 최소 높이 (창틀이 380 ~ 405, 390은 디버그 키 2에만 씀)
FLOOR_YS = (ROAD_Y, LEDGE_FLOOR_Y, ROOF_Y)  # 층 최소 높이
MINUTES_PER_TILE = 10                   # 건물 1칸 = 10분
SUN_LEFT_X, SUN_RIGHT_X, SUN_Y = 80, 1520, 770     # 해 일직선 길 (화면 좌표, 플레이 칸 맨 위)
SUN_SCALE = 0.7                         # 해 그리기 배율
SUN_SPEED = 0.05                        # 그리는 해의 진행률이 따라가는 속도 (초당)
DAY_END_TIME = 2                        # 낮 끝에 경비원 지침을 보여 주는 시간 (초)
WINDOW_W, WINDOW_GAP_MIN = 90, 50       # 창틀 발판 길이(= 창문 폭), 창틀 사이 최소 간격
WINDOW_YS = (380, 385, 390, 395, 400, 405)  # 창틀 높이 후보 (창문마다 따로 고름)
WINDOW_H, WINDOW_INSET = 70, 10         # 임시 창문 그림 높이(창틀 위로), 좌우 안쪽 여백
PIPE_W, PIPE_PEG_W = 16, 60             # 임시 배수관 굵기, 받침 발판 길이
PIPE_PEGS_Y = (300, 390, 480)           # 배수관 받침 높이 (층 중간 · 창틀 층 · 층 중간), 480에서 지붕으로
POLE_X, POLE_TOP = (92, 108), 630      # 임시 전봇대 x 범위(타일 안), 위 끝 (570 못보다 위)
POLE_PEG_X = (70, 130)                  # 전봇대 못 발판 x 범위 (타일 안)
POLE_PEGS_Y = (300, 390, 480, 570)      # 전봇대 못 높이, 570에서 양옆 지붕으로
CLOTHESLINE_CHANCE = 0.3                # 일반 건물 사이 빨랫줄 확률 (accel -> gap 사이는 항상)
LINE_FROM = ('basic', 'pipe', 'accel', 'gap', 'pole')   # 빨랫줄이 시작될 수 있는 앞 타일
LINE_TO = ('basic', 'pipe', 'accel')    # 빨랫줄이 이어질 수 있는 다음 타일 (gap은 항상)
PLATFORM_THICK = {'roof': 20, 'ledge': 12, 'peg': 10, 'accel': 20}  # 임시 그림 두께

# 박스 이동
BOX_START_X = 200                       # 시작 위치
FLOOR_SPEEDS = (310, 330, 350)          # 도로·창틀·지붕 기본 속도 px/s (FLOOR_YS와 같은 순서)
ACCEL_RATE = 1.5                        # 가속 지붕 오른쪽 이동 배율
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
ANIM_FPS_FALL, ANIM_FPS_RECOVER = 10, 7
STUN_PX_PER_SEC = 180                   # 떨어진 높이 180px당 1초 멈춤
DIZZY_FPS, DIZZY_GAP = 6, 18            # 도는 별 속도, 머리 위 간격(px)
INPUT_BUFFER_TIME = 0.15                # 미리 누른 키를 기억하는 시간 (초)

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

# 경비원 (임시 사각형)
GUARD_W, GUARD_H = 90, 170              # 그림 크기
GUARD_START_GAP = 600                   # 시작할 때 박스와의 거리
GUARD_START_DELAY = 1                   # 출발 전 기다리는 시간 (초)
GUARD_SPEED = 280                       # px/s
CATCH_DIST = 90                         # 박스와의 가로 거리가 이 이하면 잡힘
CAUGHT_TIME = 1                         # 잡힌 뒤 멈춤 시간 (초)

# 몸통박치기
SLAM_DIST, SLAM_TIME, SLAM_COOLDOWN = 130, 0.22, 0.5    # px, 초, 초
SLAM_RETURN_TIME, SLAM_BOUNCE_H = 0.25, 16              # 돌아오는 시간(초), 튕김 높이(px, 그림만)
SLAM_SX, SLAM_SY, SLAM_ROT = 1.2, 0.85, 0.15            # 임시 그림 배율, 기울기(rad)

# 허수아비
DUMMY_X, DUMMY_W, DUMMY_H = 1200, 84, 144
DUMMY_HIT_TIME, DUMMY_SHAKE = 0.15, 4   # 초, px
DUMMY_FONT_SIZE, DUMMY_TEXT_GAP = 32, 24    # 맞은 횟수 글자 크기, 머리 위 간격

# 그림일기 화면
UI_LIFE_X, UI_LIFE_GAP, UI_LIFE_Y = 688, 56, 160       # 생명 칸 (바닥 띠 가운데, 5칸 가운데 x 800)
UI_LIFE_EMPTY_ALPHA = 0.25              # 빈 생명 칸 불투명도
UI_HEADER_Y, UI_NOW_X = 856, 868                        # 위쪽 칸 글자 높이, 지금 칸 가운데
UI_DAY_X, UI_HOUR_X, UI_MIN_X = 1218, 1328, 1474        # 도망친 지 칸 숫자 가운데
TIP_INTERVAL, TIP_CHAR_TIME = 6, 0.05   # 팁 바뀌는 간격, 한 글자 써지는 시간 (초)
UI_TIP_X, UI_TIP_Y = 52.5, 54           # 원고지 첫 칸 가운데
MARKER_X, MARKER_Y = 70, 360            # 화면 밖 경비원 표시 가운데 (왼쪽 가운데)
MARKER_SIZE, MARKER_MIN_SCALE, MARKER_FAR = 64, 0.35, 1000  # 기본 크기, 가장 작은 배율, 이 거리부터 가장 작음
MARKER_ARROW_SCALE, MARKER_ARROW_GAP = 0.5, 4   # 화살표 배율, 네모와의 간격(px)
MARKER_BLINK_DIST, MARKER_BLINK_TIME = 200, 0.15    # 이 거리 이하면 깜빡임, 깜빡이는 간격(초)
FRAME_STRIP_W = 27                    # 테두리 덮개 폭
FRAME_STRIP_BOTTOM, FRAME_STRIP_TOP = 100, 820      # 테두리 덮개 위아래
