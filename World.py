import random

from pyglet import image
from pyglet.graphics import TextureGroup, Batch
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from Block import *
from Player import *

def normalize(position):
  x, y, z = position
  x, y, z = (int(round(x)), int(round(y)), int(round(z)))
  return (x, y, z)

TEXTURE_PATH = 'texture1.png'

class World(object):

  def __init__(self):
    self.batch = Batch()
    self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())
    self.world_blocks = set()
    self.block_to_texture = {}
    self.block_to_vList = {}
    self.shown = set()
    self.on_air = set()
    self._initialize()

  def _initialize(self):
    n = 50  
    y = 0  
    for x in range(-n, n + 1, 1):
      for z in range(-n, n + 1, 1):
        grass_block = Block((x, y - 2, z))
        stone_block = Block((x, y - 3, z))
        self.block_to_texture[grass_block] = GRASS
        self.block_to_texture[stone_block] = STONE
        self.add_block(grass_block)
        self.add_block(stone_block)
        if x in (-n, n) or z in (-n, n):
          for dy in range(-2, 5):      
            self.block_to_texture[Block((x, y + dy, z))] = STONE
            self.add_block(Block((x, y + dy, z)))

    o = n - 10
    for _ in range(50):
      x_pos = random.randint(-o, o)  
      z_pos = random.randint(-o, o)  
      h = random.randint(1, 6)  
      s = random.randint(4, 8)  
      t = random.choice([GRASS, SAND, BRICK])
      for y in range(-1, h - 1):
        for x in range(x_pos - s, x_pos + s + 1):
          for z in range(z_pos - s, z_pos + s + 1):
            if (x - x_pos) ** 2 + (z - z_pos) ** 2 > (s + 1) ** 2:  # kind of circular shape
              continue
            if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:  # cannot be close to the corner
              continue
            random_block = Block((x, y, z))
            self.block_to_texture[random_block] = t
            self.add_block(random_block)
        s -= 1

  def ray_trace(self, position, vector, max_distance=8):
    m = 8
    x, y, z = position
    dx, dy, dz = vector
    previous_pos = None
    hit_block = Block()
    for _ in range(max_distance * m):
      hit_block.setPosition(normalize((x, y, z)))
      if hit_block.getPosition != previous_pos and hit_block in self.world_blocks:
        return hit_block, previous_pos
      previous_pos = hit_block.getPosition()
      x, y, z = x + dx / m, y + dy / m, z + dz / m
    return None, previous_pos

  def add_block(self, block : Block):
    if block in self.world_blocks:
      self.remove_block(block)
    self.world_blocks.add(block)
    self.show_block(block)

  def remove_block(self, block : Block):
    self.world_blocks.remove(block)
    if block in self.shown:
      self.shown.remove(block)
      self.block_to_vList[block].delete()

  def show_block(self, block : Block):
    if block not in self.shown:
      self.shown.add(block)
    vertex_data = block.getVertices()
    texture_data = list(self.block_to_texture[block])
    self.block_to_vList[block] = self.batch.add(24, GL_QUADS, self.group,
                                              ('v3f/static', vertex_data),
                                              ('t2f/static', texture_data))
