# math2d_line.py

import math

from math2d_vector import Vector

class LineSide:
    NEITHER = 0
    FRONT = 1
    BACK = 2

class Line(object):
    # Unlike a ray, the normal points orthogonal (perpendicular) to the line, not parallel to it.
    # Unlike a line-segment, these have infinite length, like a ray.  Rays are for hitting, while
    # these are the 2-dimensional analog of planes in 3D space that have front and back spaces.
    def __init__(self, center, normal):
        self.center = center if center is not None else Vector(0.0, 0.0)
        self.normal = normal if normal is not None else Vector(1.0, 0.0)
    
    def SignedDistance(self, point):
        vector = point - self.center
        return self.normal.Dot(vector)
    
    def Distance(self, point):
        return math.fabs(self.SignedDistance(point))
    
    def CalcSide(self, point, epsilon=1e-7):
        distance = self.SignedDistance(point)
        if math.fabs(distance) <= epsilon:
            return LineSide.NEITHER
        if distance < 0.0:
            return LineSide.BACK
        return LineSide.FRONT