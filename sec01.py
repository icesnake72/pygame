'''
pygame practice section 01
이미지 움직이기 기초
'''

def move1():
  screen = [1,1,2,2,2,1]
  print(screen)
  
def move2():
  screen = [1,1,2,2,2,1]
  screen[3] = 8
  print(screen)
  
def move3():
  screen = [1,1,2,2,2,1]
  playerpos = 3
  screen[playerpos] = 8
  print(screen)
  
def move4():
  screen = [1,1,2,2,2,1]
  playerpos = 3
  screen[playerpos] = 8  
  print(screen)
  playerpos -= 1
  screen[playerpos] = 8  
  print(screen)

def move5():
  background = [1,1,2,2,2,1]
  screen = background.copy()
  print(screen)
    
  playerpos = 3
  screen[playerpos] = 8  
  print(screen)

# def move5():
#   background = [1,1,2,2,2,1]
#   screen = background.copy()
#   print(screen)
    
#   playerpos = 3
#   screen[playerpos] = 8  
#   print(screen)
  
#   screen[playerpos] = background[playerpos]
#   playerpos -= 1
#   screen[playerpos] = 8
  
# def move5():
#   background = [1,1,2,2,2,1]
#   screen = background.copy()
#   print(screen)
    
#   playerpos = 3
#   screen[playerpos] = 8  
#   print(screen)
  
#   screen[playerpos] = background[playerpos]
#   playerpos -= 1
#   screen[playerpos] = 8
#   print(screen)

def move6():
  background = [1,1,2,2,2,1]
  screen = background.copy()
  print(screen)
    
  playerpos = 3
  screen[playerpos] = 8  
  print(screen)
  
  screen[playerpos] = background[playerpos]
  playerpos -= 1
  screen[playerpos] = 8
  print(screen)
  
  screen[playerpos] = background[playerpos]
  playerpos -= 1
  screen[playerpos] = 8
  print(screen)
  
  
def move7():
  background = []

# move1()
# move2()
# move3()
# move4()
# move5()
move6()