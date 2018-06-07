# math2d_polygon.py

import copy
import math

from math2d_vector import Vector
from math2d_triangle import Triangle
from math2d_line_segment import LineSegment

class Polygon(object):
    # These are lists of points with CCW winding in the plane.
    # The path of the polygon's perimeter must not cross itself, but we do allow polygons to be self-tangential.
    # If the vertex list does not satisfy these requirements, then the result of any method is left undefined.
    def __init__(self):
        self.vertex_list = []
        self.mesh = None
    
    def Copy(self):
        return copy.deepcopy(self)
    
    def Serialize(self):
        pass

    def Deserialize(self, json_data):
        pass
    
    def MakeRegularPolygon(self, sides, radius=1.0):
        for i in range(sides):
            point = Vector(angle=2.0 * math.pi * float(i) / float(sides), radius=radius)
            self.vertex_list.append(point)
    
    def Tessellate(self):
        # Note that it is up to the caller to know when and if we need to recalculate this mesh, which some methods depend upon.
        from math2d_tri_mesh import TriangleMesh
        self.mesh = TriangleMesh()
        polygon = self.Copy()
        while True:
            polygon.RemoveRedundantVertices()
            if len(polygon.vertex_list) < 3:
                break
            found = False
            for i in range(len(polygon.vertex_list)):
                j = (i + 1) % len(polygon.vertex_list)
                k = (i + 2) % len(polygon.vertex_list)
                vertex_a = polygon.vertex_list[i]
                vertex_b = polygon.vertex_list[j]
                vertex_c = polygon.vertex_list[k]
                triangle = Triangle(vertex_a, vertex_b, vertex_c)
                if triangle.Area() > 0.0:
                    for vertex in self.vertex_list:
                        if triangle.ContainsPoint(vertex) and not triangle.ContainsPointOnBorder(vertex):
                            break
                    else:
                        found = True
                if found:
                    self.mesh.AddTriangle(triangle)
                    del polygon.vertex_list[j]
                    break
            if not found:
                raise Exception('Failed to tessellate polygon.')
    
    def IsConvex(self):
        return not self.IsConcave()
    
    def IsConcave(self):
        pass # TODO: Can we find an edge who's line is straddled by the polygon?
    
    def RemoveRedundantVertices(self, epsilon=1e-7):
        if len(self.vertex_list) >= 3:
            while True:
                found = None
                for j in range(len(self.vertex_list)):
                    i = (j - 1) % len(self.vertex_list)
                    k = (j + 1) % len(self.vertex_list)
                    vertex_a = self.vertex_list[i]
                    vertex_b = self.vertex_list[j]
                    vertex_c = self.vertex_list[k]
                    triangle = Triangle(vertex_a, vertex_b, vertex_c)
                    if math.fabs(triangle.Area()) <= epsilon:
                        found = j
                        break
                if found is None:
                    break
                else:
                    del self.vertex_list[found]
    
    def Area(self):
        return self.mesh.Area()
    
    def ContainsPoint(self, point, epsilon=1e-7):
        return self.mesh.ContainsPoint(point, epsilon)

    def ContainsPointOnBorder(self, point, epsilon=1e-7):
        for line in self.GenerateLineSegments():
            if line.ContainsPoint(point, epsilon):
                return True
        return False
    
    def Transform(self, transform, preserve_winding=True):
        for i, point in enumerate(self.vertex_list):
            self.vertex_list[i] = transform.Transform(point)
        if preserve_winding:
            det = transform.Determinant()
            if det < 0.0:
                self.ReverseWinding()
    
    def ReverseWinding(self):
        self.vertex_list = [point for point in reversed(self.vertex_list)]
    
    def IsWoundCCW(self, epsilon=1e-7):
        if len(self.vertex_list) <= 2:
            return None
        net_angle = 0.0
        for i in range(len(self.vertex_list)):
            j = (i + 1) % len(self.vertex_list)
            k = (i + 2) % len(self.vertex_list)
            vector_a = self.vertex_list[j] - self.vertex_list[i]
            vector_b = self.vertex_list[k] - self.vertex_list[j]
            net_angle += vector_a.SignedAngleBetween(vector_b)
        if math.fabs(net_angle - 2.0 * math.pi) < epsilon:
            return True
        elif math.fabs(net_angle + 2.0 * math.pi) < epsilon:
            return False
        return None

    def IsWoundCW(self):
        return not self.IsWoundCCW()
    
    def GenerateLineSegments(self):
        for i in range(len(self.vertex_list)):
            j = (i + 1) % len(self.vertex_list)
            line_segment = LineSegment(self.vertex_list[i], self.vertex_list[j])
            yield line_segment
    
    def IsSymmetry(self, transform):
        polygon = transform * self
        for vertex in self.vertex_list:
            i = polygon.FindVertex(vertex)
            if i is None:
                return False
            del polygon.vertex_list[i]
        return True
    
    def FindVertex(self, given_vertex, epsilon=1e-7):
        for i, vertex in enumerate(self.vertex_list):
            if vertex.IsPoint(given_vertex, epsilon):
                return i
        return None
    
    def Render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_LINE_LOOP
        glBegin(GL_LINE_LOOP)
        try:
            for i in range(len(self.vertex_list)):
                point = self.vertex_list[i]
                glVertex2f(point.x, point.y)
        finally:
            glEnd()