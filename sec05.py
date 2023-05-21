from typing import Any
import pygame


# Pygame 초기화
pygame.init()

# 화면 크기 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Jumping Character Example")

# 주인공 캐릭터 클래스 정의
class Character(pygame.sprite.Sprite):
  def __init__(self, x, y):
      super().__init__()
      self.image = pygame.Surface((50, 50))
      self.image.fill((255, 0, 0))  # 빨간색
      self.rect = self.image.get_rect()
      self.rect.x = x
      self.rect.y = y
      self.velocity_y = 0
      self.is_jumping = False
      self.jump_power = -20
      self.gravity = 0.5
      self.spaceKeyPressed = False
      

  def update(self):
    # 키 입력 처리
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
      self.rect.x -= 3          
      
    if keys[pygame.K_RIGHT]:
      self.rect.x += 3          
      
    # for key, pressed in enumerate(keys):
    #   if pressed:
    #     print(f"Key {pygame.key.name(key)} is pressed")
      
    if keys[pygame.K_SPACE] and not self.is_jumping and not self.spaceKeyPressed:# and self.isJumpable:
      self.is_jumping = True
      self.spaceKeyPressed = True
      self.velocity_y = self.jump_power 

    # 중력 적용
    self.velocity_y += self.gravity
    self.rect.y += self.velocity_y
    self.is_jumping = True
    
    print(self.rect.y)

    # 바닥 충돌 체크
    if self.rect.bottom >= screen_height:
      self.rect.bottom = screen_height
      self.velocity_y = 0
      self.is_jumping = False
      # self.isJumpable = True
        
    # 장애물과 충돌 체크
    hits = pygame.sprite.spritecollide(self, obstacles, False)
    if len(hits):      
      for hit in hits:
        if self.velocity_y > 0:   # 내려오는 중이면...
          self.rect.y = hit.rect.top - self.rect.height
          self.velocity_y = 0
          self.is_jumping = False
          # self.isJumpable = True
        
    if self.rect.left < 0:
      self.rect.left = 0
      
    if self.rect.right > screen_width:
      self.rect.right = screen_width
      
    
      
    # self.last_key = keys # pygame.key.get_pressed()
    
  def checkJumpOver(self, event):
    if event.type == pygame.KEYUP and self.spaceKeyPressed:
      self.spaceKeyPressed = False
      # self.last_key = pygame.key.name(event.key)
      # self.last_key = pygame.key.get_pressed()
      
      # print(self.last_key)
          
# 장애물 클래스 정의
class Obstacle(pygame.sprite.Sprite):
  def __init__(self, x, y, width, height):
      super().__init__()
      self.image = pygame.Surface((width, height))
      self.image.fill((0, 0, 255))  # 파란색
      self.rect = self.image.get_rect()
      self.rect.x = x
      self.rect.y = y
      
      
class Enemy(pygame.sprite.Sprite):
  def __init__(self, x, y, width, height) -> None:
    super().__init__()
    self.image = pygame.Surface((width, height))
    self.image.fill((0, 255, 0))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    
  def update(self) -> None:
    pass
  
  
class EnemyLv1(pygame.sprite.Sprite):
  def __init__(self, x, y, width, height) -> None:
    super().__init__()
    self.image = pygame.Surface((width, height))
    self.image.fill((0, 255, 0))
    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y
    self.speed = 5
    
  def update(self) -> None:
    self.rect.left += self.speed
    
    if self.rect.left <= 0 or self.rect.right >= screen_width:
      self.speed = -self.speed
      

      
    
# 그라디언트 함수
def create_gradient(start_color, end_color, width, height):
  gradient = pygame.Surface((width, height))
  
  for y in range(height):
    r = start_color[0] + (end_color[0] - start_color[0]) * y / height
    g = start_color[1] + (end_color[1] - start_color[1]) * y / height
    b = start_color[2] + (end_color[2] - start_color[2]) * y / height
    line_color = (r, g, b)
    print(line_color)
    pygame.draw.line(gradient, line_color, (0, y), (width, y))
    
  return gradient
  
          


# 배경 스크롤 속도 설정
background_scroll_speed = -3

# 주인공 캐릭터 생성
character = Character(100, 100)
enemy = EnemyLv1(400, screen_height-50, 50, 50)

# 장애물 생성
obstacle = Obstacle(300, 300, 100, 20)

# 스프라이트 그룹 생성
all_sprites = pygame.sprite.Group()

# 장애물 그룹 생성
obstacles = pygame.sprite.Group()
obstacles.add(obstacle)

# enemy group 생성
enemies = pygame.sprite.Group()
enemies.add(enemy)

all_sprites.add(character, obstacle, enemy)

# 배경 그라디언트 생성
start_color = (0, 0, 255)  # 시작 색상 (파란색)
end_color = (255, 255, 255)  # 종료 색상 (흰색)
background_gradient = create_gradient(start_color, end_color, screen_width, screen_height*2)

# 배경 위치 초기화
background_y = 0#background_gradient.get_rect().h // 2

# 게임 루프
running = True
clock = pygame.time.Clock()
while running:
    # 이벤트 처리
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      elif event.type == pygame.KEYUP:
        character.checkJumpOver(event)
          # print(f'Key {pygame.key.name(event.key)} is pressed.')

    # 게임 로직 업데이트
    all_sprites.update()
    
    # 충돌 체크
    if pygame.sprite.spritecollide(character, enemies, True):
      running = False
        
    # 배경 스크롤
    background_y += background_scroll_speed
    if background_y < -screen_height or background_y >= 0:
      background_scroll_speed = -background_scroll_speed
      
    # 게임 화면 업데이트
    screen.blit(background_gradient, (0, background_y))
    

    # 게임 화면 업데이트    
    all_sprites.draw(screen)
    pygame.display.flip()

    # 초당 프레임 설정
    clock.tick(60)

# Pygame 종료
pygame.quit()
