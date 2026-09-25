"""
종스크롤 디펜더 슈팅 게임 (pygame 2.x)

[게임 규칙]
  - 방향키: 이동 / Space: 발사 / R: 게임오버 후 재시작 / ESC: 종료
  - 적이 화면 하단을 통과하거나 아군과 부딪히면 목숨 -1, 라운드 리셋
  - 목숨 3개를 모두 잃으면 게임 오버

[코드 구조]
  1. 설정값        : 난이도·크기·색 등 "숫자"를 한곳에 모아 조절하기 쉽게 함
  2. 에셋 로더     : 파일 경로/로딩 실패 처리를 한곳에서 담당
  3. 배경          : 이음새 없는 이미지를 무한 스크롤
  4. 스프라이트    : Bullet / Player / Enemy - 각자 "자기 움직임"만 책임짐
  5. Game 클래스   : 이벤트 → 업데이트 → 그리기 순서의 게임 루프와 규칙(점수·목숨) 담당

[필요 파일] (이 파일과 같은 폴더)
  classic_bg_800x1400_seamless.png, shooter1.png, enemy1.png, NanumGothic.ttf
  ※ 파일이 없어도 대체 도형/기본 폰트로 실행은 됨 (에셋 로더 참고)
"""
import os
import random
import sys

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

# 게임 규칙
START_LIFE = 3
SCORE_PER_KILL = 10

# 배경
SCROLL_SPEED = 1                  # 배경 스크롤 속도 (초당 60px)

# 플레이어
PLAYER_SPEED = 5                  # 초당 300px
PLAYER_BOTTOM_MARGIN = 10         # 시작 위치: 화면 하단에서 띄울 거리
SHOT_DELAY_MS = 100               # 발사 간격(ms). 작을수록 연사가 빨라짐

# 총알
BULLET_SIZE = (6, 16)             # 세로로 길게 → 진행 방향이 눈에 잘 띔
BULLET_SPEED = -9                 # 음수 = 위로 이동. |속도| <= 총알 길이(16)여야 끊겨 보이지 않음

# 적
ENEMY_SPEED_RANGE = (1.0, 2.0)    # 소수 속도 → Enemy에서 float 좌표로 누적 처리
SPAWN_INTERVAL_MS = 900           # 적 생성 간격(ms). 클수록 적게 나옴 (레벨 1 기준)

# 폭발 효과 (단일 이미지를 "확대 + 페이드아웃" 으로 애니메이션)
EXPLOSION_FRAMES = 12             # 지속 프레임 수 (60FPS 기준 0.2초)
EXPLOSION_SCALE_RANGE = (0.6, 1.6)  # 적 크기 대비 시작/끝 배율

# 난이도 (시간 경과에 따라 단계적으로 상승)
#  - 연속적으로 올리지 않고 "레벨" 단위로 올리는 이유:
#    1) 적 생성 타이머는 set_timer 를 다시 호출할 때마다 카운트가 리셋되므로 매 프레임 바꿀 수 없음
#    2) 플레이어가 "어려워졌다"는 것을 인지할 수 있음 (LEVEL UP 표시)
#  - 반드시 상한(MIN/CAP)을 둔다. 무한히 오르면 어느 순간 클리어 불가능한 게임이 됨
LEVEL_UP_MS = 20_000              # 20초마다 레벨 +1
MAX_LEVEL = 10
SPAWN_STEP_MS = 60                # 레벨당 생성 간격 감소량
SPAWN_INTERVAL_MIN_MS = 400       # 생성 간격 하한
ENEMY_SPEED_STEP = 0.15           # 레벨당 적 속도 증가량 (px/frame)
ENEMY_SPEED_CAP = 3.5             # 적 속도 상한
LEVEL_MSG_MS = 1500               # LEVEL UP 문구 표시 시간

# 색 (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
BULLET_CORE = (255, 240, 150)

# 에셋 파일명
BG_FILE = "classic_bg_800x1400_seamless.png"
PLAYER_FILE = "shooter1.png"
ENEMY_FILE = "enemy1.png"
EXPLOSION_FILE = "explosion.png"
FONT_FILE = "NanumGothic.ttf"


# =====================================================================
# 2. 에셋 로더
# =====================================================================
# 이 .py 파일이 있는 폴더를 기준으로 경로를 만든다.
#  - sys.argv[0]은 IDE 실행/모듈 import 시 빈 문자열이 될 수 있어 불안정하다.
#  - __file__ 은 항상 "현재 소스 파일" 경로이므로 어디서 실행해도 같은 결과가 나온다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(filename: str) -> str:
    """에셋 파일의 절대 경로를 반환 (실행 위치와 무관하게 동일)"""
    return os.path.join(BASE_DIR, filename)


def load_image(filename: str, alpha: bool = True,
               fallback_size=(40, 40), fallback_color=WHITE,
               pointing_up: bool = True, fallback_shape: str = "triangle") -> pygame.Surface:
    """
    이미지를 불러와 화면 픽셀 포맷으로 변환해 반환한다.

    - convert()       : 불투명 이미지(배경)용. blit 속도가 수 배 빨라진다.
    - convert_alpha() : 투명 영역이 있는 이미지(비행기)용.
    - 파일이 없으면 삼각형 대체 이미지를 만들어 게임이 멈추지 않게 한다.
      (수업 중 파일 누락으로 실습이 중단되는 상황 방지)

    ※ convert 계열은 display.set_mode() 이후에만 호출할 수 있다.
    """
    path = asset_path(filename)
    try:
        image = pygame.image.load(path)
    except (FileNotFoundError, pygame.error):
        print(f"[경고] 이미지 파일 없음: {path} → 대체 도형 사용")
        w, h = fallback_size
        image = pygame.Surface((w, h), pygame.SRCALPHA)
        if fallback_shape == "circle":
            pygame.draw.circle(image, fallback_color, (w // 2, h // 2), min(w, h) // 2)
        else:
            points = [(w // 2, 0), (0, h), (w, h)] if pointing_up else [(0, 0), (w, 0), (w // 2, h)]
            pygame.draw.polygon(image, fallback_color, points)
        return image
    return image.convert_alpha() if alpha else image.convert()


def load_font(size: int) -> pygame.font.Font:
    """한글 폰트를 불러오고, 없으면 pygame 기본 폰트로 대체 (한글은 깨질 수 있음)"""
    try:
        return pygame.font.Font(asset_path(FONT_FILE), size)
    except (FileNotFoundError, OSError):
        print(f"[경고] 폰트 파일 없음: {asset_path(FONT_FILE)} → 기본 폰트 사용")
        return pygame.font.Font(None, size)


# =====================================================================
# 3. 배경 - 이음새 없는 이미지 무한 스크롤
# =====================================================================
class ScrollingBackground:
    """
    [원리]
      위아래가 이어지는 이미지는 "이미지 top 위에 같은 이미지가 또 붙어 있을 때"
      경계가 보이지 않는다. 그래서 위치(offset)를 이미지 높이로 나눈 나머지로
      순환시키고, 원본 위쪽에 복사본을 이어 그린다.

          ┌────────┐ ← offset - 높이   (복사본)
          │ 화면   │
          │────────│ ← offset          (원본)
          └────────┘

      기존 방식처럼 끝에서 "처음 위치로 순간이동"시키면 보이는 영역이
      한 번에 바뀌어 끊겨 보인다.
    """

    def __init__(self, image: pygame.Surface, screen_height: int, speed: float):
        self.image = image
        self.height = image.get_height()
        self.screen_height = screen_height
        self.speed = speed
        self.offset = 0.0
        self.reset()

    def reset(self) -> None:
        """이미지 아랫부분이 화면에 보이는 위치에서 시작 (0 <= offset < 높이 로 정규화)"""
        self.offset = -(self.height - self.screen_height) % self.height

    def update(self) -> None:
        # 모듈로(%) 연산 → 값이 계속 커지지 않고 항상 [0, 높이) 범위에서 순환
        self.offset = (self.offset + self.speed) % self.height

    def draw(self, surface: pygame.Surface) -> None:
        # 한 장 위(복사본)부터 화면 아래 끝까지 필요한 만큼 이어 그린다.
        # 화면이 이미지보다 높아져도 빈틈이 생기지 않도록 while 사용
        y = int(self.offset) - self.height
        while y < self.screen_height:
            surface.blit(self.image, (0, y))
            y += self.height


# =====================================================================
# 4. 스프라이트
#    - pygame.sprite.Sprite 를 상속하면 image/rect 만 준비해도
#      Group.update() / Group.draw() / 충돌 함수를 그대로 쓸 수 있다.
#    - Sprite.__init__(*groups) 에 그룹을 넘기면 생성과 동시에 그룹에 등록된다.
# =====================================================================
class Bullet(pygame.sprite.Sprite):
    """아군 총알: 위로 직진하고 화면 밖으로 나가면 스스로 제거"""

    _image_cache = None   # 모든 총알이 같은 모양 → 한 번만 그려서 공유 (매 발사마다 그리면 낭비)

    @classmethod
    def _get_image(cls) -> pygame.Surface:
        if cls._image_cache is None:
            w, h = BULLET_SIZE
            img = pygame.Surface((w, h), pygame.SRCALPHA)       # 둥근 모서리 바깥은 투명
            r = img.get_rect()
            pygame.draw.rect(img, RED, r, border_radius=3)                      # 바깥 = 테두리 색
            pygame.draw.rect(img, ORANGE, r.inflate(-2, -2), border_radius=2)   # 안쪽 채우기
            pygame.draw.line(img, BULLET_CORE,                                  # 밝은 심지 → 시인성 향상
                             (r.centerx - 1, 3), (r.centerx - 1, r.bottom - 5))
            cls._image_cache = img
        return cls._image_cache

    def __init__(self, x: int, y: int, *groups):
        super().__init__(*groups)                 # 생성과 동시에 넘겨받은 그룹들에 등록
        self.image = self._get_image()
        self.rect = self.image.get_rect(centerx=x, bottom=y)   # 비행기 코끝에서 발사
        self.speed = BULLET_SPEED

    def update(self) -> None:
        self.rect.y += self.speed
        # 화면 위로 완전히 벗어나면 제거 → 안 지우면 보이지 않는 총알이 계속 쌓여 느려짐
        if self.rect.bottom < 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    """아군 비행기: 키 입력으로 이동/발사"""

    def __init__(self, image: pygame.Surface, bullet_groups: tuple):
        super().__init__()
        self.image = image
        # mask: 투명 부분을 제외한 실제 모양 → 충돌 판정을 사각형보다 정확하게
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.speed = PLAYER_SPEED
        # 총알을 어떤 그룹에 넣을지 외부에서 주입받는다.
        # (전역 변수 all_sprites/bullets 에 직접 접근하지 않음 → 클래스가 독립적)
        self.bullet_groups = bullet_groups
        self.last_shot = 0
        self.screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.reset_position()

    def reset_position(self) -> None:
        """화면 하단 중앙으로 이동 (게임 시작/라운드 리셋 시 사용)"""
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - PLAYER_BOTTOM_MARGIN
        self.last_shot = 0

    def update(self) -> None:
        keys = pygame.key.get_pressed()

        # True/False 는 1/0 으로 계산된다 → (오른쪽 - 왼쪽) = -1, 0, 1
        # if/elif 로 처리하면 한 번에 한 방향만 되지만, 합산하면 대각선 이동이 가능
        self.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        self.rect.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed

        # clamp_ip: rect 를 지정 영역 안으로 밀어 넣음 (상하좌우 경계 체크를 한 줄로)
        self.rect.clamp_ip(self.screen_rect)

        if keys[pygame.K_SPACE]:
            self.shoot()

    def shoot(self) -> None:
        # 발사 쿨타임: 마지막 발사 후 SHOT_DELAY_MS 가 지나야 다시 발사
        # (없으면 키를 누르고 있는 동안 매 프레임 = 초당 60발 발사)
        now = pygame.time.get_ticks()
        if now - self.last_shot >= SHOT_DELAY_MS:
            self.last_shot = now
            Bullet(self.rect.centerx, self.rect.top, *self.bullet_groups)


class Enemy(pygame.sprite.Sprite):
    """적 비행기: 위에서 아래로 내려옴. 하단 통과 판정은 Game 이 담당"""

    def __init__(self, image: pygame.Surface, mask: pygame.mask.Mask, *groups,
                 speed_range=ENEMY_SPEED_RANGE):
        # speed_range 는 *groups 뒤에 있으므로 반드시 키워드로 전달해야 한다 (위치 인자와 혼동 방지)
        super().__init__(*groups)
        # 이미지/마스크는 Game 에서 한 번만 로드해서 모든 적이 공유
        # (적을 만들 때마다 파일을 읽으면 디스크 접근으로 프레임 드랍 발생)
        self.image = image
        self.mask = mask
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)  # 이미지 폭만큼 빼야 화면 안에 생성
        self.rect.bottom = 0                     # 화면 바로 위에서 시작 → 갑자기 튀어나오지 않음

        # rect 좌표는 정수만 저장된다. rect.y += 1.5 를 하면 소수점이 버려지므로
        # 실제 위치는 float 로 따로 누적하고, 그릴 때만 rect 에 반영한다.
        self.y = float(self.rect.y)
        self.speed = random.uniform(*speed_range)   # 현재 레벨의 속도 범위 적용

    def update(self) -> None:
        self.y += self.speed
        self.rect.y = round(self.y)
        # 여기서 화면 밖 kill() 을 하지 않는다.
        # → 스스로 사라지면 Game 이 "하단 통과"를 감지할 수 없기 때문



class Explosion(pygame.sprite.Sprite):
    """
    적 격추 위치에 잠깐 나타났다 사라지는 효과.
    - 이동/충돌에 관여하지 않고 "프레임 리스트를 순서대로 보여주는" 역할만 한다.
    - 프레임(확대 + 투명도 변화)은 build_frames() 로 한 번만 만들어 모든 폭발이 공유한다.
      (매 프레임 transform.scale 을 호출하면 폭발이 몇 개만 겹쳐도 프레임 드랍이 생긴다)
    """

    @staticmethod
    def build_frames(image: pygame.Surface, base_size: int,
                     count: int = EXPLOSION_FRAMES,
                     scale_range: tuple = EXPLOSION_SCALE_RANGE) -> list:
        if count < 1:
            raise ValueError(f"count must be >= 1, got {count}")
        start, end = scale_range
        frames = []
        for i in range(count):
            t = i / max(count - 1, 1)                        # 0.0 → 1.0 진행률
            size = max(1, int(base_size * (start + (end - start) * t)))
            frame = pygame.transform.smoothscale(image, (size, size))
            frame.set_alpha(int(255 * (1.0 - t)))            # 점점 투명해짐
            frames.append(frame)
        return frames

    def __init__(self, frames: list, center: tuple, *groups):
        super().__init__(*groups)
        if not frames:
            raise ValueError("frames must not be empty")
        self.frames = frames
        self.frame_index = 0
        self.center = center
        self.image = frames[0]
        self.rect = self.image.get_rect(center=center)

    def update(self) -> None:
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.kill()                                      # 마지막 프레임 뒤에는 스스로 제거
            return
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=self.center)  # 크기가 바뀌어도 중심 고정


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

    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # ── 에셋 로드 (set_mode 이후여야 convert 가능) ──
        self.background = ScrollingBackground(
            load_image(BG_FILE, alpha=False, fallback_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
                       fallback_color=(40, 90, 50)),
            SCREEN_HEIGHT, SCROLL_SPEED)
        player_img = load_image(PLAYER_FILE, fallback_color=(80, 160, 255))
        self.enemy_img = load_image(ENEMY_FILE, fallback_color=(200, 40, 40), pointing_up=False)
        self.enemy_mask = pygame.mask.from_surface(self.enemy_img)
        explosion_img = load_image(EXPLOSION_FILE, fallback_size=(45, 45),
                                   fallback_color=ORANGE, fallback_shape="circle")
        self.explosion_frames = Explosion.build_frames(
            explosion_img, max(self.enemy_img.get_size()))

        self.font = load_font(16)
        self.font_big = load_font(50)

        # 게임오버 화면용 반투명 오버레이 (매 프레임 새로 만들지 않도록 미리 생성)
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 140))

        # ── 스프라이트 그룹 ──
        # all_sprites : 업데이트/그리기용 전체 묶음
        # enemies/bullets : 충돌 판정용 분류
        # effects : 폭발 등 연출 전용 (충돌 판정에서 제외)
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()

        self.player = Player(player_img, bullet_groups=(self.all_sprites, self.bullets))
        self.all_sprites.add(self.player)

        # ── 적 생성 타이머 ──
        # 매 프레임 확률로 생성하면 FPS 에 따라 생성량이 달라진다.
        # 타이머 이벤트는 실제 시간 기준으로 일정 간격마다 발생한다.
        # 실제 간격 설정(set_timer)은 레벨에 따라 apply_difficulty() 에서 한다.
        self.SPAWN_EVENT = pygame.USEREVENT + 1

        self.running = True
        self.new_game()

    # ------------------------------------------------------------------
    # 게임 상태 관리
    # ------------------------------------------------------------------
    def new_game(self) -> None:
        """점수·목숨까지 전부 초기화 (처음 시작, R 재시작)"""
        self.score = 0
        self.life = START_LIFE
        self.state = self.STATE_PLAYING
        # 난이도: 새 게임에서만 초기화 (목숨을 잃어도 레벨은 유지 → 긴장감 유지)
        self.play_ms = 0              # 실제 "플레이한" 시간 (게임오버 중에는 증가하지 않음)
        self.level = 1
        self.level_msg_until = 0
        self.apply_difficulty()
        self.reset_round()

    def reset_round(self) -> None:
        """
        목숨을 잃었을 때의 리셋: 적·총알 제거 + 위치 초기화.
        점수와 목숨은 유지한다. (new_game 과 역할 분리)
        """
        # 그룹을 순회하면서 kill() 하면 순회 중 그룹이 변경되므로 list() 로 복사 후 처리
        # kill() 은 스프라이트가 속한 "모든" 그룹(all_sprites 포함)에서 제거한다.
        for sprite in list(self.enemies) + list(self.bullets) + list(self.effects):
            sprite.kill()
        self.player.reset_position()
        self.background.reset()

    def lose_life(self) -> None:
        self.life -= 1
        self.reset_round()
        if self.life <= 0:
            self.state = self.STATE_GAME_OVER

    def spawn_enemy(self) -> None:
        Enemy(self.enemy_img, self.enemy_mask, self.all_sprites, self.enemies,
              speed_range=self.enemy_speed_range)

    def spawn_explosion(self, center: tuple) -> None:
        Explosion(self.explosion_frames, center, self.all_sprites, self.effects)

    # ------------------------------------------------------------------
    # 난이도
    # ------------------------------------------------------------------
    def apply_difficulty(self) -> None:
        """현재 레벨에 맞춰 생성 간격/적 속도를 계산하고 타이머에 반영"""
        step = self.level - 1                       # 레벨 1 = 기본값

        # 생성 간격: 레벨마다 줄이되 하한 아래로는 내려가지 않음
        self.spawn_interval = max(SPAWN_INTERVAL_MIN_MS,
                                  SPAWN_INTERVAL_MS - step * SPAWN_STEP_MS)

        # 적 속도: 범위 전체를 위로 이동시키되 상한으로 제한
        lo, hi = ENEMY_SPEED_RANGE
        bonus = step * ENEMY_SPEED_STEP
        self.enemy_speed_range = (min(lo + bonus, ENEMY_SPEED_CAP),
                                  min(hi + bonus, ENEMY_SPEED_CAP))

        # set_timer 를 다시 호출하면 기존 타이머를 대체 (레벨이 바뀔 때만 호출)
        pygame.time.set_timer(self.SPAWN_EVENT, self.spawn_interval)

    def update_difficulty(self, dt: int) -> None:
        """플레이 시간을 누적하고, 레벨 경계를 넘으면 난이도 재계산"""
        self.play_ms += dt
        new_level = min(MAX_LEVEL, 1 + self.play_ms // LEVEL_UP_MS)
        if new_level != self.level:
            self.level = new_level
            self.apply_difficulty()
            self.level_msg_until = pygame.time.get_ticks() + LEVEL_MSG_MS

    # ------------------------------------------------------------------
    # 게임 루프
    # ------------------------------------------------------------------
    def run(self) -> None:
        while self.running:
            # tick() 은 직전 프레임 이후 흐른 시간(ms)을 반환 → 난이도용 시간 측정에 사용
            dt = self.clock.tick(FPS)     # 최대 60FPS 로 제한 (px/frame 속도의 기준)
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False    # 게임 루프를 빠져나오는 flag, false이면 종료(게임 루프 탈출)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # KEYDOWN 은 "눌린 순간" 한 번만 발생 → 키를 누르고 있어도 재시작이 중복되지 않음
                elif event.key == pygame.K_r and self.state == self.STATE_GAME_OVER:
                    self.new_game()

            # 게임오버 중에는 타이머가 울려도 적을 만들지 않음
            elif event.type == self.SPAWN_EVENT and self.state == self.STATE_PLAYING:
                self.spawn_enemy()

    def update(self, dt: int = 1000 // FPS) -> None:
        self.background.update()          # 게임오버 화면에서도 배경은 계속 흐르게

        if self.state != self.STATE_PLAYING:
            return                        # 게임오버 중에는 플레이 시간도 멈춤

        self.update_difficulty(dt)

        # 모든 스프라이트의 update() 를 호출 - 반드시 프레임당 1회
        # (2번 호출하면 모든 객체가 2배 속도로 움직인다)
        self.all_sprites.update()
        self.check_collisions()

    def check_collisions(self) -> None:
        # 1) 총알 ↔ 적 : 먼저 처리해야 같은 프레임에 격추된 적이 "통과/충돌"로 잡히지 않음
        #    groupcollide(A, B, A삭제여부, B삭제여부) → {총알: [맞은 적 목록]}
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, True, True)
        killed = 0
        for enemies in hits.values():                # 한 총알이 여러 적을 맞춘 경우 포함
            for enemy in enemies:
                self.spawn_explosion(enemy.rect.center)   # 격추된 자리에 폭발 연출
                killed += 1
        self.score += killed * SCORE_PER_KILL

        # 2) 아군 ↔ 적 : collide_mask 로 실제 모양끼리 비교 (투명 모서리 스침은 무시)
        #    spritecollideany 는 첫 충돌만 찾으면 바로 반환 → 리스트를 만드는 spritecollide 보다 가벼움
        crashed = pygame.sprite.spritecollideany(
            self.player, self.enemies, pygame.sprite.collide_mask) # pyright: ignore[reportArgumentType]

        # 3) 적 하단 통과 : 디펜더 규칙 - 한 대라도 놓치면 실패
        escaped = any(enemy.rect.top > SCREEN_HEIGHT for enemy in self.enemies)

        if crashed or escaped:
            self.lose_life()

    # ------------------------------------------------------------------
    # 그리기 (뒤에 있는 것부터: 배경 → 스프라이트 → UI)
    # ------------------------------------------------------------------
    def draw(self) -> None:
        self.background.draw(self.screen)

        if self.state == self.STATE_PLAYING:
            self.all_sprites.draw(self.screen)

        self.draw_hud()

        if self.state == self.STATE_GAME_OVER:
            self.draw_game_over()

        # 메모리에 그린 화면을 실제 모니터에 한 번에 반영 (더블 버퍼링 → 깜빡임 방지)
        pygame.display.flip()

    def draw_text(self, font: pygame.font.Font, text: str, color, **pos) -> None:
        """
        그림자 있는 텍스트 출력. 밝은 배경 위에서도 글자가 잘 보이게 한다.
        pos 예) topleft=(10, 5), center=(320, 240)
        """
        shadow = font.render(text, True, BLACK)        # True = 안티앨리어싱(부드러운 글자)
        label = font.render(text, True, color)
        rect = label.get_rect(**pos)
        self.screen.blit(shadow, rect.move(2, 2))
        self.screen.blit(label, rect)

    def draw_hud(self) -> None:
        self.draw_text(self.font, f"점수 : {self.score}", WHITE, topleft=(10, 8))
        self.draw_text(self.font, f"목숨 : {self.life}", WHITE,
                       topright=(SCREEN_WIDTH - 10, 8))
        self.draw_text(self.font, f"LEVEL {self.level}", YELLOW, midtop=(SCREEN_WIDTH // 2, 8))

        # 레벨이 오른 직전 일정 시간 동안만 안내 문구 표시
        if self.state == self.STATE_PLAYING and pygame.time.get_ticks() < self.level_msg_until:
            self.draw_text(self.font_big, "LEVEL UP!", YELLOW,
                           center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            
        # 실제 FPS 표시 (디버깅용) - 화면 왼쪽 아래
        self.draw_text(self.font, f"FPS {self.clock.get_fps():.0f}", WHITE,
                       bottomleft=(10, SCREEN_HEIGHT - 8))

    def draw_game_over(self) -> None:
        self.screen.blit(self.overlay, (0, 0))
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.draw_text(self.font_big, "Game Over", YELLOW, center=(cx, cy - 20))
        self.draw_text(self.font, f"최종 점수 : {self.score}", WHITE, center=(cx, cy + 30))
        self.draw_text(self.font, "Press R to Continue", RED, center=(cx, cy + 60))


# =====================================================================
# 실행 진입점
#  - 이 파일을 직접 실행할 때만 게임 시작
#  - 다른 파일에서 import 할 때는 실행되지 않음 (클래스 재사용/테스트 가능)
# =====================================================================
if __name__ == "__main__":
    Game().run()
    sys.exit()