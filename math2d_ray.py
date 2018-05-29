# math2d_ray.py

from math2d_vector import Vector
from math2d_circle import Circle
from math2d_line_segment import LineSegment

class Ray(object):
    def __init__(self, point=None, normal=None):
        self.point = point if point is not None else Vector(0.0, 0.0)
        self.normal = normal if normal is not None else Vector(1.0, 0.0)
    
    def Copy(self):
        return Ray(self.point.Copy(), self.normal.Copy())
    
    def CastAgainst(self, other):
        if isinstance(other, Circle):
            pass
        if isinstance(other, LineSegment):
            pass