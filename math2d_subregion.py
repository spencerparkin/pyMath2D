# math2d_subregion.py

from math2d_planar_graph import PlanarGraph
from math2d_vector import Vector
from math2d_line_segment import LineSegment

class SubRegion(PlanarGraph):
    # Like polygons, these are sub-regions of the plane.  But by virtue of being represented by
    # a planar graph, these areas, unlike polygons, may have arbitrary topologies.
    # That is, they may have holes in them.  The direction of the edges indicate
    # which side of an edge is interior and which exterior.  Of course, not all
    # planar graphs represent valid sub-regions.  For example, for every point in
    # the plane, we must be able to locate it, unambiguously, as being inside or
    # outside the region.  These regions are closed (i.e., border points are
    # interior to the region.)  Also, a valid sub-region graph will have not vertex
    # with a degree other than two.  Note that given a piece of area in the plane,
    # it's representation as a graph in the said manner is not necessarily unique.
    # Whenever a planar graph does not represent a valid sub-region, the results of any
    # method of this class are left undefined.
    def __init__(self):
        super().__init__()

    def Area(self):
        mesh = self.Tesselate()
        return mesh.Area()

    def ContainsPoint(self, point, epsilon=1e-7):
        # This shouldn't be called repeatedly on a static sub-region.
        mesh = self.Tessellate()
        return mesh.ContainsPoint(point, epsilon)

    def CutAgainstLineSegment(self, line_segment):
        # Here we cut this sub-region against the given line-segment.
        # This potentially alters the graph of the sub-region, but does not change
        # the area covered by the sub-region in the plane.
        pass
        # TODO: This will involve some ray-casting along the given line-segment.

    def GeneratePolygon(self):
        # Here we generate a polygon that covers the same area as this region.
        # To do so, the returned polygon may necessarily be self-tangential.
        component_list = self.GenerateConnectedComponents()
        polygon_list = [sub_graph.GeneratePolygon() for sub_graph in component_list]
        while len(polygon_list) > 0:
            pass # TODO: Find 2 polygons we can merge into one.
        return polygon_list[0]

    def Tessellate(self):
        polygon = self.GeneratePolygon()
        return polygon.Tessellate()
    
    def RemoveRedundantVertices(self):
        pass
    
    def Transform(self, transform):
        pass