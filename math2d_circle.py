# math2d_circle.py

import math

from math2d_vector import Vector

class Circle(object):
    def __init__(self, center=None, radius=0.0):
        self.center = center if center is not None else Vector(0.0, 0.0)
        self.radius = radius
        
    def Copy(self):
        return Circle(self.center.Copy(), self.radius)
    
    def ContainsPoint(self, point, epsilon=1e-7):
        return True if (point - self.center).Length() <= self.radius + epsilon else False
    
    def Area(self):
        return math.pi * self.radius * self.radius
    
    def Circumference(self):
        return 2.0 * math.pi * self.radius

    def Render(self, sides=12):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_TRIANGLE_FAN
        glBegin(GL_TRIANGLE_FAN)
        try:
            glVertex2f(self.center.x, self.center.y)
            for i in range(sides + 1):
                angle = 2.0 * math.pi * (float(i) / float(sides))
                point = self.center + Vector(radius=self.radius, angle=angle)
                glVertex2f(point.x, point.y)
        finally:
            glEnd()