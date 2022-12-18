import math

import pyglet
from pyglet.window import key, mouse
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from World import *
from Player import *
from Block import *

TICKS_PER_SEC = 60

SPEED = 5
FLYING_SPEED = 15

GRAVITY = 10.0
MAX_JUMP_HEIGHT = 1.0  # About the height of a block.

JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)

PLAYER_HEIGHT = 2

class Window(pyglet.window.Window):

  def __init__(self, *args, **kwargs):
    super(Window, self).__init__(*args, **kwargs)
    
    self.player = Player()
    self.world = World()

    self.exclusive = False

    self.num_keys = [key._1, key._2, key._3]

    pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

  def set_exclusive_mouse(self, exclusive):
    super(Window, self).set_exclusive_mouse(exclusive)
    self.exclusive = exclusive

  def update(self, dt):
    m = 8
    dt = min(dt, 0.2)
    for _ in range(m):
      self._update(dt / m)

  def _update(self, dt):
    speed = SPEED
    d = dt * speed

    bls = list(self.world.on_air)
    for block in bls:
      bx, by, bz = block.getPosition()
      
      texture = self.world.block_to_texture[block]
      vel = block.velocity
      
      self.world.on_air.remove(block) 
      del self.world.block_to_texture[block]
      self.world.remove_block(block)
      
      vel -= dt*GRAVITY
      
      (bx, by, bz), collides = self.collision((bx, by + vel*dt, bz), 1)
      
      if collides:
        self.world.block_to_texture[Block(normalize((bx, by, bz)))] = texture
        self.world.add_block(Block(normalize((bx, by, bz))))
        continue
      
      new_block = Block((bx, by, bz))
      self.world.block_to_texture[new_block] = texture
      new_block.velocity = vel
      self.world.on_air.add(new_block)
      self.world.add_block(new_block)

    dx, dy, dz = self.player.get_motion_vector()
    dx, dy, dz = dx * d, dy * d, dz * d
    self.player.fall_velocity -= dt * GRAVITY
    self.player.fall_velocity = self.player.fall_velocity
    dy += self.player.fall_velocity * dt
    x, y, z = self.player.position
    (x, y, z), collides = self.collision((x + dx, y + dy, z + dz), self.player.height)
    self.player.position = (x, y, z)

  def collision(self, position, height):
    pad = 0.1 # 0.25
    p = list(position)
    np = normalize(position)
    collides = False
    for face in FACES:  
      for i in range(3):  
        if not face[i]:
          continue
        d = (p[i] - np[i]) * face[i]
        if d < pad:
          continue
        for dy in range(height):
          op = list(np)
          op[1] -= dy
          op[i] += face[i]
          if Block(tuple(op)) not in self.world.world_blocks:
            continue
          p[i] -= (d - pad) * face[i]
          if face == (0, -1, 0) or face == (0, 1, 0):
            collides = True
            self.player.fall_velocity = 0
          break
    return tuple(p), collides

  def on_mouse_press(self, x, y, button, modifiers):
    if self.exclusive:
      vector = self.player.get_look_vector()
      block, previous = self.world.ray_trace(self.player.position, vector)
      if (button == mouse.RIGHT) or ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)): 
        new_block = Block(previous)
        self.world.block_to_texture[new_block] = self.player.current_block_texture
        
        if block is None:  # block is created on the air
          self.world.on_air.add(new_block)
          self.world.add_block(new_block)
        
        elif previous:
          self.world.add_block(new_block)
          (a, b, c) = previous
          (x, y, z) = self.player.position
          if (a, 0, c) == normalize((x, 0, z)):
            if self.player.fall_velocity == 0:
              self.player.position = (x, y + 1, z)
              self.player.fall_velocity = JUMP_SPEED

      elif button == pyglet.window.mouse.LEFT and block:
        if self.world.block_to_texture[block] != STONE:
          del self.world.block_to_texture[block]
          self.world.remove_block(block)
    else:
        self.set_exclusive_mouse(True)

  def on_mouse_motion(self, x, y, dx, dy):
    if self.exclusive:
      m = 0.2
      x, y = self.player.look
      x, y = x + dx * m, y + dy * m
      y = max(-90, min(90, y))
      self.player.look = (x, y)

  def on_key_press(self, symbol, m):
    if symbol == key.W:
      self.player.move_forward()
    elif symbol == key.S:
      self.player.move_backward()
    elif symbol == key.A:
      self.player.move_left()
    elif symbol == key.D:
      self.player.move_right()
    elif symbol == key.SPACE:
      if self.player.fall_velocity == 0:
        self.player.fall_velocity = JUMP_SPEED
    elif symbol == key.ESCAPE:
      self.set_exclusive_mouse(False)
    elif symbol in self.num_keys:
      idx = (symbol - self.num_keys[0]) % len(self.player.inventory)
      self.player.current_block_texture = self.player.inventory[idx]

  def on_key_release(self, symbol, m):
    if symbol in [key.W, key.S]:
      self.player.stopForwardMovement()
    else:
      self.player.stopSideMovement()
      
  def on_draw(self):
    self.clear()
    width, height = self.get_size()
    glEnable(GL_DEPTH_TEST)
    viewport = self.get_viewport_size()
    glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(65.0, width / float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x, y = self.player.look
    glRotatef(x, 0, 1, 0)
    glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
    x, y, z = self.player.position
    glTranslatef(-x, -y, -z)
    glColor3d(1, 1, 1)
    self.world.batch.draw()

def setup():
  glClearColor(0.5, 0.69, 1.0, 1)
  glEnable(GL_CULL_FACE)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


def main():
  window = Window(width=800, height=600, caption='CSE47101', resizable=True)
  window.set_exclusive_mouse(True)
  setup()
  pyglet.app.run()


if __name__ == '__main__':
  main()
