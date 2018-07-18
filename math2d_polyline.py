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
        self.vertex_list = [Vector().Deserialize(vertex) for vertex in json_data['vertex_list']]
        return self
    
    # TODO: Write stuff...