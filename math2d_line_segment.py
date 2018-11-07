# math2d_line_segment.py

import math

from math2d_vector import Vector

class LineSegment(object):
    def __init__(self, point_a=None, point_b=None):
        self.point_a = point_a if point_a is not None else Vector(0.0, 0.0)
        self.point_b = point_b if point_b is not None else Vector(0.0, 0.0)
    
    def Copy(self):
        return LineSegment(self.point_a.Copy(), self.point_b.Copy())
    
    def Direction(self):
        return self.point_b - self.point_a
    
    def Length(self):
        return self.Direction().Length()
    
    def Lerp(self, lerp_value):
        return self.point_a + (self.point_b - self.point_a) * lerp_value
    
    def LerpValue(self, point, epsilon=1e-7):
        try:
            vector_a = self.point_b - self.point_a
            vector_b = point - self.point_a
            cross = vector_a.Cross(vector_b)
            if math.fabs(cross) >= epsilon:
                return None
            lerp_value = vector_a.Dot(vector_b) / vector_a.Dot(vector_a)
            return lerp_value
        except ZeroDivisionError:
            return None
    
    def ContainsPoint(self, point, epsilon=1e-7):
        lerp_value = self.LerpValue(point, epsilon)
        if lerp_value is None:
            return False
        return True if -epsilon < lerp_value < 1.0 + epsilon else False
    
    def IsEndPoint(self, point, epsilon=1e-7):
        return self.point_a.IsPoint(point, epsilon) or self.point_b.IsPoint(point, epsilon)

    def IntersectWith(self, other, epsilon=1e-7):
        if isinstance(other, LineSegment):
            numer_a = (other.point_b - other.point_a).Cross(self.point_a - other.point_a)
            numer_b = (self.point_b - self.point_a).Cross(other.point_a - self.point_a)
            denom = (self.point_b - self.point_a).Cross(other.point_b - other.point_a)
            try:
                lerp_value_a = numer_a / denom
                lerp_value_b = numer_b / -denom
            except ZeroDivisionError:
                return None
            if -epsilon <= lerp_value_a <= 1.0 + epsilon and -epsilon <= lerp_value_b <= 1.0 + epsilon:
                point = self.Lerp(lerp_value_a)
                # Let's scrutinize further.  Two disjoint and parallel line segments sometimes warrant this.
                if self.ContainsPoint(point, epsilon) and other.ContainsPoint(point, epsilon):
                    return point
                else:
                    return None
    
    def Distance(self, point):
        return (point - self.ClosestPoint(point)).Length()
    
    def ClosestPoint(self, point):
        vector = (self.point_b - self.point_a).Normalized()
        length = (point - self.point_a).Dot(vector)
        if length < 0.0:
            return self.point_a
        elif length > self.Length():
            return self.point_b
        else:
            return self.point_a + vector * length