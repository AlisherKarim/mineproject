from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np

# for loading textures
from PIL import Image

IMAGE_PATH = 'texture.png'

# solution for no np.float128/np.complex256 error on windows
np.float128 = np.longdouble
np.complex256 = np.clongdouble

def load_textures(path = IMAGE_PATH):
    img = Image.open(path)
    w, h = img.size

    # load texture images
    earth = img.crop((0, h/2, w/4, 3*h/4))
    sand = img.crop((w/4, h/2, w/2, 3*h/4))
    stone = img.crop((w/2, h/2, 3*w/4, 3*h/4))
    earth_wg = img.crop((0, 3*h/4, w/4, h))
    grass = img.crop((w/4, 3*h/4, w/2, h))
    brick = img.crop((w/2, 3*h/4, 3*w/4, h))

    img.close()

    # TODO create textures, mb need to create separate classes
    imgs = [earth, sand, stone, earth_wg, grass, brick]
    textures = []
    for i in imgs:  
        textData = i.tobytes("raw", "RGBA", 0, -1)
        # textData = np.array(list(i.getdata()))
        textID = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, textID)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, textData)
        textures.append(textID)

    return textures


class Block:
    def __init__(self):
        self.textures = load_textures()

    def draw(self):
        verts = ((1, 1), (1,-1), (-1,-1), (-1,1))
        texts = ((1, 0), (1, 1), (0, 1), (0, 0))
        surf = (0, 1, 2, 3)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[0])

        glBegin(GL_QUADS)
        for i in surf:
            glTexCoord2f(texts[i][0], texts[i][1])
            glVertex2f(verts[i][0], verts[i][1])
        glEnd()
        
        glDisable(GL_TEXTURE_2D)


class Viewer:
    def __init__(self):
        pass

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # color of clear sky
        glClearColor(135 / 255, 206 / 255, 235 / 255, 1)
        # do not render back facing facets
        glEnable(GL_CULL_FACE)

        glMatrixMode(GL_MODELVIEW)

        block = Block()
        block.draw()

        glutSwapBuffers()

    def keyboard(self, key, x, y):
        print(f"keyboard event: key={key}, x={x}, y={y}")
        if glutGetModifiers() & GLUT_ACTIVE_SHIFT:
            print("shift pressed")
        if glutGetModifiers() & GLUT_ACTIVE_ALT:
            print("alt pressed")
        if glutGetModifiers() & GLUT_ACTIVE_CTRL:
            print("ctrl pressed")

        glutPostRedisplay()

    def special(self, key, x, y):
        print(f"special key event: key={key}, x={x}, y={y}")

        glutPostRedisplay()

    def mouse(self, button, state, x, y):
        # button macros: GLUT_LEFT_BUTTON, GLUT_MIDDLE_BUTTON, GLUT_RIGHT_BUTTON
        print(f"mouse press event: button={button}, state={state}, x={x}, y={y}")

        glutPostRedisplay()

    def motion(self, x, y):
        print(f"mouse move event: x={x}, y={y}")

        glutPostRedisplay()

    def passive_motion(self, x, y):
        print(f"mouse (passive) move event: x={x}, y={y}")

        glutPostRedisplay()

    # def reshape(self, w, h):
    #     # implement here
    #     print(f"window size: {w} x {h}")

    #     # TODO adjust necessary changes to projection and ratio

    #     # change screen size and trackball radius
    #     self.screen_width, self.screen_height = w, h
    #     self.radius = min(self.screen_width, self.screen_height)

    #     glViewport(0, 0, w, h)
    #     glutPostRedisplay()


    def run(self):
        glutInit()
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(800, 800)
        glutInitWindowPosition(0, 0)
        glutCreateWindow(b"Minegame")

        glutDisplayFunc(self.display)
        glutKeyboardFunc(self.keyboard)
        glutSpecialFunc(self.special)
        glutMouseFunc(self.mouse)
        glutMotionFunc(self.motion)
        glutPassiveMotionFunc(self.passive_motion) # for monitoring mouse position while it's not pressed
        # glutReshapeFunc(self.reshape)

        glutMainLoop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()
