"""
종스크롤 디펜더 슈팅 게임 (pygame 2.x)

[게임 규칙]
- 방향키: 이동 / Space: 발사 / R: 게임오버 후 재시작 / ESC: 종료
- 적이 화면 하단을 통과하거나 아군과 부딪히면 목숨 -1, 라운드 리셋
- 목숨 3개를 모두 잃으면 게임 오버

[코드 구조]
1. 설정값     : 난이도·크기·색 등 "숫자"를 한곳에 모아 조절하기 쉽게 함
2. 에셋 로더  : 파일 경로/로딩 실패 처리를 한곳에서 담당
3. 배경       : 이음새 없는 이미지를 무한 스크롤
4. 스프라이트 : Bullet / Player / Enemy - 각자 "자기 움직임"만 책임짐
5. Game 클래스: 이벤트 → 업데이트 → 그리기 순서의 게임 루프와 규칙(점수·목숨) 담당

[필요 파일] (이 파일과 같은 폴더)
classic_bg_800x1400_seamless.png, shooter1.png, enemy1.png, NanumGothic.ttf
※ 파일이 없어도 대체 도형/기본 폰트로 실행은 됨 (에셋 로더 참고)
"""
import os       # 에셋 파일 경로 계산
import random   # 적의 출현 위치/속도
import sys      # 종료 시 sys.exit()

import pygame


# =====================================================================
# 1. 설정값
#    - 코드 곳곳에 숫자를 직접 쓰면(매직 넘버) 난이도 조절 시 찾기 어렵다.
#    - 대문자 상수로 모아두면 "밸런스 조절 = 이 블록만 수정"이 된다.
#    - 속도 단위는 px/frame 이다. FPS를 60으로 고정하므로 초당 이동량 = 값 × 60
# =====================================================================
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
FPS = 60
TITLE = "Sky Defender"

# 색 (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BULLET_CORE = (255, 240, 150)

# =====================================================================
# 5. Game - 게임 루프와 규칙
# =====================================================================
class Game:
    """
    게임 루프의 기본 형태 (매 프레임 반복)

        handle_events()  : 입력/타이머 이벤트 처리
        update()         : 위치 이동, 충돌, 점수/목숨 계산  ← 한 프레임에 한 번만!
        draw()           : 화면 그리기

    상태(state)를 두어 "플레이 중"과 "게임 오버"의 동작을 분리한다.
    (if game_over: ... continue 방식보다 흐름이 명확하고 상태 추가가 쉬움)
    """

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.running = True

    # ------------------------------------------------------------------
    # 게임 루프
    # ------------------------------------------------------------------
    def run(self) -> None:
        while self.running:
            # tick() 은 직전 프레임 이후 흐른 시간(ms)을 반환 → 난이도용 시간 측정에 사용
            dt = self.clock.tick(FPS)     # 최대 60FPS 로 제한 (px/frame 속도의 기준)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False    # 게임 루프를 빠져나오는 flag, false이면 종료(게임 루프 탈출)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self) -> None:
        pass

    # ------------------------------------------------------------------
    # 그리기 (뒤에 있는 것부터: 배경 → 스프라이트 → UI)
    # ------------------------------------------------------------------
    def draw(self) -> None:
        self.screen.fill(BLACK)

        # 메모리에 그린 화면을 실제 모니터에 한 번에 반영 (더블 버퍼링 → 깜빡임 방지)
        pygame.display.flip()


# =====================================================================
# 실행 진입점
#  - 이 파일을 직접 실행할 때만 게임 시작
#  - 다른 파일에서 import 할 때는 실행되지 않음 (클래스 재사용/테스트 가능)
# =====================================================================
if __name__ == "__main__":
    Game().run()
    sys.exit()