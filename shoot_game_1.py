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

# 게임 객체 정의
class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y):
    super().__init__()
    self.image = pygame.Surface((5, 5))
    self.image.fill(GREEN)
    self.rect = self.image.get_rect()
    self.rect.centerx = x
    self.rect.bottom = y
    self.speed = -20

  def update(self):
    self.rect.y += self.speed
    if self.rect.bottom < 0:
      self.kill()
            
            
class Player(pygame.sprite.Sprite):
  def __init__(self, bullets:pygame.sprite.Group=None):
    super().__init__()
    # self.image = pygame.Surface((30, 30))
    self.image = pygame.image.load('shooter1.png').convert_alpha()
    # self.image.fill(BLUE)
    self.rect = self.image.get_rect()
    self.rect.x = SCREEN_WIDTH // 2
    self.rect.y = SCREEN_HEIGHT - 50
    self.speed = 5
    self.bullets = bullets

  def update(self):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
      self.rect.x -= self.speed
    elif keys[pygame.K_RIGHT]:
      self.rect.x += self.speed
    elif keys[pygame.K_UP]:
      self.rect.top -= self.speed
    elif keys[pygame.K_DOWN]:
      self.rect.top += self.speed

    # 경계 체크
    if self.rect.left < 0:
      self.rect.left = 0
    elif self.rect.right > SCREEN_WIDTH:
      self.rect.right = SCREEN_WIDTH
      
    # 스페이스바 키 입력 체크
    if keys[pygame.K_SPACE]:
      bullet = Bullet(self.rect.centerx, self.rect.top)
      all_sprites.add(bullet)
      bullets.add(bullet)


class Enemy(pygame.sprite.Sprite):
  def __init__(self):
    super().__init__()
    # self.image = pygame.Surface((10, 10))
    # self.image.fill(BLACK)
    self.image = pygame.image.load('enemy1.png').convert_alpha()
    self.rect = self.image.get_rect()
    self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
    self.rect.y = 0
    self.speed = random.randint(3, 5)

  def update(self):
    self.rect.y += self.speed
    if self.rect.top > SCREEN_HEIGHT:
      self.kill()
      
      
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
background = pygame.image.load('background1.jpg')
back_y_pos = -(background.get_rect().height - SCREEN_HEIGHT)
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

back_y_pos = -(background.get_rect().height - SCREEN_HEIGHT)
score = 0
game_over = False
life = 3

running = True
# 게임 루프
while running:
  clock.tick(60)
  # 이벤트 처리
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    
  
  # 배경 스크롤
  back_y_pos += scroll_speed
  if back_y_pos >= 0:
    back_y_pos = 0
    
      
  if game_over:    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
      game_over = False
      score = 0
      life = 3
      back_y_pos = -(background.get_rect().height - SCREEN_HEIGHT)
      
    screen.blit(background, (0, back_y_pos))
    screen.blit(text, (0, 0))
    over = font_over.render("Game Over", True, (255,255,0))
    restart = font.render("Press R to Continue", True, (255,0,0))
    screen.blit(over, ((SCREEN_WIDTH-over.get_rect().width)//2, (SCREEN_HEIGHT-over.get_rect().height)//2))
    screen.blit(restart, ((SCREEN_WIDTH-restart.get_rect().width)//2, (SCREEN_HEIGHT-over.get_rect().height)//2+80))
    screen.blit(text, (0, 0))
    pygame.display.flip()
    continue
    

  # 새로운 적 생성
  if random.randint(1, 100) <= 20:
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

  # 스프라이트 업데이트
  all_sprites.update()
 
  # 충돌 체크
  if pygame.sprite.spritecollide(player, enemies, True):
    back_y_pos = -(background.get_rect().height - SCREEN_HEIGHT)
    for enemy in enemies:
      enemy.kill()
    life -= 1
    if life == 0:
      game_over = True
    
  hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
  for hit in hits:
    hit.kill()
    score += 10
    
  # 점수 출력      
  text = font.render(f"점수 : {score}", 
                    True, # anti-alias
                    (255, 255, 255)) # text color    

  # 화면 그리기
  # screen.fill(BLACK)        
  screen.blit(background, (0, back_y_pos))
  print(back_y_pos)
    
  all_sprites.draw(screen)    
  screen.blit(text, (0, 0))

  pygame.display.flip()
  
  
pygame.quit()
sys.exit()
