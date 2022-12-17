from __future__ import division

import sys
import random
import time

from collections import deque
from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from Block import *

def normalize(position):
  x, y, z = position
  x, y, z = (int(round(x)), int(round(y)), int(round(z)))
  return (x, y, z)

TICKS_PER_SEC = 60

if sys.version_info[0] >= 3:
  xrange = range


class World(object):

    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        self.world_blocks = set()
        self.block_to_texture = {}
        self.block_to_vList = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = set()

        # sector to list of Blocks
        self.sectors = {}
        
        
        self.on_air = set()

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self._initialize()

    def _initialize(self):
        """ Initialize the world by placing all the blocks.

        """
        n = 50  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                # create a layer stone an Block.grass everywhere.
                grass_block = Block((x, y - 2, z))
                stone_block = Block((x, y - 3, z))
                self.block_to_texture[grass_block] = GRASS
                self.block_to_texture[stone_block] = STONE
                self.add_block(grass_block, immediate=False)
                self.add_block(stone_block, immediate=False)
                # if x in (-n, n) or z in (-n, n):
                #   for dy in xrange(-2, 3):      
                    
                #     self.add_block(Block((x, y + dy, z), STONE), immediate=False)

        # generate the hills randomly
        o = n - 10
        for _ in xrange(120):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(1, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice([GRASS, SAND, BRICK])
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:  # kind of circular shape
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:  # cannot be close to the corner
                            continue
                        random_block = Block((x, y, z))
                        self.block_to_texture[random_block] = t
                        self.add_block(random_block, immediate=False)
                s -= d  # decrement side length so hills taper off

    def hit_test(self, position, vector, max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous_pos = None
        hit_block = Block()
        for _ in xrange(max_distance * m):
            hit_block.setPosition(normalize((x, y, z)))
            if hit_block.getPosition != previous_pos and hit_block in self.world_blocks:
              return hit_block, previous_pos
            previous_pos = hit_block.getPosition()
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, previous_pos

    def exposed(self, block : Block):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.

        """
        x, y, z = block.getPosition()
        currentBlock = Block((x, y, z))
        for dx, dy, dz in FACES:
          currentBlock.setPosition((x + dx, y + dy, z + dz))
          if currentBlock not in self.world_blocks:
            return True
        return False

    def add_block(self, block : Block, immediate : bool=True):
        """ Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.

        """
        if block in self.world_blocks:
          self.remove_block(block, immediate)
        self.world_blocks.add(block)
        self.sectors.setdefault(block.getSector(), []).append(block)
        if immediate:
          if self.exposed(block):
            self.show_block(block)
          self.check_neighbors(block)

    def remove_block(self, block : Block, immediate=True):
        """ Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.

        """
        self.world_blocks.remove(block)
        self.sectors[block.getSector()].remove(block)
        if immediate:
          if block in self.shown:
            self.hide_block(block)
          self.check_neighbors(block)

    def check_neighbors(self, block : Block):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        """
        x, y, z = block.getPosition()
        for dx, dy, dz in FACES:
            b = Block((x + dx, y + dy, z + dz))
            if b not in self.world_blocks:
                continue
            if self.exposed(b):
                if b not in self.shown:
                    self.show_block(b)
            else:
                if b in self.shown:
                    self.hide_block(b)

    def show_block(self, block : Block, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.

        """
        self.shown.add(block)
        if immediate:
            self._show_block(block)
        else:
            self._enqueue(self._show_block, block)

    def _show_block(self, block : Block):
        vertex_data = block.getVertices(0.5)
        texture_data = list(self.block_to_texture[block])
        self.block_to_vList[block] = self.batch.add(24, GL_QUADS, self.group,
                                               ('v3f/static', vertex_data),
                                               ('t2f/static', texture_data))
        if block.getPosition == (0, -2, 0):
          print(block.vList)

    def hide_block(self, block : Block, immediate=True):
        self.shown.remove(block)
        if immediate:
          self._hide_block(block)
        else:
          self._enqueue(self._hide_block, block)

    def _hide_block(self, block : Block):
      """ Private implementation of the 'hide_block()` method.

      """
      self.block_to_vList[block].delete()

    def show_sector(self, sector):
      """ Ensure all blocks in the given sector that should be shown are
      drawn to the canvas.

      """
      for block in self.sectors.get(sector, []):
        if block not in self.shown and self.exposed(block):
          self.show_block(block, False)

    def hide_sector(self, sector):
      for block in self.sectors.get(sector, []):
        if block in self.shown:
          self.hide_block(block, False)

    def change_sectors(self, before, after):
      before_set = set()
      after_set = set()
      pad = 4
      for dx in xrange(-pad, pad + 1):
          for dy in [0]:  # xrange(-pad, pad + 1):
              for dz in xrange(-pad, pad + 1):
                  if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                      continue
                  if before:
                      x, y, z = before
                      before_set.add((x + dx, y + dy, z + dz))
                  if after:
                      x, y, z = after
                      after_set.add((x + dx, y + dy, z + dz))
      show = after_set - before_set
      hide = before_set - after_set
      for sector in show:
          self.show_sector(sector)
      for sector in hide:
          self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.

        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.

        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False

        """
        start = time.perf_counter()
        while self.queue and time.perf_counter() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.

        """
        while self.queue:
            self._dequeue()
