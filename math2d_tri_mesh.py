# math2d_tri_mesh.py

import copy
import random

from math2d_vector import Vector
from math2d_triangle import Triangle

class TriangleMesh(object):
    # These are lists of triangles.  Each triangle is an integer-triple,
    # each integer an index into the stored vertex list.
    def __init__(self):
        self.vertex_list = []
        self.triangle_list = []
    
    def Copy(self):
        return copy.deepcopy(self)
    
    def Serialize(self):
        json_data = {
            'vertex_list': [vertex.Serialize() for vertex in self.vertex_list],
            'triangle_list': [triple for triple in self.triangle_list]
        }
        return json_data
    
    def Deserialize(self, json_data):
        self.vertex_list = [Vector().Deserialize(vertex) for vertex in json_data['vertex_list']]
        self.triangle_list = [(triple[0], triple[1], triple[2]) for triple in json_data['triangle_list']]
    
    def MakeTriangleFromTriple(self, triple):
        vertex_a = self.vertex_list[triple[0]]
        vertex_b = self.vertex_list[triple[1]]
        vertex_c = self.vertex_list[triple[2]]
        return Triangle(vertex_a, vertex_b, vertex_c)
    
    def Area(self):
        area = 0.0
        for triple in self.triangle_list:
            triangle = self.MakeTriangleFromTriple(triple)
            area += triangle.Area()
        return area
    
    def ContainsPoint(self, point, epsilon=1e-7):
        for triple in self.triangle_list:
            triangle = self.MakeTriangleFromTriple(triple)
            if triangle.ContainsPoint(point, epsilon):
                return True
        return False
    
    def FindOrAddVertex(self, given_vertex, epsilon=1e-7):
        for i, vertex in enumerate(self.vertex_list):
            if given_vertex.IsPoint(vertex, epsilon):
                return i
        else:
            self.vertex_list.append(given_vertex)
            return len(self.vertex_list) - 1
    
    def FindOrAddTriangleTriple(self, given_triple):
        for i, triple in enumerate(self.triangle_list):
            if given_triple == triple:
                return i
        else:
            self.triangle_list.append(given_triple)
            return len(self.triangle_list) - 1
    
    def AddTriangle(self, triangle):
        triangle.FixWindingIfNecessary()
        triple = (
            self.FindOrAddVertex(triangle.Vertex(0)),
            self.FindOrAddVertex(triangle.Vertex(1)),
            self.FindOrAddVertex(triangle.Vertex(2))
        )
        self.FindOrAddTriangleTriple(triple)
    
    def GenerateTriStrip(self): # TODO: Test this.  I'm sure it needs fixes.
        triangle_sequence = []
        i = 0 # This is our current triangle.
        j = 0 # This indicates how we entered the current triangle.
        while True:
            triangle_sequence.append(i)
            triple_a = self.triangle_list[i]
            # The correctness of our algorithms depends on a consistent ordering
            # here of the edges that we're trying to exit through.  This in turn
            # depends on a consistent winding (CCW) of all mesh triangles.
            desired_edge_list = [(triple_a[(j - 1) % 3], triple_a[j]), (triple_a[j], triple_a[(j + 1) % 3])]
            if i == 0:
                desired_edge_list.append(triple_a[(j + 1) % 3], triple_a[(j + 2) % 3])
            found = False
            for desired_edge in desired_edge_list:
                for k in range(len(self.triangle_list)):
                    if not any([k == x for x in triangle_sequence]):
                        triple_b = self.triangle_list[k]
                        shared_edge = self._SharedEdge(triple_a, triple_b)
                        if shared_edge is not None and shared_edge == desired_edge:
                            i = k
                            j = self._FindVertexComplementaryToEdge(triple_b, desired_edge)
                            found = True
                            break
                if found:
                    break
            if not found:
                break
        if len(triangle_sequence) < len(self.triangle_list):
            raise Exception('Failed to tri-strip mesh.')
        tri_strip_sequence = []
        for i in range(len(triangle_sequence) - 1):
            triple_a = self.triangle_list[triangle_sequence[i]]
            triple_b = self.triangle_list[triangle_sequence[i + 1]]
            edge = self._SharedEdge(triple_a, triple_b)
            if i == 0:
                j = self._FindVertexComplementaryToEdge(triple_a, edge)
                tri_strip_sequence.append(triple_a[j])
                tri_strip_sequence.append(triple_a[(j + 1) % 3])
                tri_strip_sequence.append(triple_a[(j + 2) % 3])
            j = self._FindVertexComplementaryToEdge(triple_b, edge)
            tri_strip_sequence.append(triple_b[j])
        return tri_strip_sequence
    
    def _SharedEdge(self, triple_a, triple_b):
        for i in range(3):
            edge_a = (triple_a[i], triple_b[(i + 1) % 3])
            for j in range(3):
                edge_b = (triple_b[(j + 1) % 3], triple_b[j])
                if edge_a == edge_b:
                    return edge_a
        return None
    
    def _FindVertexComplementaryToEdge(self, triple, edge):
        for i in range(3):
            if triple[i] != edge[0] and triple[i] != edge[1]:
                return i
        return None
    
    def Render(self, tri_strip_sequence=None):
        if tri_strip_sequence is None:
            for triple in self.triangle_list:
                triangle = self.MakeTriangleFromTriple(triple)
                triangle.Render()
        else:
            from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_TRIANGLE_STRIP
            glBegin(GL_TRIANGLE_STRIP)
            try:
                for i in tri_strip_sequence:
                    point = self.vertex_list[i]
                    glVertex2f(point.x, point.y)
            finally:
                glEnd()