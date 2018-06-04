# math2d_region.py

import copy

from math2d_polygon import Polygon

class Region(object):
    # These are simply collections of sub-regions.  The sub-regions are assumed
    # to be pair-wise disjoint from one another.  If this requirement is not
    # satisfied, then the result of any method is left undefined.
    def __init__(self):
        self.sub_region_list = []
    
    def Copy(self):
        return copy.deepcopy(self)

    def Tessellate(self):
        for sub_region in self.sub_region_list:
            sub_region.Tessellate()
            
    def ContainsPoint(self, point, epsilon=1e-7):
        for sub_region in self.sub_region_list:
            if sub_region.ContainsPoint(point, epsilon):
                return True
        return False
    
    def CutAgainst(self, other):
        from math2d_planar_graph import PlanarGraph, PlanarGraphEdgeLabel
        graph = PlanarGraph()
        graph.Add(self, False, PlanarGraphEdgeLabel.REGION_BORDER)
        graph.Add(other, False, PlanarGraphEdgeLabel.CUT)
        return graph.ReadCutRegions(self)

class SubRegion(object):
    # These are polygons with zero or more holes in them.
    # Each hole is described by a polygon contained within the main polygon of the sub-region.
    # Note that the perimeter and holes of the sub-region are both wound CCW in the plane.
    # If these requirements are not met, then the results of any method are left undefined.
    def __init__(self):
        self.polygon = None
        self.hole_list = []
    
    def Copy(self):
        return copy.deepcopy(self)

    def GenerateSelfTangentialPolygon(self):
        pass

    def Tessellate(self):
        # If you want a triangle mesh for the sub-region, then
        # tessellate a generated self-tangential polygon.
        self.polygon.Tessellate()
        for hole in self.hole_list:
            hole.Tessellate()
    
    def ContainsPoint(self, point, epsilon=1e-7):
        if not self.polygon.ContainsPoint(point, epsilon):
            return False
        for hole in self.hole_list:
            if hole.ContainsPoint(self, point, epsilon):
                return False
        return True