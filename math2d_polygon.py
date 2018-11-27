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
        json_data = {
            'vertex_list': [vertex.Serialize() for vertex in self.vertex_list]
        }
        return json_data

    def Deserialize(self, json_data):
        self.vertex_list = [Vector().Deserialize(vertex) for vertex in json_data['vertex_list']]
        return self

    def AverageVertex(self):
        avg_vertex = Vector(0.0, 0.0)
        for vertex in self.vertex_list:
            avg_vertex += vertex
        avg_vertex = avg_vertex / float(len(self.vertex_list))
        return avg_vertex

    def MakeRegularPolygon(self, sides, radius=1.0, center=None):
        for i in range(sides):
            point = Vector(angle=2.0 * math.pi * float(i) / float(sides), radius=radius)
            if center is None:
                self.vertex_list.append(point)
            else:
                self.vertex_list.append(point + center)
        return self
    
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
        from math2d_point_cloud import PointCloud
        point_cloud = PointCloud()
        point_cloud.Add(self)
        for line in self.GenerateLines():
            point_cloud_back, point_cloud_front, point_cloud_neither = point_cloud.Split(line)
            if point_cloud_back.Size() > 0 and point_cloud_front.Size() > 0:
                return True
        return False
    
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
    
    def ContainsPoint(self, point, epsilon=1e-7, assume_convex=False):
        if assume_convex:
            from math2d_line import Line
            for line in self.GenerateLines():
                side = line.CalcSide(point, epsilon)
                if side != Line.SIDE_FRONT:
                    return False
            return True
        elif self.mesh is not None:
            return self.mesh.ContainsPoint(point, epsilon)
        else:
            raise Exception('Can\'t determine if polygon contains point.')

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

    def GenerateLines(self):
        # Note that the front of the line will be outside the polygon,
        # and the back of the line will be inside the polygon.
        # This doesn't quite hold in some self-tangential cases, but...
        from math2d_line import Line
        for i in range(len(self.vertex_list)):
            j = (i + 1) % len(self.vertex_list)
            line = Line()
            line.MakeForPoints(self.vertex_list[j], self.vertex_list[i])
            yield line

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
    
    def IntersectWith(self, polygon):
        from math2d_planar_graph import PlanarGraph
        polygon_list = []
        self.Tessellate()
        graph = PlanarGraph()
        graph.Add(polygon)
        graph.Add(self, disposition={'replace_edges': True})
        while True:
            for i, vertex in enumerate(graph.vertex_list):
                if self.ContainsPoint(vertex) and polygon.ContainsPoint(vertex):
                    break
            else:
                break
            intersect_polygon = Polygon()
            polygon_list.append(intersect_polygon)
            visited_vertices = set()
            while True:
                visited_vertices.add(i)
                vertex = graph.vertex_list[i]
                intersect_polygon.vertex_list.append(vertex)
                adjacency_list = graph.FindAllAdjacencies(i, ignore_direction=True, vertices=True)
                for i in adjacency_list:
                    if i not in visited_vertices:
                        vertex = graph.vertex_list[i]
                        if self.ContainsPoint(vertex) and polygon.ContainsPoint(vertex):
                            break
                else:
                    break
            if not intersect_polygon.IsWoundCCW():
                intersect_polygon.ReverseWinding()
            for vertex in intersect_polygon.vertex_list:
                graph.RemoveVertex(vertex)
        return polygon_list
    
    def Render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_LINE_LOOP
        glBegin(GL_LINE_LOOP)
        try:
            for i in range(len(self.vertex_list)):
                point = self.vertex_list[i]
                glVertex2f(point.x, point.y)
        finally:
            glEnd()