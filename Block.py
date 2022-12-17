
def tex_coord(x, y, n=4):
  m = 1.0 / n
  dx = x * m
  dy = y * m
  return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
  top = tex_coord(*top)
  bottom = tex_coord(*bottom)
  side = tex_coord(*side)
  result = []
  result.extend(top)
  result.extend(bottom)
  result.extend(side * 4)
  return result

TEXTURE_PATH = 'texture1.png'
GRASS = tex_coords((1, 0), (0, 1), (0, 0))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
BRICK = tex_coords((2, 0), (2, 0), (2, 0))
STONE = tex_coords((2, 1), (2, 1), (2, 1))

FACES = [
  (0, 1, 0),
  (0, -1, 0),
  (-1, 0, 0),
  (1, 0, 0),
  (0, 0, 1),
  (0, 0, -1),
]

def normalize(position):
  x, y, z = position
  x, y, z = (int(round(x)), int(round(y)), int(round(z)))
  return (x, y, z)

class Block():
  def __init__(self, pos = (0, 0, 0)):
    self._position = pos
    self.is_moving = False
    self.velocity = 0
  
  def __eq__(self, other):
    return (other.getPosition()) == (self._position)
  
  def __hash__(self):
    return hash(self._position)
  
  def getPosition(self):
    return self._position
  
  def setPosition(self, pos):
    self._position = pos
  
  def getVertices(self, n):
    x, y, z = self._position
    return [
      x-n, y+n, z-n, x-n, y+n, z+n, x+n, y+n, z+n, x+n, y+n, z-n,  # top
      x-n, y-n, z-n, x+n, y-n, z-n, x+n, y-n, z+n, x-n, y-n, z+n,  # bottom
      x-n, y-n, z-n, x-n, y-n, z+n, x-n, y+n, z+n, x-n, y+n, z-n,  # left
      x+n, y-n, z+n, x+n, y-n, z-n, x+n, y+n, z-n, x+n, y+n, z+n,  # right
      x-n, y-n, z+n, x+n, y-n, z+n, x+n, y+n, z+n, x-n, y+n, z+n,  # front
      x+n, y-n, z-n, x-n, y-n, z-n, x-n, y+n, z-n, x+n, y+n, z-n,  # back
    ]