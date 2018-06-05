# math2d_test.py

import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def initializeGL(self):
        glShadeModel(GL_FLAT)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)
    
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        viewport = glGetIntegerv(GL_VIEWPORT)
        width = viewport[2]
        height = viewport[3]
        
        aspect_ratio = float(width) / float(height)
        extent = 10.0
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if aspect_ratio > 0.0:
            gluOrtho2D(-extent * aspect_ratio, extent * aspect_ratio, -extent, extent)
        else:
            gluOrtho2D(-extent, extent, -extent / aspect_ratio, extent / aspect_ratio)
            
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glBegin(GL_QUADS)
        glColor3f(1.0, 0.0, 0.0)
        glVertex2f(-5.0, -5.0)
        glVertex2f(5.0, -5.0)
        glVertex2f(5.0, 5.0)
        glVertex2f(-5.0, 5.0)
        glEnd()
        
        glFlush()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

if __name__ == '__main__':
    
    app = QtGui.QGuiApplication(sys.argv)
    
    win = Window()
    win.show()
    
    sys.exit(app.exec_())