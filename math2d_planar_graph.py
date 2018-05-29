# math2d_planar_graph.py

from math2d_vector import Vector
from math2d_line_segment import LineSegment

class PlanarGraph(object):
    # These are graphs in the plane where no two edges overlap.
    # The edges are directed by being ordered pairs of indices into the vertex list.
    # Each vertex is simply a point in the plane.
    def __init__(self):
        self.vertex_list = []
        self.edge_list = []

class SubRegion(PlanarGraph):
    # These are sub-regions of the plane.  By virtue of being represented by
    # a planar graph, these may have arbitrary topologies.  The direction of
    # the edges indicate which side of an edge is interior and which exterior.
    # Not all planar graphs represent valid sub-regions.  For example, for
    # every point in the plane, we must be able to locate it as being inside
    # or outside the region.  These regions are closed (i.e., border points
    # are interior to the region.)
    def __init__(self):
        super().__init__()
    
    def Copy(self):
        subregion = SubRegion()
        subregion.vertex_list = [vertex.Copy for vertex in self.vertex_list]
        subregion.edge_list = [edge for edge in self.edge_list]
        return subregion
    
    def Cut(self, cutter):
        # The given cutter must be an iterable that produces line segments.
        # 1) Make a copy of self.
        # 2) In the copy, add additional edges by applying the given cutter.
        # 3) Construct all new regions from the cuts made.  A new region has
        #    to inherit any holes that were in it.
        subregion = self.Copy()
        for cut_segment in cutter:
            pass
        while len(subregion.edge_list) > 0:
            pass # Always read off a new sub-region by starting at a cut made in the sub-region.
    
    def Tessolate(self):
        subregion = self.Copy()
        while True:
            # TODO: Find a triangle in the interior.  If we can't find one, we're done.
            #       If we do find one, then add it to our mesh, then shrink the sub-region.
            pass

class SubRegionSegmentIterable(object):
    def __init__(self, subregion):
        self.subregion = subregion
        self.i = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.i >= len(self.subregion.edge_list):
            raise StopIteration()
        edge = self.subregion.edge_list[self.i]
        line_segment = LineSegment(self.subregion.vertex_list[edge[0]], self.subregion.vertex_list[edge[1]])
        self.i += 1
        return line_segment
    
class SubRegionVertexIterable(object):
    def __init__(self, subregion):
        self.subregion = subregion
        self.i = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.i >= len(self.subregion.vertex_list):
            raise StopIteration()
        vertex = self.subregion.vertex_list[self.i]
        self.i += 1
        return vertex