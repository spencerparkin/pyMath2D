# math2d_triangle.py

import math
import copy

from math2d_vector import Vector
from math2d_line_segment import LineSegment

class Triangle(object):
    def __init__(self, vertex_a=None, vertex_b=None, vertex_c=None):
        self.vertex_a = vertex_a if vertex_a is not None else Vector(0.0, 0.0)
        self.vertex_b = vertex_b if vertex_a is not None else Vector(0.0, 0.0)
        self.vertex_c = vertex_c if vertex_a is not None else Vector(0.0, 0.0)
    
    def Copy(self):
        return copy.deepcopy(self)
    
    def Area(self):
        # Note that a triangle will have negative area if it is not wound CCW in the plane.
        area = (self.vertex_b - self.vertex_a).Cross(self.vertex_c - self.vertex_a) / 2.0
        return area
    
    def Vertex(self, i):
        return [self.vertex_a, self.vertex_b, self.vertex_c][i]
    
    def ContainsPoint(self, point, epsilon=1e-7):
        # Note that our correctness here depends on a CCW ordering of the vertices in the plane.
        for i in range(3):
            if self.Vertex(i).IsPoint(point, epsilon):
                return True
        for i in range(3):
            j = (i + 1) % 3
            if LineSegment(self.Vertex(i), self.Vertex(j)).ContainsPoint(point, epsilon):
                return True
        # The following check is really all that is necessary, but the previous
        # two checks allow us to approximate the result.  We could approximate
        # the result here too by using our espilon instead of zero, but that might
        # not be as well defined as what we're doing to approximate above.
        for i in range(3):
            j = (i + 1) % 3
            if Triangle(self.Vertex(i), self.Vertex(j), point).Area() < 0.0:
                return False
        return True

    def IsDegenerate(self, epsilon=1e-7):
        return True if math.abs(self.Area()) < epsilon else False
    
    def FixWindingIfNecessary(self):
        if self.Area() < 0.0:
            vertex = self.vertex_b
            self.vertex_b = self.vertex_c
            self.vertex_c = vertex
    
    def Render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_TRIANGLES
        glBegin(GL_TRIANGLES)
        glVertex2f(self.vertex_a.x, self.vertex_a.y)
        glVertex2f(self.vertex_b.x, self.vertex_b.y)
        glVertex2f(self.vertex_c.x, self.vertex_c.y)
        glEnd()