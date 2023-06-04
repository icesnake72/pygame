import pygame as pyg

pyg.init()
screen =pyg.display.set_mode((1280, 720), vsync=1)
pyg.display.set_caption("GUI")
clock = pyg.time.Clock()
running = True
dt = 0
player_pos = pyg.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:
  for event in pyg.event.get():
    if event.type == pyg.QUIT:
      running = False
      
  screen.fill("purple")
  pyg.draw.circle(screen, "red", player_pos, 40)
  
  keys = pyg.key.get_pressed()
  if keys[pyg.K_w]:
      player_pos.y -= 300 * dt
  if keys[pyg.K_s]:
      player_pos.y += 300 * dt
  if keys[pyg.K_a]:
      player_pos.x -= 300 * dt
  if keys[pyg.K_d]:
      player_pos.x += 300 * dt
  
  pyg.display.flip()
  dt = clock.tick(60) / 1000

pyg.quit()