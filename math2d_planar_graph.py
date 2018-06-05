# math2d_planar_graph.py

import copy
import math

from math2d_line_segment import LineSegment

class PlanarGraphEdgeLabel:
    NONE = 0
    REGION_BORDER = 1,
    CUT = 2,

class PlanarGraph(object):
    # These are graphs in the plane where no two edges non-trivially overlap.
    # Edges are ordered pairs, but stored as triples, the third entry being a label.
    # Consequently, the edges are directional, and certain algorithms depend on this.
    # If the graph is not truly planar, then the result of any algorithm here is left undefined.
    def __init__(self):
        self.vertex_list = []
        self.edge_list = []
    
    def Copy(self):
        return copy.deepcopy(self)
    
    def FindVertex(self, point, epsilon=1e-7):
        for i, vertex in enumerate(self.vertex_list):
            if vertex.point.IsPoint(point, epsilon):
                return i
        return None
    
    def FindEdge(self, given_edge, ignore_direction=True, ignore_label=True):
        for i, edge in enumerate(self.edge_list):
            edges_match = False
            if edge[0] == given_edge[0] and edge[1] == given_edge[1]:
                edges_match = True
            if ignore_direction and edge[0] == given_edge[1] and edge[1] == given_edge[0]:
                edges_match = True
            if edges_match and (ignore_label or edge[2] == given_edge[2]):
                return i
        return None
    
    def Add(self, other, disposition=None):
        from math2d_region import Region, SubRegion
        from math2d_polygon import Polygon
        
        if isinstance(other, PlanarGraph):
            pass
        
        elif isinstance(other, Region):
            for sub_region in other.sub_region_list:
                self.Add(sub_region, disposition)
                
        elif isinstance(other, SubRegion):
            self.Add(other.polygon, disposition)
            for hole in other.hole_list:
                self.Add(hole, {**disposition, 'flip_edge_direction': True})
                
        elif isinstance(other, Polygon):
            for line_segment in other.GenerateLineSegments():
                self.Add(line_segment, disposition)
                
        elif isinstance(other, LineSegment):
            for vertex in self.vertex_list:
                if other.ContainsPoint(vertex) and not other.IsEndPoint(vertex):
                    self.Add(LineSegment(other.point_a, vertex), disposition)
                    self.Add(LineSegment(vertex, other.point_b), disposition)
                    return

            for i, edge in enumerate(self.edge_list):
                edge_segment = LineSegment(self.vertex_list[edge[0]], self.vertex_list[edge[1]])
                if not (other.IsEndPoint(edge_segment.point_a) or other.IsEndPoint(edge_segment.point_b)):
                    point = edge_segment.IntersectWith(other)
                    if point is not None:
                        del self.edge_list[i]
                        self.Add(LineSegment(edge_segment.point_a, point), {**disposition, 'edge_label': edge[2]})
                        self.Add(LineSegment(point, edge_segment.point_b), {**disposition, 'edge_label': edge[2]})
                        self.Add(LineSegment(other.point_a, point), disposition)
                        self.Add(LineSegment(point, other.point_b), disposition)
                        return

            i = self.FindVertex(other.point_a)
            if i is None:
                self.vertex_list.append(other.point_a)
                i = len(self.vertex_list)

            j = self.FindVertex(other.point_b)
            if j is None:
                self.vertex_list.append(other.point_b)
                j = len(self.vertex_list)
                
            if disposition['flip_edge_direction']:
                new_edge = (j, i, disposition['edge_label'])
            else:
                new_edge = (i, j, disposition['edge_label'])
            
            if new_edge[0] == new_edge[1]:
                raise Exception('Tried to add degenerate line-segment.')
            
            k = self.FindEdge(new_edge)
            if k is not None:
                if disposition['replace_edges']:
                    self.edge_list[k] = new_edge
                elif disposition['duplicate_edges']:
                    self.edge_list.append(new_edge)
            else:
                self.edge_list.append(new_edge)
    
    def ApplyCuts(self, region):
        # Turn all the cuts into bi-directional borders.
        while True:
            for i, edge in enumerate(self.edge_list):
                if edge[2] == PlanarGraphEdgeLabel.CUT:
                    break
            else:
                break
            del self.edge_list[i]
            edge_segment = LineSegment(self.vertex_list[edge[0]], self.vertex_list[edge[1]])
            if region.ContainsPoint(edge_segment.Lerp(0.5)):
                self.edge_list.append((edge[0], edge[1], PlanarGraphEdgeLabel.REGION_BORDER))
                self.edge_list.append((edge[1], edge[0], PlanarGraphEdgeLabel.REGION_BORDER))
                
        # Now go read-off all the perimeter and hole polygons.
        from math2d_polygon import Polygon
        perimeter_list = []
        hole_list = []
        while True:
            for edge in self.edge_list:
                if edge[2] == PlanarGraphEdgeLabel.REGION_BORDER:
                    break
            else:
                break
            polygon = Polygon()
            cycle_list = self.FindCycleContainingEdge(edge, True)
            polygon.vertex_list = [self.vertex_list[edge[0]] for edge in cycle_list]
            if polygon.IsWoundCCW():
                polygon.Tessellate()
                perimeter_list.append(polygon)
            else:
                cycle_list = self.FindCycleContainingEdge(edge, False)
                polygon.vertex_list = [self.vertex_list[edge[0]] for edge in cycle_list]
                if polygon.IsWoundCW():
                    polygon.ReverseWinding()
                    hole_list.append(polygon)
                else:
                    raise Exception('Failed to process cycle containing edge.')
            for edge in cycle_list:
                i = self.FindEdge(edge, False, False)
                del self.edge_list[i]
        
        # Finally, merry all the holes to the appropriate perimeters.
        from math2d_region import Region, SubRegion
        region = Region()
        for perimeter in perimeter_list:
            sub_region = SubRegion(perimeter)
            new_hole_list = []
            for hole in hole_list:
                # I believe we need only test a single point on the hole.
                if perimeter.ContainsPoint(hole.vertex_list[0]) and not perimeter.ContainsPointOnBorder(hole.vertex_list[0]):
                    sub_region.hole_list.append(hole)
                else:
                    new_hole_list.append(hole)
            hole_list = new_hole_list
            region.sub_region_list.append(sub_region)
        if len(hole_list) > 0:
            raise Exception('Failed to marry %d holes to perimeters.' % len(hole_list))
        
        return region

    def FindCycleContainingEdge(self, given_edge, wind_ccw=True):
        cycle_list = [given_edge]
        while cycle_list[len(cycle_list) - 1][1] != cycle_list[0][0]:
            edge = cycle_list[len(cycle_list) - 1]
            adjacency_list = self.FindAllAdjacencies(edge[1])
            cur_heading = self.EdgeVector(edge)
            j = -1
            if wind_ccw:
                largest_angle = 0.0
                for i in range(len(adjacency_list)):
                    adj_edge = adjacency_list[i]
                    new_heading = self.EdgeVector(adj_edge)
                    angle = cur_heading.SignedAngleBetween(new_heading)
                    if angle > largest_angle:
                        j = i
            else:
                smallest_angle = 3.0 * math.pi
                for i in range(len(adjacency_list)):
                    new_heading = self.EdgeVector(adj_edge)
                    angle = cur_heading.SignedAngleBetween(new_heading)
                    if angle < smallest_angle:
                        j = i
            cycle_list.append(self.adjacency_list[j])
        return cycle_list
    
    def EdgeVector(self, edge):
        return self.vertex_list[edge[1]] - self.vertex_list[edge[0]]
    
    def FindAllAdjacencies(self, i, ignore_direction=False):
        adjacency_list = []
        for edge in self.edge_list:
            if edge[0] == i:
                adjacency_list.append(edge)
            elif ignore_direction and edge[1] == i:
                adjacency_list.append(edge)
        return adjacency_list

    def Render(self, color_func=None):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, glPointSize, GL_LINES, GL_POINTS
        glBegin(GL_LINES)
        try:
            for edge in self.edge_list:
                point_a = self.vertex_list[edge[0]]
                point_b = self.vertex_list[edge[1]]
                if color_func is not None:
                    color_a, color_b = color_func(edge)
                else:
                    color_a = (1.0, 1.0, 1.0)
                    color_b = (1.0, 1.0, 1.0)
                glColor3f(color_a[0], color_a[1], color_a[2])
                glVertex2f(point_a.x, point_a.y)
                glColor3f(color_b[0], color_b[1], color_b[2])
                glVertex2f(point_b.x, point_b.y)
        finally:
            glEnd()
        glBegin(GL_POINTS)
        glPointSize(2.0)
        try:
            for point in self.vertex_list:
                glColor3f(0.0, 0.0, 0.0)
                glVertex2f(point.x, point.y)
        finally:
            glEnd()