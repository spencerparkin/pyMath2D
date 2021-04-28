# math2d_polyline.py

import copy
import math

from math2d_vector import Vector
from math2d_triangle import Triangle
from math2d_line_segment import LineSegment

class Polyline(object):
    def __init__(self):
        self.vertex_list = []

    def Copy(self):
        return copy.deepcopy(self)

    def Serialize(self):
        json_data = {
            'vertex_list': [vertex.Serialize() for vertex in self.vertex_list]
        }
        return json_data

    def Deserialize(self, json_data):
        self.vertex_list = [Vector().Deserialize(vertex) for vertex in json_data.get('vertex_list', [])]
        return self

    def Render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_LINE_STRIP
        glBegin(GL_LINE_STRIP)
        try:
            for i in range(len(self.vertex_list)):
                point = self.vertex_list[i]
                glVertex2f(point.x, point.y)
        finally:
            glEnd()

    def GenerateLineSegments(self):
        for i in range(len(self.vertex_list) - 1):
            yield LineSegment(point_a=self.vertex_list[i], point_b=self.vertex_list[i + 1])

    def Length(self):
        total_length = 0.0
        for i in range(len(self.vertex_lsit) - 1):
            total_length += (self.vertex_list[i + 1] - self.vertex_list[i]).Length()
        return total_length