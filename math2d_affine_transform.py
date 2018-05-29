# math2d_affine_transform.py

from math2d_vector import Vector
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
    
    def Transform(self, vector):
        return self.linear_transform(vector) + self.translation
    
    def Concatinate(self, other):
        self.translation = self.linear_transform.Transform(other.translation) + self.translation
        self.linear_transform.Concatinate(other)
    
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