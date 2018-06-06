# math2d_affine_transform.py

from math2d_vector import Vector
from math2d_line_segment import LineSegment
from math2d_linear_transform import LinearTransform

class AffineTransform(object):
    def __init__(self, x_axis=None, y_axis=None, translation=None):
        self.linear_transform = LinearTransform(x_axis, y_axis)
        self.translation = translation if translation is not None else Vector(0.0, 0.0)
    
    def Copy(self):
        return AffineTransform(self.linear_transform.x_axis.Copy(), self.linear_transform.y_axis.Copy(), self.translation.Copy())
    
    def Identity(self):
        self.linear_transform.Identity()
        self.translation = Vector(0.0, 0.0)
    
    def Transform(self, object):
        return self.linear_transform.Transform(object) + self.translation
    
    def __call__(self, object):
        return self.Transform(object)
    
    def Concatinate(self, other):
        self.translation = self.linear_transform.Transform(other.translation) + self.translation
        self.linear_transform.Concatinate(other)
    
    def __mul__(self, other):
        if isinstance(other, AffineTransform):
            transform = other.Copy()
            transform.Concatinate(self)
            return transform
        elif isinstance(other, Vector):
            return self.Transform(other)
        elif isinstance(other, LineSegment):
            return LineSegment(self * other.point_a, self * other.point_b)
    
    def Determinant(self):
        return self.linear_transform.Determinant()
    
    def Invert(self):
        self.linear_transform.Invert()
        self.translation = -self.linear_transform.Transform(self.translation)
    
    def Rotation(self, center, angle):
        self.Identity()
        self.Concatinate(AffineTransform(None, None, -center))
        self.Concatinate(AffineTransform().linear_transform.Rotation(angle))
        self.Concatinate(AffineTransform(None, None, center))
    
    def Reflect(self, center, vector):
        pass
    
    def Translate(self, translation):
        self.Identity()
        self.translation = translation
    
    def RigidBodyMotion(self, angle, translation):
        pass
    
    def Decompose(self):
        pass