# math2d_vector.py

import math

class Vector(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)
    
    def __neg__(self):
        return Vector(-self.x, -self.y)
    
    def Copy(self):
        return Vector(self.x, self.y)
    
    def IsPoint(self, point, epsilon=1e-7):
        return True if (point - self).Length() < epsilon else False
    
    def Length(self):
        return math.sqrt(self.Dot(self))
    
    def Normalize(self):
        try:
            self.Scale(1.0 / self.Length())
            return True
        except ZeroDivisionError:
            return False
    
    def Scale(self, scale):
        self.x *= scale
        self.y *= scale
    
    def Dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def Cross(self, other):
        return self.x * other.y - self.y * other.x
    
    def Reflect(self, normal):
        return self.Project(normal) - self.Reject(normal)
    
    def Project(self, normal):
        return normal * self.Dot(normal)
    
    def Reject(self, normal):
        return self - self.Project(normal)
    
    def AngleBetween(self, vector):
        normal_vector_a = self.Copy()
        normal_vector_a.Normalize()
        normal_vector_b = vector.Copy()
        normal_vector_b.Normalize()
        angle = math.acos(normal_vector_a.Dot(normal_vector_b))
        return angle

    def SignedAngleBetween(self, vector):
        angle = self.AngleBetween(vector)
        return angle if self.Cross(vector) >= 0.0 else -angle