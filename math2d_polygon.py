# math2d_polygon.py

import copy

from math2d_triangle import Triangle

class Polygon(object):
    # These are lists of points with CCW winding in the plane.  It is a bit hard to
    # rigorously define exactly what is and is not a valid polygon.
    # Intuitively, the polygon must wrap a non-self-overlapping area of the plane,
    # and not self-intersect itself.  We do, however, allow them to be self-tangential.
    # You might say that this is a special case of the sub-region class.  Specifically,
    # these are sub-regions without any holes.  Unlike sub-regions, however, we must
    # enforce a CCW winding in the plane.
    def __init__(self):
        self.vertex_list = []
    
    def Copy(self):
        return copy.deepcopy(self)
    
    def Tessellate(self):
        from math2d_tri_mesh import TriangleMesh
        mesh = TriangleMesh()
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
                    mesh.AddTriangle(triangle)
                    del polygon.vertex_list[(i + 1) % len(polygon.vertex_list)]
                    break
            if not found:
                raise Exception('Failed to tessellate polygon.')
        return mesh
    
    def IsConvex(self):
        return not self.IsConcave()
    
    def IsConcave(self):
        pass # TODO: Can we find an edge who's line is straddled by the polygon?
    
    def RemoveRedundantVertices(self):
        # A vertex is redundant if it is on what could be an edge of the polygon.
        pass
    
    def Area(self):
        mesh = self.Tesselate()
        return mesh.Area()
    
    def ContainsPoint(self, point, epsilon=1e-7):
        # This shouldn't be called repeatedly on a static polygon.
        mesh = self.Tessellate()
        return mesh.ContainsPoint(point, epsilon)
    
    def Transform(self, transform):
        for i, point in enumerate(self.vertex_list):
            self.vertex_list[i] = transform.Transform(point)
        det = transform.Determinant()
        if det < 0.0:
            self.ReverseWinding()
    
    def ReverseWinding(self):
        self.vertex_list = [point for point in reversed(self.vertex_list)]
    
    def Render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_LINE_LOOP
        glBegin(GL_LINE_LOOP)
        try:
            for i in range(len(self.vertex_list)):
                point = self.vertex_list[i]
                glVertex2f(point.x, point.y)
        finally:
            glEnd()