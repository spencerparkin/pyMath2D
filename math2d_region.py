# math2d_region.py

import copy

from math2d_polygon import Polygon
from math2d_line_segment import LineSegment

class Region(object):
    # These are simply collections of sub-regions.  The sub-regions are assumed
    # to be pair-wise disjoint from one another.  If this requirement is not
    # satisfied, then the result of any method is left undefined.
    def __init__(self):
        self.sub_region_list = []
    
    def Copy(self):
        return copy.deepcopy(self)

    def Serialize(self):
        json_data = {
            'sub_region_list': [sub_region.Serialize() for sub_region in self.sub_region_list]
        }
        return json_data
    
    def Deserialize(self, json_data):
        self.sub_region_list = [SubRegion().Deserialize(sub_region) for sub_region in json_data['sub_region_list']]
        return self

    def Tessellate(self):
        for sub_region in self.sub_region_list:
            sub_region.Tessellate()
    
    def TessellatePolygons(self):
        polygon_list = [sub_region.TessellatePolygon() for sub_region in self.sub_region_list]
        return polygon_list
    
    def GenerateMesh(self):
        from math2d_tri_mesh import TriangleMesh
        polygon_list = self.TessellatePolygons()
        mesh = TriangleMesh()
        for polygon in polygon_list:
            for triangle in polygon.mesh.GenerateTriangles():
                mesh.AddTriangle(triangle)
        return mesh
    
    def GenerateLineMesh(self, thickness=0.5):
        from math2d_planar_graph import PlanarGraph
        graph = PlanarGraph()
        graph.Add(self)
        return graph.GenerateLineMesh(thickness)
    
    def ContainsPoint(self, point, epsilon=1e-7):
        for sub_region in self.sub_region_list:
            if sub_region.ContainsPoint(point, epsilon):
                return True
        return False

    def ContainsPointOnBorder(self, point, epsilon=1e-7):
        for sub_region in self.sub_region_list:
            if sub_region.ContainsPointOnBorder(point, epsilon):
                return True
        return False
        
    def CutAgainst(self, other):
        from math2d_planar_graph import PlanarGraph, PlanarGraphEdgeLabel
        graph = PlanarGraph()
        graph.Add(self, {'edge_label': PlanarGraphEdgeLabel.REGION_BORDER})
        graph.Add(other, {'edge_label': PlanarGraphEdgeLabel.CUT})
        return graph.ApplyCuts(self)
    
    def Render(self):
        for sub_region in self.sub_region_list:
            sub_region.Render()

class SubRegion(object):
    # These are polygons with zero or more holes in them.
    # Each hole is described by a polygon contained within the main polygon of the sub-region.
    # Note that the perimeter and holes of the sub-region are both wound CCW in the plane.
    # If these requirements are not met, then the results of any method are left undefined.
    def __init__(self, polygon=None):
        self.polygon = polygon if polygon is not None else Polygon()
        self.hole_list = []
    
    def Copy(self):
        return copy.deepcopy(self)

    def Serialize(self):
        json_data = {
            'border_polygon': self.polygon.Serialize(),
            'hole_list': [hole.Serialize() for hole in self.hole_list]
        }
        return json_data

    def Deserialize(self, json_data):
        self.polygon = Polygon().Deserialize(json_data['border_polygon'])
        self.hole_list = [Polygon().Deserialize(hole) for hole in json_data['hole_list']]
        return self

    def GeneratePolygon(self):
        # Return a polygon covering the same area as this sub-region.
        # If there are holes in this polygon, then the returned polygon
        # will necessarily be self-tangential.  Note that we're not necessarily
        # finding the best polygon according to some sort of metric.  We're
        # just finding the first one we can find that works.
        sub_region = self.Copy()
        while len(sub_region.hole_list) > 0:
            # Try to merge a hole with the perimeter to expand the perimeter.
            for i, hole in enumerate(sub_region.hole_list):
                polygon = sub_region._MergePolygons(sub_region.polygon, hole, True)
                if polygon is not None:
                    del sub_region.hole_list[i]
                    sub_region.polygon = polygon
                    break
        
            # Try to merge a hole with some other hole to make a new hole.
            found = False
            for i in range(len(sub_region.hole_list)):
                hole_a = sub_region.hole_list[i]
                for j in range(i + 1, len(sub_region.hole_list)):
                    hole_b = sub_region.hole_list[j]
                    polygon = sub_region._MergePolygons(hole_a, hole_b, False)
                    if polygon is not None:
                        del sub_region.hole_list[j] # Must delete j before i since j > i.
                        del sub_region.hole_list[i]
                        sub_region.hole_list.append(polygon)
                        found = True
                        break
                if found:
                    break
                    
        return sub_region.polygon

    def _MergePolygons(self, polygon_a, polygon_b, b_contains_a):
        for i, point_a in enumerate(polygon_a.vertex_list):
            for j, point_b in enumerate(polygon_b.vertex_list):
                line_segment = LineSegment(point_a, point_b)
                if self._TouchesOnlyEndpointsOfSegment(line_segment):
                    polygon = Polygon()
                    for k in range(len(polygon_a.vertex_list) + 1):
                        polygon.vertex_list.append(polygon_a.vertex_list[(i + k) % len(polygon_a.vertex_list)])
                    q = -1 if b_contains_a else 1
                    for k in range(len(polygon_b.vertex_list) + 1):
                        polygon.vertex_list.append(polygon_b.vertex_list[(j + q * k) % len(polygon_b.vertex_list)])
                    return polygon
    
    def _TouchesOnlyEndpointsOfSegment(self, line_segment):
        for edge in self.GenerateLineSegments():
            if line_segment.IntersectWith(edge) is not None:
                if not line_segment.IsEndPoint(edge.point_a) and not line_segment.IsEndPoint(edge.point_b):
                    return False
        for vertex in self.GenerateVertices():
            if line_segment.ContainsPoint(vertex):
                if not line_segment.IsEndPoint(vertex) and not line_segment.IsEndPoint(vertex):
                    return False
        return True

    def GenerateLineSegments(self):
        yield from self.polygon.GenerateLineSegments()
        for hole in self.hole_list:
            yield from hole.GenerateLineSegments()

    def GenerateVertices(self):
        for vertex in self.polygon.vertex_list:
            yield vertex
        for hole in self.hole_list:
            for vertex in hole.vertex_list:
                yield vertex

    def TessellatePolygon(self):
        polygon = self.GeneratePolygon()
        polygon.Tessellate()
        return polygon

    def Tessellate(self):
        self.polygon.Tessellate()
        for hole in self.hole_list:
            hole.Tessellate()
    
    def ContainsPoint(self, point, epsilon=1e-7):
        if not self.polygon.ContainsPoint(point, epsilon):
            return False
        for hole in self.hole_list:
            if hole.ContainsPoint(point, epsilon):
                return False
        return True
    
    def ContainsPointOnBorder(self, point, epsilon=1e-7):
        if self.polygon.ContainsPointOnBorder(point, epsilon):
            return True
        for hole in self.hole_list:
            if hole.ContainsPointOnBorder(point, epsilon):
                return True
        return False
    
    def Render(self):
        self.polygon.Render()
        for hole in self.hole_list:
            hole.Render()