import pygame
import random

# 화면 크기 설정
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# 색깔 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 게임 객체 정의
class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y):
    super().__init__()
    self.image = pygame.Surface((5, 5))
    self.image.fill(WHITE)
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
    self.image = pygame.Surface((30, 30))
    self.image.fill(WHITE)
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
    self.image = pygame.Surface((10, 10))
    self.image.fill(RED)
    self.rect = self.image.get_rect()
    self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
    self.rect.y = 0
    self.speed = random.randint(3, 5)

  def update(self):
    self.rect.y += self.speed
    if self.rect.top > SCREEN_HEIGHT:
      self.kill()

# 게임 초기화
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# 스프라이트 그룹 초기화
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# 플레이어 객체 생성
player = Player(bullets)
all_sprites.add(player)

# 게임 루프
running = True
while running:
  clock.tick(60)
  # 이벤트 처리
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  # 새로운 적 생성
  if random.randint(1, 100) <= 20:
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

  # 스프라이트 업데이트
  all_sprites.update()

  # 충돌 체크
  if pygame.sprite.spritecollide(player, enemies, True):
    running = False
  hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
  for hit in hits:
    hit.kill()

  # 화면 그리기
  screen.fill(BLACK)
  all_sprites.draw(screen)
  pygame.display.flip()
