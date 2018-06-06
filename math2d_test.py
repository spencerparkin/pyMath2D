# math2d_test.py

import sys
import random

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from math2d_vector import Vector
from math2d_polygon import Polygon
from math2d_region import Region, SubRegion
from math2d_planar_graph import PlanarGraph, PlanarGraphEdgeLabel

class TestCase(object):
    def __init__(self):
        pass
    
    def Render(self):
        pass
    
    def Click(self):
        pass

class TestCaseA(TestCase):
    def __init__(self):
        super().__init__()

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-5.0, -4.0))
        sub_region.polygon.vertex_list.append(Vector(4.0, -4.0))
        sub_region.polygon.vertex_list.append(Vector(4.0, 3.0))
        sub_region.polygon.vertex_list.append(Vector(-5.0, 3.0))

        hole = Polygon()
        hole.vertex_list.append(Vector(-4.0, -3.0))
        hole.vertex_list.append(Vector(3.0, -3.0))
        hole.vertex_list.append(Vector(3.0, -2.0))
        hole.vertex_list.append(Vector(-3.0, -2.0))
        hole.vertex_list.append(Vector(-3.0, 1.0))
        hole.vertex_list.append(Vector(3.0, 1.0))
        hole.vertex_list.append(Vector(3.0, 2.0))
        hole.vertex_list.append(Vector(-4.0, 2.0))
        sub_region.hole_list.append(hole)

        hole = Polygon()
        hole.vertex_list.append(Vector(-2.0, -1.0))
        hole.vertex_list.append(Vector(0.0, -1.0))
        hole.vertex_list.append(Vector(0.0, 0.0))
        hole.vertex_list.append(Vector(-2.0, 0.0))
        sub_region.hole_list.append(hole)

        hole = Polygon()
        hole.vertex_list.append(Vector(1.0, -1.0))
        hole.vertex_list.append(Vector(3.0, -1.0))
        hole.vertex_list.append(Vector(3.0, 0.0))
        hole.vertex_list.append(Vector(1.0, 0.0))
        sub_region.hole_list.append(hole)

        self.region = Region()
        self.region.sub_region_list.append(sub_region)

        self.cut_region = Region()

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-1.0, -5.0))
        sub_region.polygon.vertex_list.append(Vector(5.0, -5.0))
        sub_region.polygon.vertex_list.append(Vector(5.0, 4.0))
        sub_region.polygon.vertex_list.append(Vector(-1.0, 4.0))
        self.cut_region.sub_region_list.append(sub_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-6.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, 1.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, 4.0))
        sub_region.polygon.vertex_list.append(Vector(-6.0, 4.0))
        self.cut_region.sub_region_list.append(sub_region)

        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(-6.0, -5.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, -5.0))
        sub_region.polygon.vertex_list.append(Vector(-3.0, -3.0))
        sub_region.polygon.vertex_list.append(Vector(-6.0, -3.0))
        self.cut_region.sub_region_list.append(sub_region)
        
        sub_region = SubRegion()
        sub_region.polygon.vertex_list.append(Vector(0.5, 0.5))
        sub_region.polygon.vertex_list.append(Vector(0.5, -1.5))
        sub_region.polygon.vertex_list.append(Vector(3.5, -1.5))
        sub_region.polygon.vertex_list.append(Vector(3.5, 0.5))
        self.cut_region.sub_region_list.append(sub_region)
    
        self.result_region = None
        self.polygon_list = []

    def Render(self):
        if self.result_region is None:
            glColor3f(1.0, 1.0, 1.0)
            self.region.Render()
            glColor3f(1.0, 0.0, 0.0)
            self.cut_region.Render()
        else:
            glColor3f(0.0, 1.0, 0.0)
            self.result_region.Render()

            for polygon in self.polygon_list:
                glColor3f(random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))
                polygon.mesh.Render()

    def Click(self):
        self.result_region = self.region.CutAgainst(self.cut_region)
        self.polygon_list = self.result_region.TessellatePolygons()

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.test_case = TestCaseA()
    
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
        extent = 6.0
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if aspect_ratio > 0.0:
            gluOrtho2D(-extent * aspect_ratio, extent * aspect_ratio, -extent, extent)
        else:
            gluOrtho2D(-extent, extent, -extent / aspect_ratio, extent / aspect_ratio)
            
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        self.test_case.Render()
        
        glFlush()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def mousePressEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            self.test_case.Click()
            self.update()

def ExceptionHook(cls, exc, tb):
    sys.__excepthook__(cls, exc, tb)

if __name__ == '__main__':
    sys.excepthook = ExceptionHook
    
    app = QtGui.QGuiApplication(sys.argv)
    
    win = Window()
    win.resize(640, 480)
    win.show()
    
    sys.exit(app.exec_())