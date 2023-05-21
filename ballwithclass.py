'''
bouncing ball 을 class 형태로 바꾸기
'''

import pygame
import threading, sys, os



class Ball(pygame.sprite.Sprite):
  def __init__(self, filepath:str, speed:tuple, screen_size:tuple) -> None:
    pygame.sprite.Sprite.__init__(self)
    self.image = pygame.image.load(filepath)
    self.rect = self.image.get_rect()
    self.speed = [x for x in speed]
    self.screen_size = [x for x in screen_size]
    
    # print(self.speed)
    # print(self.screen_size)
  
  def update(self):
    # ball 객체의 위치값을 나타내는 ballrect의 값을 speed값에 의해 변경한다.  
    self.rect = self.rect.move(self.speed)
    
    # print(self.rect.left, self.rect.right, self.rect.top, self.rect.bottom)
    # print(self.screen_size[0], self.screen_size[1])
        
    # ballrect의 left, right 값이 음수가 되거나, 게임영역 넓이를 넘어가면 좌우 이동 offset값의 부호를 바꾼다.
    if self.rect.left < 0 or self.rect.right > self.screen_size[0]:    
      self.speed[0] = -self.speed[0]
    # ballrect의 top, bottom 값이 음수가 되거나, 게임영역 높이를 넘어가면 상하 이동 offset값의 부호를 바꾼다.
    if self.rect.top < 0 or self.rect.bottom > self.screen_size[1]:
      self.speed[1] = -self.speed[1]
    


if __name__=='__main__':
  SCREEN_WIDTH = 640
  SCREEN_HEIGHT = 480
  screen_size = SCREEN_WIDTH, SCREEN_HEIGHT
  
  # Update Rate = Frame Rate
  FR = 60
  
  speed = [2,2]   # 공이 이동할 스피드(Pixel 단위)
  black = 0,0,0   # 이렇게 저장하면 tuple의 형태로 black이라는 변수가 초기화된다. 백그라운드 컬러를 블랙(0,0,0)으로 초기화
  
  # 현재 실행 파일의 경로 추출
  current_path = os.path.dirname(sys.argv[0])
  print(current_path)

  # 절대 경로로 변환
  absolute_path = os.path.abspath(current_path)
  print(absolute_path)
  
  # 폰트 파일(ttf) Path 구하기 : 
  font_filepath = os.path.join(absolute_path, 'NanumGothic.ttf')
  
  pygame.init()
  
  ball = Ball('intro_ball.gif', (2,2), (SCREEN_WIDTH, SCREEN_HEIGHT))
  
  all_sprites = pygame.sprite.Group()  
  all_sprites.add(ball)
  
  # 폰트 객체를 생성하고 초기화한다.
  font = pygame.font.Font(font_filepath, 24)
  
  # 게임 영역 지정하고 메인 서피스 객체를 생성
  screen = pygame.display.set_mode(screen_size)
  clock = pygame.time.Clock()
  
  # 루프를 반복하거나 탈출하기 위한 Flag(switch)변수를 초기화.
  running = True

  # 플래그 변수(running)의 값이 참(True)인동안 루프를 반복한다.
  while running:
    # Clock 객체의 카운터를 초기화한다. 
    # 아래의 경우 초당 60회 카운트하도록 한다.  
    clock.tick(FR)
    
    # event모듈의 get()함수는 Event객체 리스트를 반환한다.
    # 가져온 이벤트 리스트를 반복하며 이벤트 객체를 가져와 처리한다.
    # 이때 이벤트 객체가 QUIT이면 Flag 변수, running의 값을 False로 하여 루프를 탈출할 수 있도록 한다.
    for event in pygame.event.get():    
      if event.type == pygame.QUIT: 
        running = False
    
    # ballrect정보를 화면에 출력하기 위해 text Surface 객체를 생성한다.
    text = font.render(f"공위치 : (x={ball.rect.x}), (y={ball.rect.y},속도=({ball.speed}))", 
                      True, # anti-alias
                      (255, 255, 255)) # text color
    
    
    ball.update()
                
    # screen Surface객체를 검정색(0,0,0)으로 채운다
    screen.fill(black)
    
    all_sprites.update()
    
    # screen Surface객체에 ball객체(Surface)를 ballrect 위치에 그린다(찍는다).
    # screen.blit(ball, ballrect)  
    # screen Surface객체에 text객체를 0,0위치에 그린다.
    all_sprites.draw(screen)
    screen.blit(text, (0, 0))
    
    # display모듈의 update()함수는 screen Surface 객체를 윈도우에 나타낸다
    # pygame.display.update(ballrect)
    pygame.display.flip()