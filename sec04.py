'''
pygame의 시작 2
'''

import pygame, sys

# pygame 모듈의 초기화
pygame.init()

# display될 surface 객체를 만든다
screen = pygame.display.set_mode((640, 480))

# 논리적인 원을 생성
ball_obj = pygame.draw.circle(surface=screen, 
                              color=(255,0,0), 
                              center=[100, 100], 
                              radius=40)

# 이벤트를 가져오고 처리해준다
while True:
  events = pygame.event.get()
  for event in events:
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
      
  # 논리적인 원의 속성을 이용해 화면에 볼을 그림
  pygame.draw.circle(surface=screen, color=(255,0,0), center=ball_obj.center, radius=40)
    
  #pygame.display.update()  # 화면의 변경사항만 체크하여 update 
  pygame.display.flip()     # 전체 화면을 update

