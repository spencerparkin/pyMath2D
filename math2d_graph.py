# math2d_graph.py

from math2d_vector import Vector
from math2d_planar_graph import PlanarGraph
from math2d_line_segment import LineSegment

class GraphVertex(object):
    def __init__(self, point):
        self.point = point.Copy()
        self.adjacency_list = []

    def Degree(self):
        return len(self.adjacency_list)

    def AddAdjacency(self, vertex):
        for i in range(len(self.adjacency_list)):
            if self.adjacency_list[i] == vertex:
                break
        else:
            self.adjacency_list.append(vertex)

    def RemoveAdjacency(self, vertex):
        for i in range(len(self.adjacency_list)):
            if self.adjacency_list[i] == vertex:
                del self.adjacency_list[i]
                break

class Graph(object):
    # These are undirected graphs that need not be planar.
    def __init__(self):
        self.vertex_list = []

    def FromPlanarGraph(self, planar_graph):
        self.vertex_list = [GraphVertex(vertex) for vertex in planar_graph.vertex_list]
        for edge in planar_graph.edge_list:
            vertex_a = self.vertex_list[edge[0]]
            vertex_b = self.vertex_list[edge[1]]
            vertex_a.adjacency_list.append(vertex_b)
            vertex_b.adjacency_list.append(vertex_a)

    def ToPlanarGraph(self):
        planar_graph = PlanarGraph()
        for edge_segment in self.GenerateEdgeSegments():
            planar_graph.Add(edge_segment)
        return planar_graph

    def GenerateEdgeSegments(self):
        edge_set = set()
        for vertex in self.vertex_list:
            key_a = hex(id(vertex))
            for adjacent_vertex in vertex.adjacency_list:
                key_b = hex(id(adjacent_vertex))
                key = key_a + key_b if key_a < key_b else key_b + key_a
                if key not in edge_set:
                    edge_set.add(key)
                    yield LineSegment(point_a=vertex.point, point_b=adjacent_vertex.point)

    def IsAcyclic(self):
        pass

    def FindVertex(self, point):
        for i, vertex in enumerate(self.vertex_list):
            if vertex.point.IsPoint(point):
                return i

    def Disconnect(self, i, j):
        vertex_a = self.vertex_list[i]
        vertex_b = self.vertex_list[j]
        vertex_a.RemoveAdjacency(vertex_b)
        vertex_b.RemoveAdjacency(vertex_a)

    def Connect(self, i, j):
        vertex_a = self.vertex_list[i]
        vertex_b = self.vertex_list[j]
        vertex_a.AddAdjacency(vertex_b)
        vertex_b.AddAdjacency(vertex_a)

    def RemoveArea(self, convex_polygon, assume_convex=True):
        disconnect_list = []
        new_edge_segment_list = []
        for edge_segment in self.GenerateEdgeSegments():
            in_list, out_list = convex_polygon.SplitLineSegment(edge_segment, assume_convex=assume_convex)
            if len(in_list) > 0:
                i = self.FindVertex(edge_segment.point_a)
                j = self.FindVertex(edge_segment.point_b)
                disconnect_list.append((i, j))
                new_edge_segment_list += out_list
        for pair in disconnect_list:
            self.Disconnect(pair[0], pair[1])
        for new_edge_segment in new_edge_segment_list:
            self.Add(new_edge_segment)

    def Add(self, other):
        if isinstance(other, LineSegment):
            i = self.FindVertex(other.point_a)
            j = self.FindVertex(other.point_b)
            if i is not None and j is not None:
                self.Connect(i, j)
            elif i is not None:
                self.vertex_list.append(GraphVertex(other.point_b))
                self.Connect(i, len(self.vertex_list) - 1)
            elif j is not None:
                self.vertex_list.append(GraphVertex(other.point_a))
                self.Connect(j, len(self.vertex_list) - 1)
            else:
                self.vertex_list.append(GraphVertex(other.point_a))
                self.vertex_list.append(GraphVertex(other.point_b))
                self.Connect(len(self.vertex_list) - 2, len(self.vertex_list) - 1)

    def Render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_LINES
        glBegin(GL_LINES)
        try:
            for edge_segment in self.GenerateEdgeSegments():
                glVertex2f(edge_segment.point_a.x, edge_segment.point_a.y)
                glVertex2f(edge_segment.point_b.x, edge_segment.point_b.y)
        finally:
            glEnd()