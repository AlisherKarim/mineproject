from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy as np

class Block:
    def __init__(self):
        pass

    def draw(self):
        pass


class Viewer:
    def __init__(self):
        pass

    def light(self):
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        # feel free to adjust light colors
        lightAmbient = [0.5, 0.5, 0.5, 1.0]
        lightDiffuse = [0.5, 0.5, 0.5, 1.0]
        lightSpecular = [0.5, 0.5, 0.5, 1.0]
        lightPosition = [1, 1, -1, 0]    # vector: point at infinity
        glLightfv(GL_LIGHT0, GL_AMBIENT, lightAmbient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightDiffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, lightSpecular)
        glLightfv(GL_LIGHT0, GL_POSITION, lightPosition)
        glEnable(GL_LIGHT0)

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0, 0, 0, 1)

        glMatrixMode(GL_MODELVIEW)

        # visualize your polygons here

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
        # for monitoring mouse position while it's not pressed
        glutPassiveMotionFunc(self.passive_motion)
        # glutReshapeFunc(self.reshape)

        self.light()

        glutMainLoop()


if __name__ == "__main__":
    viewer = Viewer()
    viewer.run()
