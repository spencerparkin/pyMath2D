# math2d_test.py

import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from math2d_vector import Vector
from math2d_polygon import Polygon

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.polygon = Polygon()
        self.polygon.vertex_list.append(Vector(-1.0, -1.0))
        self.polygon.vertex_list.append(Vector(3.0, 3.0))
        self.polygon.vertex_list.append(Vector(3.5, -2.0))
        self.polygon.vertex_list.append(Vector(3.0, -2.0))
        self.polygon.vertex_list.append(Vector(4.0, -2.6))
        self.polygon.vertex_list.append(Vector(4.1, 5.0))
        self.polygon.vertex_list.append(Vector(-5.0, 1.0))
        self.polygon.vertex_list.append(Vector(-5.5, 3.5))
        self.polygon.vertex_list.append(Vector(-6.5, 0.0))
        self.polygon.vertex_list.append(Vector(-1.5, -5.0))
        self.polygon.Tessellate()
    
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
        
        glColor3f(1.0, 1.0, 1.0)
        self.polygon.Render()
        
        self.polygon.mesh.Render()
        
        glFlush()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

if __name__ == '__main__':
    
    app = QtGui.QGuiApplication(sys.argv)
    
    win = Window()
    win.resize(640, 480)
    win.show()
    
    sys.exit(app.exec_())