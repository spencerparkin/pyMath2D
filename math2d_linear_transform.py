# math2d_linear_transform.py

import math

from math2d_vector import Vector

class LinearTransform(object):
    def __init__(self, x_axis=None, y_axis=None):
        self.x_axis = x_axis if x_axis is not None else Vector(1.0, 0.0)
        self.y_axis = y_axis if y_axis is not None else Vector(0.0, 1.0)
    
    def Copy(self):
        return LinearTransform(self.x_axis.Copy(), self.y_axis.Copy())
    
    def Serialize(self):
        json_data = {
            'x_axis': self.x_axis.Serialize(),
            'y_axis': self.y_axis.Serialize()
        }
        return json_data

    def Deserialize(self, json_data):
        self.x_axis = Vector().Deserialize(json_data['x_axis'])
        self.y_axis = Vector().Deserialize(json_data['y_axis'])
        return self
    
    def IsTransform(self, transform, epsilon=1e-7):
        return self.x_axis.IsPoint(transform.x_axis, epsilon) and self.y_axis.IsPoint(transform.y_axis, epsilon)
    
    def Identity(self):
        self.x_axis = Vector(1.0, 0.0)
        self.y_axis = Vector(0.0, 1.0)
    
    def Transform(self, object):
        if isinstance(object, Vector):
            return self.x_axis * object.x + self.y_axis * object.y
        elif isinstance(object, LinearTransform):
            transform = LinearTransform()
            transform.x_axis = self.Transform(object.x_axis)
            transform.y_axis = self.Transform(object.y_axis)
            return transform
    
    def __call__(self, object):
        return self.Transform(object)
    
    def __mul__(self, other):
        return self.Transform(other)
    
    def Determinant(self):
        return self.x_axis.Cross(self.y_axis)
    
    def Invert(self):
        inverse = self.Inverted()
        if inverse is None:
            return False
        else:
            self.x_axis = inverse.x_axis
            self.y_axis = inverse.y_axis
            return True
    
    def Inverted(self):
        try:
            det = self.Determinant()
            inverse = LinearTransform()
            scale = 1.0 / det
            inverse.x_axis = Vector(self.y_axis.y, -self.x_axis.y) * scale
            inverse.y_axis = Vector(-self.y_axis.x, self.x_axis.x) * scale
            return inverse
        except ZeroDivisionError:
            return None
    
    def Rotation(self, angle):
        self.Identity()
        self.x_axis = self.x_axis.Rotated(angle)
        self.y_axis = self.y_axis.Rotated(angle)
    
    def Reflection(self, vector):
        self.Identity()
        self.x_axis = self.x_axis.Reflected(vector)
        self.y_axis = self.y_axis.Reflected(vector)

    def Scale(self, x_scale, y_scale):
        self.x_axis = Vector(x_scale, 0.0)
        self.y_axis = Vector(0.0, y_scale)

    def Decompose(self):
        pass