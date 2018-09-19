# math2d_aa_rect.py

import copy

from math2d_vector import Vector
from math2d_line_segment import LineSegment

class AxisAlignedRectangle(object):
    def __init__(self, min_point=None, max_point=None):
        self.min_point = min_point if min_point is not None else Vector(0.0, 0.0)
        self.max_point = max_point if max_point is not None else Vector(0.0, 0.0)

    def Clone(self):
        return copy.deepcopy(self)
    
    def Serialize(self):
        json_data = {
            'min_point': self.min_point.Serialize(),
            'max_point': self.max_point.Serialize()
        }
        return json_data

    def Deserialize(self, json_data):
        self.min_point = Vector().Deserialize(json_data['min_point'])
        self.max_point = Vector().Deserialize(json_data['max_point'])
        return self
    
    def CalcUVs(self, point):
        u = (point.x - self.min_point.x) / (self.max_point.x - self.min_point.x)
        v = (point.y - self.min_point.y) / (self.max_point.y - self.min_point.y)
        return u, v

    def ApplyUVs(self, u, v):
        x = self.min_point.x + u * (self.max_point.x - self.min_point.x)
        y = self.min_point.y + v * (self.max_point.y - self.min_point.y)
        return Vector(x, y)

    def Map(self, thing, rectangle):
        if isinstance(thing, Vector):
            u, v = self.CalcUVs(thing)
            return rectangle.ApplyUVs(u, v)
        elif isinstance(thing, LineSegment):
            return LineSegment(self.Map(thing.point_a, rectangle), self.Map(thing.point_b, rectangle))

    def Width(self):
        return self.max_point.x - self.min_point.x

    def Height(self):
        return self.max_point.y - self.min_point.y

    def Area(self):
        return self.Width() * self.Height()

    def AspectRatio(self):
        return self.Width() / self.Height()

    def ExpandToMatchAspectRatioOf(self, rectangle):
        aspect_ratio_a = self.AspectRatio()
        aspect_ratio_b = rectangle.AspectRatio()
        if aspect_ratio_a > aspect_ratio_b:
            delta_height = (rectangle.Height() * self.Width() / rectangle.Width() - self.Height()) / 2.0
            self.min_point.y -= delta_height
            self.max_point.y += delta_height
        else:
            delta_width = (rectangle.Width() * self.Height() / rectangle.Height() - self.Width()) / 2.0
            self.min_point.x -= delta_width
            self.min_point.x += delta_width

    def ContractToMatchAspectRatioOf(self, rectangle):
        aspect_ratio_a = self.AspectRatio()
        aspect_ratio_b = rectangle.AspectRatio()
        if aspect_ratio_a > aspect_ratio_b:
            delta_width = (self.Width() - rectangle.Width() * self.Height() / rectangle.Height()) / 2.0
            self.min_point.x += delta_width
            self.max_point.x -= delta_width
        else:
            delta_height = (self.Height() - rectangle.Height() * self.Width() / rectangle.Width()) / 2.0
            self.min_point.y += delta_height
            self.max_point.y -= delta_height

    def Center(self):
        return LineSegment(self.min_point, self.max_point).Lerp(0.5)

    def GrowFor(self, object):
        from math2d_polygon import Polygon
        from math2d_region import Region, SubRegion
        from math2d_planar_graph import PlanarGraph
        if isinstance(object, Vector):
            # Minimally grow the rectangle to include the given point.
            if self.min_point.x > object.x:
                self.min_point.x = object.x
            if self.max_point.x < object.x:
                self.max_point.x = object.x
            if self.min_point.y > object.y:
                self.min_point.y = object.y
            if self.max_point.y < object.y:
                self.max_point.y = object.y
        elif isinstance(object, Polygon):
            for vertex in object.vertex_list:
                self.GrowFor(vertex)
        elif isinstance(object, Region):
            for sub_region in object.sub_region_list:
                self.GrowFor(sub_region)
        elif isinstance(object, SubRegion):
            self.GrowFor(object.polygon)
        elif isinstance(object, PlanarGraph):
            for edge_segment in object.GenerateEdgeSegments():
                self.GrowFor(edge_segment)
        elif isinstance(object, LineSegment):
            self.GrowFor(object.point_a)
            self.GrowFor(object.point_b)
        elif isinstance(object, AxisAlignedRectangle):
            self.GrowFor(object.GeneratePolygon())
        else:
            raise Exception('Failed to grow for "%s"' + str(object))

    def Scale(self, scale_factor):
        center = self.Center()
        max_vector = self.max_point - center
        min_vector = self.min_point - center
        max_vector = max_vector.Scaled(scale_factor)
        min_vector = min_vector.Scaled(scale_factor)
        self.max_point = center + max_vector
        self.min_point = center + min_vector

    def GeneratePolygon(self):
        from math2d_polygon import Polygon
        polygon = Polygon()
        polygon.vertex_list.append(Vector(self.min_point.x, self.min_point.y))
        polygon.vertex_list.append(Vector(self.max_point.x, self.min_point.y))
        polygon.vertex_list.append(Vector(self.max_point.x, self.max_point.y))
        polygon.vertex_list.append(Vector(self.min_point.x, self.max_point.y))
        return polygon