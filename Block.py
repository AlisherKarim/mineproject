FACES = [
  (0, 1, 0),
  (0, -1, 0),
  (-1, 0, 0),
  (1, 0, 0),
  (0, 0, 1),
  (0, 0, -1),
]

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
  
  def getVertices(self):
    x, y, z = self._position
    return [
      x-0.5, y+0.5, z-0.5, x-0.5, y+0.5, z+0.5,
      x+0.5, y+0.5, z+0.5, x+0.5, y+0.5, z-0.5,  # top
      x-0.5, y-0.5, z-0.5, x+0.5, y-0.5, z-0.5, 
      x+0.5, y-0.5, z+0.5, x-0.5, y-0.5, z+0.5,  # bottom
      x-0.5, y-0.5, z-0.5, x-0.5, y-0.5, z+0.5, 
      x-0.5, y+0.5, z+0.5, x-0.5, y+0.5, z-0.5,  # left
      x+0.5, y-0.5, z+0.5, x+0.5, y-0.5, z-0.5, 
      x+0.5, y+0.5, z-0.5, x+0.5, y+0.5, z+0.5,  # right
      x-0.5, y-0.5, z+0.5, x+0.5, y-0.5, z+0.5, 
      x+0.5, y+0.5, z+0.5, x-0.5, y+0.5, z+0.5,  # front
      x+0.5, y-0.5, z-0.5, x-0.5, y-0.5, z-0.5, 
      x-0.5, y+0.5, z-0.5, x+0.5, y+0.5, z-0.5,  # back
    ]