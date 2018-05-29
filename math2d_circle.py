# math2d_circle.py

import math

from math2d_vector import Vector

class Circle(object):
    def __init__(self, center=None, radius=0.0):
        self.center = center if center is not None else Vector(0.0, 0.0)
        self.radius = radius
        
    def Copy(self):
        return Circle(self.center.Copy(), self.radius)
    
    def EncompassesPoint(self, point, epsilon=1e-7):
        return True if (point - self.center).Length() <= self.radius + epsilon else False
    
    def Area(self):
        return math.pi * self.radius * self.radius
    
    def Circumference(self):
        return 2.0 * math.pi * self.radius