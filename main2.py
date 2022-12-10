from __future__ import division

import sys
import math

from pyglet.gl import *
from pyglet.window import key, mouse
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from World import *
from Player import *
from Block import *

TICKS_PER_SEC = 60

# Size of sectors used to ease block loading.
SECTOR_SIZE = 16

SPEED = 5
FLYING_SPEED = 15

GRAVITY = 20.0
MAX_JUMP_HEIGHT = 1.0  # About the height of a block.

JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50

PLAYER_HEIGHT = 2

if sys.version_info[0] >= 3:
    xrange = range

def normalize(position):
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3

    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


def sectorize(position):
    """ Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3

    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, 0, z)


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)
        
        self.player = Player()
        self.world = World()

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False
        self.reticle = None

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        self.world.process_queue()
        sector = sectorize(self.player.position)
        if sector != self.player.sector:
            self.world.change_sectors(self.player.sector, sector)
            if self.player.sector is None:
                self.world.process_entire_queue()
            self.player.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)

    def _update(self, dt):
        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.

        """
        # walking
        speed = SPEED
        d = dt * speed  # distance covered this tick.

        bls = list(self.world.on_air.keys())
        for pos in bls:
            bx, by, bz = pos
            
            texture = self.world.on_air[pos]
            vel = self.world.block_velocity[pos]
            del self.world.on_air[pos]       
            del self.world.block_velocity[pos]
            # del self.world.world[pos]
            self.world.remove_block(pos, True) 
            
            vel -= dt*GRAVITY
            vel = max(vel, -TERMINAL_VELOCITY)
            
            (bx, by, bz), collides = self.collision((bx, by + vel*dt, bz), 1)
            
            if collides:
                self.world.add_block(normalize((bx, by, bz)), texture, True)
                continue
            self.world.on_air[(bx, by, bz)] = texture
            self.world.block_velocity[(bx, by, bz)] = vel
            self.world.add_block((bx, by, bz), texture, True)


        dx, dy, dz = self.player.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        self.player.fall_velocity -= dt * GRAVITY
        self.player.fall_velocity = max(self.player.fall_velocity, -TERMINAL_VELOCITY)
        dy += self.player.fall_velocity * dt
        # collisions
        x, y, z = self.player.position
        (x, y, z), collides = self.collision((x + dx, y + dy, z + dz), self.player.height)
        self.player.position = (x, y, z)

    def collision(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.

        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.1 # 0.25
        p = list(position)
        np = normalize(position)
        collides = False
        for face in FACES:  # check all surrounding blocks
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in xrange(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.world.world:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        collides = True
                        self.player.fall_velocity = 0
                    break
        return tuple(p), collides

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.

        """
        if self.exclusive:
            vector = self.player.get_sight_vector()
            block, previous = self.world.hit_test(self.player.position, vector)
            if (button == mouse.RIGHT) or \
                    ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                if block is None:  # block is created on the air
                    self.world.on_air[previous] = self.player.current_block_texture
                    self.world.add_block(previous, self.player.current_block_texture)
                    self.world.block_velocity[previous] = 0
                
                elif previous:
                    self.world.add_block(previous, self.player.current_block_texture)
                    (a, b, c) = previous
                    (x, y, z) = self.player.position
                    if (a, 0, c) == normalize((x, 0, z)):
                      if self.player.fall_velocity == 0:
                        self.player.position = (x, y + 1, z)
                        self.player.fall_velocity = JUMP_SPEED

            elif button == pyglet.window.mouse.LEFT and block:
                texture = self.world.world[block]
                if texture != STONE:
                    self.world.remove_block(block)
        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.

        """
        if self.exclusive:
            m = 0.15
            x, y = self.player.look
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.player.look = (x, y)

    def on_key_press(self, symbol, modifiers):
      """ Called when the player presses a key. See pyglet docs for key
      mappings.

      Parameters
      ----------
      symbol : int
          Number representing the key that was pressed.
      modifiers : int
          Number representing any modifying keys that were pressed.

      """
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

    def on_key_release(self, symbol, modifiers):
      """ Called when the player releases a key. See pyglet docs for key
      mappings.

      Parameters
      ----------
      symbol : int
          Number representing the key that was pressed.
      modifiers : int
          Number representing any modifying keys that were pressed.

      """
      if symbol == key.W:
        self.player.move_backward()
      elif symbol == key.S:
        self.player.move_forward()
      elif symbol == key.A:
        self.player.move_right()
      elif symbol == key.D:
        self.player.move_left()

    def set_2d(self):
        """ Configure OpenGL to draw in 2d.

        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.player.look
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.player.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.world.batch.draw()
        self.set_2d()
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)
        
    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.

        """
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
                                                   ('v2i', (x - n, y, x + n,
                                                    y, x, y - n, x, y + n))
                                                   )


def setup():
    glClearColor(0.5, 0.69, 1.0, 1)
    glEnable(GL_CULL_FACE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)


def main():
    window = Window(width=800, height=600, caption='CSE47101', resizable=True)
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    window.set_exclusive_mouse(True)
    setup()
    pyglet.app.run()


if __name__ == '__main__':
    main()
