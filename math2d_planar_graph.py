# math2d_planar_graph.py

import copy

class PlanarGraph(object):
    # These are graphs in the plane where no two edges non-trivially overlap.
    # The edges are directed by being ordered pairs of indices into the vertex list.
    # Each vertex is simply a point in the plane.
    def __init__(self):
        self.vertex_list = []
        self.edge_list = []
    
    def Copy(self):
        return copy.deepcopy(self)
    
    def FindOrAddVertex(self, given_vertex):
        for i, vertex in enumerate(self.vertex_list):
            if vertex.IsPoint(given_vertex):
                return i
        else:
            self.vertex_list.append(given_vertex)
            return len(self.vertex_list) - 1
    
    def FindOrAddEdge(self, given_edge):
        for i, edge in enumerate(self.edge_list):
            if edge == given_edge:
                return i
        else:
            self.edge_list.append(given_edge)
            return len(self.edge_list) - 1
    
    def GenerateConnectedComponents(self):
        component_list = []
        visit_set = set()
        while len(visit_set) < len(self.vertex_list):
            sub_graph = PlanarGraph()
            for i in range(len(self.vertex_list)):
                if i not in visit_set:
                    break
            iterator = PlanarGraphIterator(self, i)
            while True:
                try:
                    i = next(iterator)
                    visit_set.add(i)
                    a = sub_graph.FindOrAddVertex(self.vertex_list[i])
                    for edge in self.GenerateAdjacentEdges(i):
                        j = self.FollowEdge(edge, i)
                        b = sub_graph.FindOrAddVertex(self.vertex_list[j])
                        sub_graph.FindOrAddEdge((a, b) if edge[0] == i else (b, a))
                except StopIteration:
                    break
            component_list.append(sub_graph)
        return component_list

    def __iter__(self):
        return PlanarGraphIterator(self, 0)

    def GenerateAdjacentEdges(self, i):
        for edge in self.edge_list:
            if edge[0] == i or edge[1] == i:
                yield edge

    def FindAdjacencies(self, i):
        adjacency_list = []
        for edge in self.GenerateAdjacentEdges(i):
            adjacency_list.append(self.FollowEdge(edge, i))
        return adjacency_list

    def FollowEdge(self, edge, i):
        # Here we follow the given edge, regardless of its direction.
        if edge[0] == i:
            return edge[1]
        elif edge[1] == i:
            return edge[0]
        return None

    def GeneratePolygon(self, origin=0):
        # If the planar graph doesn't represent a polygon, our result here is undefined.
        from math2d_polygon import Polygon
        polygon = Polygon()
        i = origin
        while True:
            polygon.vertex_list.append(self.vertex_list[i])
            for edge in self.GenerateAdjacentEdges(i):
                if edge[0] == i:
                    i = edge[1]
                    break
            if i == 0:
                break
        mesh = polygon.Tessellate()
        if mesh is None:
            polygon.ReverseWinding()
        return polygon

class PlanarGraphIteration:
    BREADTH_FIRST_SEARCH = 0
    DEPTH_FIRST_SEARCH = 1

class PlanarGraphIterator(object):
    def __init__(self, planar_graph, origin, iteration=PlanarGraphIteration.BREADTH_FIRST_SEARCH):
        self.planar_graph = planar_graph
        self.iteration = iteration
        self.visit_set = set()
        self.queue = [origin]
    
    def __next__(self):
        if len(self.queue) == 0:
            raise StopIteration()
        i = self.queue.pop()
        self.visit_set.add(i)
        adjacency_list = self.planar_graph.FindAdjacencies(i)
        for j in adjacency_list:
            if j not in self.visit_set:
                if self.iteration == PlanarGraphIteration.BREADTH_FIRST_SEARCH:
                    self.queue.append(j)
                elif self.iteration == PlanarGraphIteration.DEPTH_FIRST_SEARCH:
                    self.queue.insert(0, j)
        return i