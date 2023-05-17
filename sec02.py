'''
pygame의 시작
'''

import pygame, sys

# pygame 모듈의 초기화
pygame.init()

# display될 surface 객체를 만든다
screen = pygame.display.set_mode((640, 480))

# 이벤트를 가져오고 처리해준다
while True:
  events = pygame.event.get()
  for event in events:
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
      
    
  #pygame.display.update()  # 화면의 변경사항만 체크하여 update 
  pygame.display.flip()     # 전체 화면을 update