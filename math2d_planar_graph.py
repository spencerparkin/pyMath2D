# math2d_planar_graph.py

import copy
import math

from math2d_line_segment import LineSegment

class PlanarGraphEdgeLabel:
    NONE = 0
    REGION_BORDER = 1
    CUT = 2

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
    
    def FindVertex(self, point, add_if_not_found=False, epsilon=1e-7):
        for i, vertex in enumerate(self.vertex_list):
            if vertex.IsPoint(point, epsilon):
                return i
        if add_if_not_found:
            self.vertex_list.append(point)
            return len(self.vertex_list) - 1
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
    
    def Add(self, other, disposition={}):
        from math2d_region import Region, SubRegion
        from math2d_polygon import Polygon
        from math2d_aa_rect import AxisAlignedRectangle
        
        if isinstance(other, PlanarGraph):
            for edge in other.edge_list:
                line_segment = other.EdgeSegment(edge)
                self.Add(line_segment, {**disposition, 'edge_label': edge[2]})
        
        elif isinstance(other, AxisAlignedRectangle):
            polygon = other.GeneratePolygon()
            self.Add(polygon, disposition)
        
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
                edge_segment = self.EdgeSegment(edge)
                if not (other.IsEndPoint(edge_segment.point_a) or other.IsEndPoint(edge_segment.point_b)):
                    point = edge_segment.IntersectWith(other)
                    if point is not None:
                        if not edge_segment.IsEndPoint(point):
                            del self.edge_list[i]
                            self.Add(LineSegment(edge_segment.point_a, point), {'edge_label': edge[2]})
                            self.Add(LineSegment(point, edge_segment.point_b), {'edge_label': edge[2]})
                        if not other.IsEndPoint(point):
                            self.Add(LineSegment(other.point_a, point), disposition)
                            self.Add(LineSegment(point, other.point_b), disposition)
                            return

            i = self.FindVertex(other.point_a, add_if_not_found=True)
            j = self.FindVertex(other.point_b, add_if_not_found=True)
            label = disposition.get('edge_label', PlanarGraphEdgeLabel.NONE)
            if disposition.get('flip_edge_direction', False):
                new_edge = (j, i, label)
            else:
                new_edge = (i, j, label)
            
            if new_edge[0] == new_edge[1]:
                raise Exception('Tried to add degenerate line-segment.')
            
            k = self.FindEdge(new_edge)
            if k is not None:
                if disposition.get('replace_edges', False):
                    self.edge_list[k] = new_edge
                elif disposition.get('duplicate_edges', False):
                    self.edge_list.append(new_edge)
            else:
                self.edge_list.append(new_edge)
    
    def ApplyCuts(self, region):
        # Turn all the cuts into bi-directional borders.  Discard cuts that don't cut anything.
        region.Tessellate()
        while True:
            for i, edge in enumerate(self.edge_list):
                if edge[2] == PlanarGraphEdgeLabel.CUT:
                    break
            else:
                break
            del self.edge_list[i]
            edge_segment = self.EdgeSegment(edge)
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
        # TODO: This is a bit tricky.  A hole may lie inside a perimeter, but that doesn't mean it belongs to that perimeter,
        #       because it may lie inside a yet smaller perimeter that is contained in a hole of the other perimeter.  Make sure
        #       we assign holes to containing perimeters of the smallest area.  I think this may fix the problem.
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

    def FindCycleContainingEdge(self, given_edge, wind_ccw=True, epsilon=1e-7):
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
                    if angle > largest_angle and math.fabs(math.fabs(angle) - math.pi) > epsilon:
                        j = i
            else:
                smallest_angle = 3.0 * math.pi
                for i in range(len(adjacency_list)):
                    adj_edge = adjacency_list[i]
                    new_heading = self.EdgeVector(adj_edge)
                    angle = cur_heading.SignedAngleBetween(new_heading)
                    if angle < smallest_angle and math.fabs(math.fabs(angle) - math.pi) > epsilon:
                        j = i
            cycle_list.append(adjacency_list[j])
        return cycle_list
    
    def EdgeVector(self, edge):
        return self.vertex_list[edge[1]] - self.vertex_list[edge[0]]
    
    def EdgeSegment(self, edge):
        return LineSegment(self.vertex_list[edge[0]], self.vertex_list[edge[1]])
    
    def FindAllAdjacencies(self, i, ignore_direction=False):
        adjacency_list = []
        for edge in self.edge_list:
            if edge[0] == i:
                adjacency_list.append(edge)
            elif ignore_direction and edge[1] == i:
                adjacency_list.append(edge)
        return adjacency_list

    def Render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, glColor3f, glPointSize, GL_POINTS
        for edge in self.edge_list:
            if edge[2] == PlanarGraphEdgeLabel.CUT:
                glColor3f(0.0, 1.0, 0.0)
            elif edge[2] == PlanarGraphEdgeLabel.REGION_BORDER:
                glColor3f(0.6, 0.6, 0.6)
            else:
                glColor3f(1.0, 0.0, 0.0)
            vector = self.EdgeVector(edge)
            point = self.vertex_list[edge[0]]
            vector.Render(point)
        '''glPointSize(2.0)
        glBegin(GL_POINTS)
        glColor3f(1.0, 1.0, 1.0)
        try:
            for point in self.vertex_list:
                glColor3f(0.0, 0.0, 0.0)
                glVertex2f(point.x, point.y)
        finally:
            glEnd()'''