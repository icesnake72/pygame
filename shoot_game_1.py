import pygame
import random, os, sys


# 화면 크기 설정
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

SCROLL_SPEED = 1

# 색깔 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)

# 게임 객체 정의
class Bullet(pygame.sprite.Sprite):
  W, H = 6, 16          # 세로로 긴 총알 → 진행 방향이 잘 보임
  SPEED = -9            # px/frame (60FPS 기준 초당 540px, 화면 통과 약 0.9초)
  
  def __init__(self, x, y):
    super().__init__()
    super().__init__()
    self.image = pygame.Surface((self.W, self.H), pygame.SRCALPHA)   # 둥근 모서리 밖은 투명
    r = self.image.get_rect()
    pygame.draw.rect(self.image, RED, r, border_radius=3)                     # 바깥 = 테두리
    pygame.draw.rect(self.image, ORANGE, r.inflate(-2, -2), border_radius=2)  # 안쪽 채우기
    pygame.draw.line(self.image, (255, 240, 150), (r.centerx - 1, 3), (r.centerx - 1, r.bottom - 5))  # 밝은 심지
    self.rect = self.image.get_rect(centerx=x, bottom=y)
    self.speed = self.SPEED

  def update(self):
    self.rect.y += self.speed
    if self.rect.bottom < 0:
      self.kill()
            
            
class Player(pygame.sprite.Sprite):
  def __init__(self, bullets:pygame.sprite.Group=None):
    super().__init__()
    # self.image = pygame.Surface((30, 30))
    self.image = pygame.image.load('shooter1.png').convert_alpha()
    self.rect = self.image.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 10)
    self.speed = 5
    self.bullets = bullets
    self.last_shot = 0
    self.shot_delay = 150        # ms, 초당 약 6~7발
    
    # # self.image.fill(BLUE)
    # self.rect = self.image.get_rect()
    # self.rect.x = SCREEN_WIDTH // 2
    # self.rect.y = SCREEN_HEIGHT - 50
    # self.speed = 5
    # self.bullets = bullets

  def update(self):
    keys = pygame.key.get_pressed()
    # elif 대신 합산 → 대각선 이동 가능
    self.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
    self.rect.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed
    # 상하좌우 경계를 한 줄로 처리
    self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    now = pygame.time.get_ticks()
    if keys[pygame.K_SPACE] and now - self.last_shot >= self.shot_delay:
      self.last_shot = now
      bullet = Bullet(self.rect.centerx, self.rect.top)
      all_sprites.add(bullet)
      self.bullets.add(bullet)
    # if keys[pygame.K_LEFT]:
    #   self.rect.x -= self.speed
    # elif keys[pygame.K_RIGHT]:
    #   self.rect.x += self.speed
    # elif keys[pygame.K_UP]:
    #   self.rect.top -= self.speed
    # elif keys[pygame.K_DOWN]:
    #   self.rect.top += self.speed

    # # 경계 체크
    # if self.rect.left < 0:
    #   self.rect.left = 0
    # elif self.rect.right > SCREEN_WIDTH:
    #   self.rect.right = SCREEN_WIDTH
      
    # # 스페이스바 키 입력 체크
    # if keys[pygame.K_SPACE]:
    #   bullet = Bullet(self.rect.centerx, self.rect.top)
    #   all_sprites.add(bullet)
    #   bullets.add(bullet)


class Enemy(pygame.sprite.Sprite):
  SPEED_MIN = 1.0   # px/frame (60FPS 기준 초당 60px)
  SPEED_MAX = 2.0   # px/frame (초당 120px)
  IMAGE = None
  
  def __init__(self):
    super().__init__()
    # self.image = pygame.Surface((10, 10))
    # self.image.fill(BLACK)
    if Enemy.IMAGE is None:
      Enemy.IMAGE = pygame.image.load('enemy1.png').convert_alpha()
      
    
    self.image = Enemy.IMAGE        
    self.image = pygame.image.load('enemy1.png').convert_alpha()
    self.rect = self.image.get_rect()
    self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)   # 이미지 폭 기준으로 화면 안에 생성
    self.rect.bottom = 0                     # 화면 위에서 자연스럽게 등장
    self.y = float(self.rect.y)              # 소수 위치 누적용
    self.speed = random.uniform(self.SPEED_MIN, self.SPEED_MAX)

  def update(self):
    self.y += self.speed
    self.rect.y = round(self.y)              # 정수 rect에는 반올림해서 반영
    
    # 하단 통과시 게임 목적 달성 실패로 처리함(Defender Game성격 융합)
    # if self.rect.top > SCREEN_HEIGHT:
    #   self.kill()
      
      
def init_background(background:pygame.Surface, height:int):
  # 처음엔 이미지 아랫부분이 화면에 보이도록 시작 (% 로 0 ~ bg_h 범위로 정규화)
  return -(background.get_height() - height) % background.get_height()
  
      
# player 생성 이후, 게임 루프 이전에 정의
def reset_round():
  """적·총알 제거 + 플레이어/배경 위치 초기화. 새 배경 위치를 반환"""
  for sprite in list(enemies) + list(bullets):
    sprite.kill()                       # kill()은 all_sprites 등 모든 그룹에서 제거
  player.rect.centerx = SCREEN_WIDTH // 2
  player.rect.bottom = SCREEN_HEIGHT - 10
  return init_background(background, SCREEN_HEIGHT)
  
# 폰트 파일 로딩
# 현재 실행 파일의 경로 추출
current_path = os.path.dirname(sys.argv[0])
print(current_path)

# 절대 경로로 변환
absolute_path = os.path.abspath(current_path)
print(absolute_path)

# 폰트 파일(ttf) Path 구하기 : 
font_filepath = os.path.join(absolute_path, 'NanumGothic.ttf')

# 게임 초기화
pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 배경
# 배경 (convert()로 픽셀 포맷을 화면에 맞추면 blit이 수 배 빨라짐)
background = pygame.image.load(
    os.path.join(absolute_path, 'classic_bg_800x1400_seamless.png')).convert()
bg_h = background.get_height()
back_y_pos = init_background(background, SCREEN_HEIGHT)
scroll_speed = SCROLL_SPEED


# 스프라이트 그룹 초기화
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# 플레이어 객체 생성
player = Player(bullets)
all_sprites.add(player)

font = pygame.font.Font(font_filepath, 16)
font_over = pygame.font.FontType(font_filepath, 50)

score = 0
game_over = False
life = 3

running = True

# pygame.init() / 스프라이트 그룹 생성 이후, 게임 루프 이전에 추가
SPAWN_EVENT = pygame.USEREVENT + 1
SPAWN_INTERVAL = 900          # ms, 클수록 적게 나옴
pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)

# 게임 루프
while running:
  clock.tick(60)
  # 이벤트 처리
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == SPAWN_EVENT and not game_over:
      enemy = Enemy()
      all_sprites.add(enemy)
      enemies.add(enemy)
    
  
  # 배경 스크롤
  back_y_pos = (back_y_pos + scroll_speed) % bg_h
  # if back_y_pos >= 0:
  #   back_y_pos = init_background(background, SCREEN_HEIGHT)
    
      
  if game_over:    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
      game_over = False
      score = 0
      life = 3
      reset_round()
      
    # 배경도 두 장 그려야 게임오버 화면에서 빈틈이 안 생김
    screen.blit(background, (0, back_y_pos))
    screen.blit(background, (0, back_y_pos - bg_h))
    
    screen.blit(text, (0, 0))
    over = font_over.render("Game Over", True, (255,255,0))
    restart = font.render("Press R to Continue", True, (255,0,0))
    screen.blit(over, ((SCREEN_WIDTH-over.get_rect().width)//2, (SCREEN_HEIGHT-over.get_rect().height)//2))
    screen.blit(restart, ((SCREEN_WIDTH-restart.get_rect().width)//2, (SCREEN_HEIGHT-over.get_rect().height)//2+80))
    screen.blit(text, (0, 0))
    pygame.display.flip()
    continue
    

  # 새로운 적 생성  
  # if random.randint(1, 100) <= 10:
  #   enemy = Enemy()
  #   all_sprites.add(enemy)
  #   enemies.add(enemy)

  # 스프라이트 업데이트
  all_sprites.update()
 
  # 충돌 체크
  # 스프라이트 업데이트
  all_sprites.update()

  # 1) 총알 → 적 (먼저 처리)
  hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
  score += 10 * sum(len(v) for v in hits.values())   # 한 총알이 여러 적을 맞춘 경우까지 계산

  # 2) 실패 판정: 아군과 충돌 OR 적이 하단 통과
  crashed = pygame.sprite.spritecollideany(player, enemies)
  escaped = any(e.rect.top > SCREEN_HEIGHT for e in enemies)
  if crashed or escaped:
    life -= 1
    back_y_pos = reset_round()
    if life <= 0:
      game_over = True      
  
    
  # 점수 출력      
    # 점수 출력 (목숨 표시 추가)
  text = font.render(f"점수 : {score}   목숨 : {life}", True, (255, 255, 255))
  # text = font.render(f"점수 : {score}", 
  #                   True, # anti-alias
  #                   (255, 255, 255)) # text color    

  # 화면 그리기
  # screen.fill(BLACK)        
  # screen.blit(background, (0, back_y_pos))
  # 배경 그리기: 원본 + 바로 위에 붙은 복사본
  screen.blit(background, (0, back_y_pos))
  screen.blit(background, (0, back_y_pos - bg_h))
  # print(back_y_pos)
    
  all_sprites.draw(screen)    
  screen.blit(text, (0,  0))

  pygame.display.flip()
  
  
pygame.quit()
sys.exit()
