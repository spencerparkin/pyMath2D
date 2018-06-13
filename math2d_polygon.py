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

    def AverageVertex(self):
        avg_vertex = Vector(0.0, 0.0)
        for vertex in self.vertex_list:
            avg_vertex += vertex
        avg_vertex = avg_vertex / float(len(self.vertex_list))
        return avg_vertex

    def MakeRegularPolygon(self, sides, radius=1.0):
        for i in range(sides):
            point = Vector(angle=2.0 * math.pi * float(i) / float(sides), radius=radius)
            self.vertex_list.append(point)
    
    def Tessellate(self):
        # Note that it is up to the caller to know when and if we need to recalculate this mesh, which some methods depend upon.
        from math2d_tri_mesh import TriangleMesh
        self.mesh = TriangleMesh()
        self._Tessellate(self.mesh)
    
    def _Tessellate(self, given_mesh):
        self.RemoveRedundantVertices()
        if len(self.vertex_list) < 3:
            return
        elif len(self.vertex_list) == 3:
            triangle = Triangle(self.vertex_list[0], self.vertex_list[1], self.vertex_list[2])
            given_mesh.AddTriangle(triangle)
        else:
            candidate_list = []
            for i in range(len(self.vertex_list)):
                for j in range(i + 1, len(self.vertex_list)):
                    if (i + 1) % len(self.vertex_list) != j and (i - 1) % len(self.vertex_list) != j:
                        candidate_list.append((i, j))
            # The idea here is that we might get better tessellations if we try the candidates in this order.
            candidate_list.sort(key=lambda pair: (self.vertex_list[pair[1]] - self.vertex_list[pair[0]]).Length(), reverse=True)
            for pair in candidate_list:
                i = pair[0]
                j = pair[1]
                line_segment = LineSegment(self.vertex_list[i], self.vertex_list[j])
                try:
                    for k in range(len(self.vertex_list)):
                        if k != i and k != j:
                            if line_segment.ContainsPoint(self.vertex_list[k]):
                                raise Exception()
                        if k != i and (k + 1) % len(self.vertex_list) != i:
                            if k != j and (k + 1) % len(self.vertex_list) != j:
                                edge_segment = LineSegment(self.vertex_list[k], self.vertex_list[(k + 1) % len(self.vertex_list)])
                                point = edge_segment.IntersectWith(line_segment)
                                if point is not None:
                                    raise Exception()
                    polygon_a = Polygon()
                    k = 0
                    while True:
                        r = (j + k) % len(self.vertex_list)
                        polygon_a.vertex_list.append(self.vertex_list[r])
                        if r == i:
                            break
                        k += 1
                    if polygon_a.IsWoundCW():
                        raise Exception()
                    polygon_b = Polygon()
                    k = 0
                    while True:
                        r = (i + k) % len(self.vertex_list)
                        polygon_b.vertex_list.append(self.vertex_list[r])
                        if r == j:
                            break
                        k += 1
                    if polygon_b.IsWoundCW():
                        raise Exception()
                except:
                    pass
                else:
                    polygon_a._Tessellate(given_mesh)
                    polygon_b._Tessellate(given_mesh)
                    break
            else:
                raise Exception('Failed to tessellate polygon!')
    
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