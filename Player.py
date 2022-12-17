import math


def tex_coord(x, y, n=4):
  """ Return the bounding vertices of the texture square.

  """
  m = 1.0 / n
  dx = x * m
  dy = y * m
  return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
  """ Return a list of the texture squares for the top, bottom and side.

  """
  top = tex_coord(*top)
  bottom = tex_coord(*bottom)
  side = tex_coord(*side)
  result = []
  result.extend(top)
  result.extend(bottom)
  result.extend(side * 4)
  return result

GRASS = tex_coords((1, 0), (0, 1), (0, 0))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
BRICK = tex_coords((2, 0), (2, 0), (2, 0))
STONE = tex_coords((2, 1), (2, 1), (2, 1))

class Player:
  def __init__(self):
    self.position = (0, 0, 0)
    self.height = 2
    self.movement = [0, 0]
    self.fall_velocity = 0
    self.look = (0, 0)
    self.inventory = [BRICK, SAND, STONE]
    self.current_block_texture = self.inventory[0]
  
  def move_forward(self):
    self.movement[0] = -1
  
  def move_backward(self):
    self.movement[0] = 1
    
  def move_left(self):
    self.movement[1] = -1
    
  def move_right(self):
    self.movement[1] = 1
    
  def stopSideMovement(self):
    self.movement[1] = 0
    
  def stopForwardMovement(self):
    self.movement[0] = 0
  
  def get_motion_vector(self):
    if any(self.movement):
      x, y = self.look
      strafe = math.degrees(math.atan2(*self.movement))
      x_angle = math.radians(x + strafe)
      dy = 0.0
      dx = math.cos(x_angle)
      dz = math.sin(x_angle)
    else:
      dy = 0.0
      dx = 0.0
      dz = 0.0
    return (dx, dy, dz)
  
  def get_look_vector(self):
    x, y = self.look
    m = math.cos(math.radians(y))
    dy = math.sin(math.radians(y))
    dx = math.cos(math.radians(x - 90)) * m
    dz = math.sin(math.radians(x - 90)) * m
    return (dx, dy, dz)
    
    
    