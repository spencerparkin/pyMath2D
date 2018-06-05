# math2d_test.py

import sys

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtGui, QtCore, QtWidgets
from math2d_vector import Vector
from math2d_polygon import Polygon
from math2d_region import Region, SubRegion

class Window(QtGui.QOpenGLWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
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
        
        self.test_polygon = None
    
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
        
        glColor3f(1.0, 1.0, 1.0)
        self.region.Render()
        
        glColor3f(1.0, 0.0, 0.0)
        self.cut_region.Render()
        
        if self.test_polygon is not None:
            self.test_polygon.mesh.Render()
        
        glFlush()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def mousePressEvent(self, event):
        button = event.button()
        if button == QtCore.Qt.LeftButton:
            pass
            # TODO: The first thing to test is just creating a graph that merges the region and cut-region together.

if __name__ == '__main__':
    
    app = QtGui.QGuiApplication(sys.argv)
    
    win = Window()
    win.resize(640, 480)
    win.show()
    
    sys.exit(app.exec_())