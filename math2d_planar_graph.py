# math2d_planar_graph.py

import copy
import math

from math2d_line_segment import LineSegment
from math2d_vector import Vector

class PlanarGraphEdgeLabel:
    NONE = 0
    REGION_BORDER = 1
    CUT = 2

class PlanarGraph(object):
    # These are graphs in the plane where no two edges non-trivially overlap.
    # Edges are ordered pairs, but stored as triples, the third entry being a label.
    # Consequently, the edges are directional, and certain algorithms depend on this, others don't.
    # If the graph is not truly planar, then the result of any algorithm here is left undefined.
    # It should be noted here that we can't represent any planar graph with this class,
    # because we are restricting ourselves to edges that are line-segments.
    def __init__(self):
        self.vertex_list = [] # For large graphs, points in a BSP tree would have been more efficient.
        self.edge_list = [] # Probably should have used a set for faster look-up times.

    def Clear(self):
        self.vertex_list = []
        self.edge_list = []

    def Copy(self):
        return copy.deepcopy(self)

    def Serialize(self):
        json_data = {}
        json_data['edge_list'] = self.edge_list[:]
        json_data['vertex_list'] = [vertex.Serialize() for vertex in self.vertex_list]
        return json_data

    def Deserialize(self, json_data):
        self.edge_list = json_data['edge_list'][:]
        self.vertex_list = [Vector().Deserialize(vertex_data) for vertex_data in json_data['vertex_list']]
        return self
    
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

    def FindEdges(self, i):
        return [edge for edge in self.edge_list if edge[0] == i or edge[1] == i]

    def GenerateEdgeSegments(self):
        for edge in self.edge_list:
            yield self.EdgeSegment(edge)
    
    def Add(self, other, disposition={}, epsilon=1e-7, depth=0):
        from math2d_region import Region, SubRegion
        from math2d_polygon import Polygon
        from math2d_aa_rect import AxisAlignedRectangle

        if type(other) is list:
            for item in other:
                self.Add(item, disposition, epsilon, depth + 1)

        elif isinstance(other, PlanarGraph):
            for edge in other.edge_list:
                line_segment = other.EdgeSegment(edge)
                self.Add(line_segment, {**disposition, 'edge_label': edge[2]}, epsilon, depth + 1)
        
        elif isinstance(other, AxisAlignedRectangle):
            polygon = other.GeneratePolygon()
            self.Add(polygon, disposition, epsilon, depth + 1)
        
        elif isinstance(other, Region):
            for sub_region in other.sub_region_list:
                self.Add(sub_region, disposition, epsilon, depth + 1)
                
        elif isinstance(other, SubRegion):
            self.Add(other.polygon, disposition)
            for hole in other.hole_list:
                self.Add(hole, {**disposition, 'flip_edge_direction': True}, epsilon, depth + 1)
                
        elif isinstance(other, Polygon):
            for line_segment in other.GenerateLineSegments():
                self.Add(line_segment, disposition, epsilon, depth + 1)
                
        elif isinstance(other, LineSegment):
            for vertex in self.vertex_list:
                if other.ContainsPoint(vertex, epsilon) and not other.IsEndPoint(vertex, epsilon):
                    self.Add(LineSegment(other.point_a, vertex), disposition, epsilon, depth + 1)
                    self.Add(LineSegment(vertex, other.point_b), disposition, epsilon, depth + 1)
                    return

            for i, edge in enumerate(self.edge_list):
                edge_segment = self.EdgeSegment(edge)
                if not (other.IsEndPoint(edge_segment.point_a, epsilon) or other.IsEndPoint(edge_segment.point_b, epsilon)):
                    point = edge_segment.IntersectWith(other)
                    if point is not None:
                        if not edge_segment.IsEndPoint(point):
                            del self.edge_list[i]
                            self.Add(LineSegment(edge_segment.point_a, point), {'edge_label': edge[2]}, epsilon, depth + 1)
                            self.Add(LineSegment(point, edge_segment.point_b), {'edge_label': edge[2]}, epsilon, depth + 1)
                        if not other.IsEndPoint(point):
                            self.Add(LineSegment(other.point_a, point), disposition, epsilon, depth + 1)
                            self.Add(LineSegment(point, other.point_b), disposition, epsilon, depth + 1)
                            return

            i = self.FindVertex(other.point_a, add_if_not_found=True, epsilon=epsilon)
            j = self.FindVertex(other.point_b, add_if_not_found=True, epsilon=epsilon)
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
    
    def RemoveVertex(self, i):
        if isinstance(i, Vector):
            i = self.FindVertex(i)
        del self.vertex_list[i]
        self.edge_list = [edge for edge in self.edge_list if edge[0] != i and edge[1] != i]
        for j, edge in enumerate(self.edge_list):
            self.edge_list[j] = (
                edge[0] - 1 if edge[0] > i else edge[0],
                edge[1] - 1 if edge[1] > i else edge[1],
                edge[2]
            )
                    
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
            cycle_list, cycle_found = self.FindCycleContainingEdge(edge, True)
            polygon.vertex_list = [self.vertex_list[edge[0]] for edge in cycle_list]
            if polygon.IsWoundCCW():
                polygon.Tessellate()
                perimeter_list.append(polygon)
            else:
                cycle_list, cycle_found = self.FindCycleContainingEdge(edge, False)
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
        # This algorithm depends on the direction of the edges in the graph.
        cycle_list = [given_edge]
        cycle_found = True
        while True:
            edge = cycle_list[len(cycle_list) - 1]
            adjacency_list = self.FindAllAdjacencies(edge[1])
            cur_heading = self.EdgeVector(edge)
            j = -1
            if wind_ccw:
                largest_angle = -3.0 * math.pi
                for i in range(len(adjacency_list)):
                    adj_edge = adjacency_list[i]
                    if adj_edge[1] != edge[0]:
                        new_heading = self.EdgeVector(adj_edge)
                        angle = cur_heading.SignedAngleBetween(new_heading)
                        if angle > largest_angle:
                            j = i
                            largest_angle = angle
            else:
                smallest_angle = 3.0 * math.pi
                for i in range(len(adjacency_list)):
                    adj_edge = adjacency_list[i]
                    if adj_edge[1] != edge[0]:
                        new_heading = self.EdgeVector(adj_edge)
                        angle = cur_heading.SignedAngleBetween(new_heading)
                        if angle < smallest_angle:
                            j = i
                            smallest_angle = angle
            if j == -1:
                cycle_found = False
                break
            new_edge = adjacency_list[j]
            if new_edge == given_edge:
                break
            cycle_list.append(new_edge)
        return cycle_list, cycle_found
    
    def EdgeVector(self, edge):
        return self.vertex_list[edge[1]] - self.vertex_list[edge[0]]
    
    def EdgeSegment(self, edge):
        return LineSegment(self.vertex_list[edge[0]], self.vertex_list[edge[1]])
    
    def FindAllAdjacencies(self, i, ignore_direction=False, vertices=False):
        adjacency_list = []
        for edge in self.edge_list:
            if edge[0] == i:
                if vertices:
                    adjacency_list.append(edge[1])
                else:
                    adjacency_list.append(edge)
            elif ignore_direction and edge[1] == i:
                if vertices:
                    adjacency_list.append(edge[0])
                else:
                    adjacency_list.append(edge)
        return adjacency_list

    def GeneratePolygonCycles(self, epsilon=1e-7):
        # Find and return, as a list of polygons, the cycles of the
        # graph that do not encompass any other part of the graph.
        # Here we ignore the direction of the edges of the graph.
        # If there is more than one connected component of the graph,
        # then this may not produce a desirable result.
        graph = self.Copy()
        for edge in self.edge_list:
            reverse_edge = (edge[1], edge[0], edge[2])
            i = graph.FindEdge(reverse_edge, ignore_direction=False)
            if i is None:
                graph.edge_list.append(reverse_edge)
        from math2d_polygon import Polygon
        polygon_list = []
        while len(graph.edge_list) > 0:
            edge = graph.edge_list[0]
            cycle_list, cycle_found = graph.FindCycleContainingEdge(edge, wind_ccw=True)
            if cycle_found:
                polygon = Polygon()
                polygon.vertex_list = [graph.vertex_list[edge[0]] for edge in cycle_list]
                if polygon.IsWoundCCW(epsilon):
                    polygon_list.append(polygon)
            for edge in cycle_list:
                i = graph.FindEdge(edge, False, False)
                del graph.edge_list[i]
        return polygon_list

    def GenerateConnectedComponents(self):
        from math2d_dsf import DisjointSet
        sub_graph_list = []
        dsf_set_list = [DisjointSet(i) for i in range(len(self.vertex_list))]
        visited_vertex_set = set()
        added_edges_set = set()
        while len(visited_vertex_set) < len(self.vertex_list):
            for i in range(len(self.vertex_list)):
                if i not in visited_vertex_set:
                    break
            else:
                break
            queue = {i}
            sub_graph = PlanarGraph()
            while len(queue) > 0:
                i = queue.pop()
                visited_vertex_set.add(i)
                adj_edge_list = self.FindAllAdjacencies(i, ignore_direction=True)
                for edge in adj_edge_list:
                    dsf_set_list[edge[0]].MergeWith(dsf_set_list[edge[1]])
                    for j in [edge[0], edge[1]]:
                        if j not in visited_vertex_set and j not in queue:
                            queue.add(j)
                    if edge not in added_edges_set:
                        sub_graph.Add(self.EdgeSegment(edge))
                        added_edges_set.add(edge)
            sub_graph_list.append(sub_graph)
        return sub_graph_list, dsf_set_list

    def Render(self, arrow_head_length=0.3):
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
            vector.Render(point, arrow_head_length=arrow_head_length)
        glPointSize(2.0)
        glBegin(GL_POINTS)
        try:
            for point in self.vertex_list:
                glColor3f(0.0, 0.0, 0.0)
                glVertex2f(point.x, point.y)
        finally:
            glEnd()
    
    def GenerateLineMesh(self, thickness=0.5, epsilon=1e-7):
        half_thickness = thickness / 2.0
        from math2d_tri_mesh import TriangleMesh, Triangle
        from math2d_polygon import Polygon
        from math2d_affine_transform import AffineTransform
        mesh = TriangleMesh()
        def SortKey(vector):
            angle = Vector(1.0, 0.0).SignedAngleBetween(vector)
            if angle < 0.0:
                angle += 2.0 * math.pi
            return angle
        polygon_list = []
        for i in range(len(self.vertex_list)):
            center = self.vertex_list[i]
            vector_list = []
            adj_list = self.FindAllAdjacencies(i, ignore_direction=True, vertices=True)
            for j in adj_list:
                vector_list.append(self.vertex_list[j] - center)
            vector_list.sort(key=SortKey)
            polygon = Polygon()
            for j in range(len(vector_list)):
                vector_a = vector_list[j]
                vector_b = vector_list[(j + 1) % len(vector_list)]
                angle = vector_a.SignedAngleBetween(vector_b)
                if angle < 0.0:
                    angle += 2.0 * math.pi
                if math.fabs(angle - math.pi) < epsilon or angle < math.pi:
                    affine_transform = AffineTransform()
                    affine_transform.translation = center
                    affine_transform.linear_transform.x_axis = vector_a.Normalized()
                    affine_transform.linear_transform.y_axis = affine_transform.linear_transform.x_axis.RotatedCCW90()
                    if math.fabs(angle - math.pi) < epsilon:
                        length = 0.0
                    else:
                        length = half_thickness / math.tan(angle / 2.0)
                    point = affine_transform * Vector(length, half_thickness)
                    polygon.vertex_list.append(point)
                else:
                    # Here we might create a rounded joint or something fancy, but this is good for now.
                    polygon.vertex_list.append(vector_a.Normalized().RotatedCCW90().Scaled(half_thickness) + center)
                    polygon.vertex_list.append(vector_b.Normalized().RotatedCW90().Scaled(half_thickness) + center)
            polygon.Tessellate()
            mesh.AddMesh(polygon.mesh)
            polygon_list.append(polygon)
        for edge in self.edge_list:
            center_a = self.vertex_list[edge[0]]
            center_b = self.vertex_list[edge[1]]
            line_segment = LineSegment(center_a, center_b)
            def FindEdgeSegment(polygon):
                for edge_segment in polygon.GenerateLineSegments():
                    point = edge_segment.IntersectWith(line_segment)
                    if point is not None:
                        return edge_segment
                else:
                    raise Exception('Failed to find line quad end.')
            polygon_a = polygon_list[edge[0]]
            polygon_b = polygon_list[edge[1]]
            edge_segment_a = FindEdgeSegment(polygon_a)
            edge_segment_b = FindEdgeSegment(polygon_b)
            triangle_a = Triangle(edge_segment_a.point_a, edge_segment_b.point_b, edge_segment_b.point_a)
            triangle_b = Triangle(edge_segment_a.point_a, edge_segment_b.point_a, edge_segment_a.point_b)
            area_a = triangle_a.Area()
            area_b = triangle_b.Area()
            if area_a < 0.0 or area_b < 0.0:
                raise Exception('Miscalculated line quad triangles.')
            mesh.AddTriangle(triangle_a)
            mesh.AddTriangle(triangle_b)
        return mesh

    def Reduce(self, epsilon=1e-7):
        # Here we're removing all vertices of degree 2 where the incident
        # edges are approximately co-linear.
        keep_going = True
        while keep_going:
            keep_going = False
            for i in range(len(self.vertex_list)):
                adjacency_list = self.FindAllAdjacencies(i, ignore_direction=True, vertices=False)
                if len(adjacency_list) == 2:
                    edge_a = adjacency_list[0]
                    edge_b = adjacency_list[1]
                    point_a = self.vertex_list[edge_a[0]] if edge_a[0] != i else self.vertex_list[edge_a[1]]
                    point_b = self.vertex_list[edge_b[0]] if edge_b[0] != i else self.vertex_list[edge_b[1]]
                    line_seg = LineSegment(point_a=point_a, point_b=point_b)
                    distance = line_seg.Distance(self.vertex_list[i])
                    if distance < epsilon:
                        self.RemoveVertex(i)
                        self.Add(line_seg, disposition={}, epsilon=epsilon)
                        keep_going = True
                        break