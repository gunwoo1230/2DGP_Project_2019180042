# 맵 = 타일 이름 순서 목록

TEST_MAP = ['start', 'basic', 'pipe', 'basic', 'accel', 'gap', 'pole', 'basic', 'accel', 'gap', 'basic']

# 낮 맵: 건물 1칸 = 10분, 60칸 = 10시간 + 시작 칸 (gap은 항상 accel 바로 뒤)
DAY_PATTERN = ['basic', 'pipe', 'accel', 'gap', 'basic', 'pole']
DAY_MAP = ['start'] + DAY_PATTERN * 10          # 61칸, 마지막 칸 번호 = 60
BOSS_ARENA = ['start', 'start', 'start']        # 임시 보스 무대 (빈터)
