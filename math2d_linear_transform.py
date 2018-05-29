# math2d_linear_transform.py

import math

from math2d_vector import Vector

class LinearTransform(object):
    def __init__(self, x_axis=None, y_axis=None):
        self.x_axis = x_axis if x_axis is not None else Vector(1.0, 0.0)
        self.y_axis = y_axis if y_axis is not None else Vector(0.0, 1.0)
    
    def Copy(self):
        return LinearTransform(self.x_axis.Copy(), self.y_axis.Copy())
    
    def Identity(self):
        self.x_axis = Vector(1.0, 0.0)
        self.y_axis = Vector(0.0, 1.0)
    
    def Transform(self, vector):
        return self.x_axis * vector.x + self.y_axis * vector.y
    
    def Concatinate(self, other):
        x_axis = self.Transform(other.x_axis)
        y_axis = self.Transform(other.y_axis)
        self.x_axis = x_axis
        self.y_axis = y_axis
    
    def Determinant(self):
        return self.x_axis.Cross(self.y_axis)
    
    def Invert(self):
        try:
            det = self.Determinant()
            scale = 1.0 / det
            x_axis = Vector(self.y_axis.y, -self.x_axis.x) * scale
            y_axis = Vector(-self.y_axis.x, self.x_axis.y) * scale
            self.x_axis = x_axis
            self.y_axis = y_axis
            return True
        except ZeroDivisionError:
            return False
    
    def Rotation(self, angle):
        ca = math.cos(angle)
        sa = math.sin(angle)
        self.x_axis.x = ca
        self.x_axis.y = sa
        self.y_axis.x = -sa
        self.y_axis.y = ca