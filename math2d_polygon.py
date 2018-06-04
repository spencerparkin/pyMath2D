# math2d_polygon.py

import copy

from math2d_triangle import Triangle
from math2d_line_segment import LineSegment

class Polygon(object):
    # These are lists of points with CCW winding in the plane.
    # The path of the polygon's permimeter must not cross itself, but we do allow polygons to be self-tangential.
    # If the vertex list does not satisfy these requirements, then any result of any method is left undefined.
    def __init__(self):
        self.vertex_list = []
        self.mesh = None
    
    def Copy(self):
        return copy.deepcopy(self)
    
    def Tessellate(self):
        from math2d_tri_mesh import TriangleMesh
        self.mesh = TriangleMesh()
        polygon = self.Copy()
        while len(polygon.vertex_list) > 2:
            found = False
            for i in range(len(polygon.vertex_list)):
                vertex_a = polygon.vertex_list[i]
                vertex_b = polygon.vertex_list[(i + 1) % len(polygon.vertex_list)]
                vertex_c = polygon.vertex_list[(i + 2) % len(polygon.vertex_list)]
                triangle = Triangle(vertex_a, vertex_b, vertex_c)
                if triangle.Area() > 0.0:
                    for vertex in self.vertex_list:
                        if triangle.ContainsPoint(vertex):
                            break
                else:
                    pass # What else?
                    found = True
                if found:
                    self.mesh.AddTriangle(triangle)
                    del polygon.vertex_list[(i + 1) % len(polygon.vertex_list)]
                    break
            if not found:
                raise Exception('Failed to tessellate polygon.')
    
    def IsConvex(self):
        return not self.IsConcave()
    
    def IsConcave(self):
        pass # TODO: Can we find an edge who's line is straddled by the polygon?
    
    def RemoveRedundantVertices(self):
        # A vertex is redundant if it is on what could be an edge of the polygon.
        pass
    
    def Area(self):
        return self.mesh.Area()
    
    def ContainsPoint(self, point, epsilon=1e-7):
        return self.mesh.ContainsPoint(point, epsilon)
    
    def Transform(self, transform):
        for i, point in enumerate(self.vertex_list):
            self.vertex_list[i] = transform.Transform(point)
        det = transform.Determinant()
        if det < 0.0:
            self.ReverseWinding()
    
    def ReverseWinding(self):
        self.vertex_list = [point for point in reversed(self.vertex_list)]
    
    def GenerateLineSegments(self):
        for i in range(len(self.vertex_list)):
            j = (i + 1) % len(self.vertex_list)
            line_segment = LineSegment(self.vertex_list[i], self.vertex_list[j])
            yield line_segment
    
    def Render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_LINE_LOOP
        glBegin(GL_LINE_LOOP)
        try:
            for i in range(len(self.vertex_list)):
                point = self.vertex_list[i]
                glVertex2f(point.x, point.y)
        finally:
            glEnd()