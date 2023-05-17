'''
pygame introduction

볼(Ball) 이미지를 불러와 게임화면에 출력하고, 공을 이동시킨다
규칙적인 알고리즘으로 이동시킨다.
'''

import sys, pygame

# pygame 모듈 초기화!!! (반드시!!!)
pygame.init()

# 게임 화면(윈도우 사이즈)를 아래와 같이 초기화한다(pixel 단위)
size = width, height = 640, 480, # 여기서 size 변수는 tuple 임
speed = [2,2]   # 공이 이동할 스피드(Pixel 단위)
black = 0,0,0   # 이렇게 저장하면 tuple의 형태로 black이라는 변수가 초기화된다. 백그라운드 컬러를 블랙(0,0,0)으로 초기화

# display모듈의 set_mode 함수는 surface객체를 주어진 크기(w, h)로 생성하여 반환한다.
# surface 객체는 화면에 출력될(?) 이미지로써 메모리상에 존재한다.
# display모듈의 update 함수에 의해 최종적으로 화면에 나타나게 된다.
screen = pygame.display.set_mode(size)

# 폰트 객체를 생성하고 초기화한다.
font = pygame.font.Font(None, 24)

# Clock 객체를 생성한다.
# Clock 객체는 기본적으로 게임과 화면의 주사율 동기화에 사용된다.
clock = pygame.time.Clock()

# image모듈의 load()함수는 파일로부터 이미지를 불러와 
# surface 객체를 생성하여 반환한다
image_path = "intro_ball.gif"
ball = pygame.image.load(image_path)

# 객체의 위치정보나 충돌여부를 체크하기 위해
# Rectangle(사각형) 정보를 초기화한다.
# 아래의 경우 x, y 좌표는 0,0이고, width, height 값은 이미지의 넓이와 높이 값을 갖는다.
ballrect = ball.get_rect()

# 이벤트(키, 마우스, Re-Drawing 필요여부 등)와 디스플레이 Refresh를 위해
# 게임(Application)이 종료될때까지 루프를 반복한다.

# 루프를 반복하거나 탈출하기 위한 Flag(switch)변수를 초기화.
running = True

# 플래그 변수(running)의 값이 참(True)인동안 루프를 반복한다.
while running:
  # Clock 객체의 카운터를 초기화한다. 
  # 아래의 경우 초당 60회 카운트하도록 한다.  
  clock.tick(60)  
  
  # event모듈의 get()함수는 Event객체 리스트를 반환한다.
  # 가져온 이벤트 리스트를 반복하며 이벤트 객체를 가져와 처리한다.
  # 이때 이벤트 객체가 QUIT이면 Flag 변수, running의 값을 False로 하여 루프를 탈출할 수 있도록 한다.
  for event in pygame.event.get():    
    if event.type == pygame.QUIT: 
      running = False
  
  # ballrect정보를 화면에 출력하기 위해 text Surface 객체를 생성한다.
  text = font.render(f"Ball Position : (x={ballrect.x}), (y={ballrect.y},speed=({speed}))", 
                     True, # anti-alias
                     (255, 255, 255)) # text color
  
  # ball 객체의 위치값을 나타내는 ballrect의 값을 speed값에 의해 변경한다.  
  ballrect = ballrect.move(speed)
  # ballrect의 left, right 값이 음수가 되거나, 게임영역 넓이를 넘어가면 좌우 이동 offset값의 부호를 바꾼다.
  if ballrect.left < 0 or ballrect.right > width:
    speed[0] = -speed[0]
  # ballrect의 top, bottom 값이 음수가 되거나, 게임영역 높이를 넘어가면 상하 이동 offset값의 부호를 바꾼다.
  if ballrect.top < 0 or ballrect.bottom > height:
    speed[1] = -speed[1]
      
  # screen Surface객체를 검정색(0,0,0)으로 채운다
  screen.fill(black)
  # screen Surface객체에 ball객체(Surface)를 ballrect 위치에 그린다(찍는다).
  screen.blit(ball, ballrect)  
  # screen Surface객체에 text객체를 0,0위치에 그린다.
  screen.blit(text, (0, 0))
  # display모듈의 update()함수는 screen Surface 객체를 윈도우에 나타낸다
  pygame.display.update()
  
  #  print(f'display updated ===> ({clock.get_time()})')