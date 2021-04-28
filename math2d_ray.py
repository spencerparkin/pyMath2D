# math2d_ray.py

from math2d_vector import Vector
from math2d_circle import Circle
from math2d_line_segment import LineSegment
from math2d_polygon import Polygon

class Ray(object):
    def __init__(self, point=None, normal=None):
        self.point = point if point is not None else Vector(0.0, 0.0)
        self.normal = normal if normal is not None else Vector(1.0, 0.0)
    
    def Copy(self):
        return Ray(self.point.Copy(), self.normal.Copy())

    def EvalParam(self, param):
        return self.point + self.normal * param

    def CalcParam(self, given_point):
        # If the given point is not on this ray, then the result here is the
        # parameter of the nearest point on the ray to the given point.  If the
        # given point is on the ray, then the result here is the parameter of
        # that point on the ray.
        return (given_point - self.point).Dot(self.normal)

    def CastAgainst(self, other, cast_distance=1000.0):
        if isinstance(other, Circle):
            pass
        elif isinstance(other, LineSegment):
            ray_segment = LineSegment(point_a=self.point, point_b=self.EvalParam(cast_distance))
            hit_point = ray_segment.IntersectWith(other)
            if hit_point is not None:
                return self.CalcParam(hit_point)
        elif isinstance(other, Ray):
            pass
        elif isinstance(other, Polygon):
            pass
        elif type(other) is list:
            smallest_hit = None
            for item in other:
                hit = self.CastAgainst(item)
                if hit is not None and hit >= 0.0 and (smallest_hit is None or hit < smallest_hit):
                    smallest_hit = hit
            return smallest_hit

    def Point(self, scale):
        return self.point + self.normal * scale