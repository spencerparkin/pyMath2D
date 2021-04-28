# math2d_point_cloud.py

import math
import random

from math2d_vector import Vector
from math2d_line_segment import LineSegment
from math2d_affine_transform import AffineTransform

class PointCloud(object):
    def __init__(self):
        self.point_list = []
    
    def Size(self):
        return len(self.point_list)
    
    def __eq__(self, other):
        return self.IsPointCloud(other)[0]
    
    def IsPointCloud(self, point_cloud, epsilon=1e-7):
        if not isinstance(point_cloud, PointCloud):
            return False, None
        if self.Size() != point_cloud.Size():
            return False, None
        total_error = 0.0
        for point in self.point_list:
            i = point_cloud.FindPoint(point, epsilon)
            if i is None:
                return False, None
            total_error += (point - point_cloud.point_list[i]).Length()
        return True, total_error
    
    def Add(self, other, epsilon=1e-7):
        from math2d_polygon import Polygon
        from math2d_region import Region, SubRegion
        from math2d_planar_graph import PlanarGraph
        if isinstance(other, Polygon):
            for vertex in other.vertex_list:
                self.Add(vertex)
        elif isinstance(other, SubRegion):
            self.Add(other.polygon)
            for hole in other.hole_list:
                self.Add(hole)
        elif isinstance(other, Region):
            for sub_region in other.sub_region_list:
                self.Add(sub_region)
        elif isinstance(other, Vector):
            i = self.FindPoint(other, epsilon)
            if i is None:
                self.point_list.append(other)
        elif isinstance(other, PlanarGraph):
            for vertex in other.vertex_list:
                self.Add(vertex)
    
    def FindPoint(self, given_point, epsilon=1e-7):
        # For large point-clouds, a linear search here may be impractical, and something like a BSP tree would be helpful.
        for i, point in enumerate(self.point_list):
            if given_point.IsPoint(point, epsilon):
                return i
        return None
    
    def FindNearestPoints(self, given_point, epsilon=1e-7):
        nearest_points = []
        smallest_distance = 999999.0
        for i, point in enumerate(self.point_list):
            distance = (point - given_point).Length()
            if math.fabs(distance - smallest_distance) < epsilon:
                nearest_points.append(i)
            elif distance < smallest_distance:
                nearest_points = []
                smallest_distance = distance
        return nearest_points, smallest_distance
    
    def GenerateConvexHull(self):
        from math2d_line import Line
        from math2d_polygon import Polygon
        from math2d_triangle import Triangle
        found = False
        for i in range(len(self.point_list)):
            for j in range(len(self.point_list)):
                if j == i:
                    continue
                for k in range(len(self.point_list)):
                    if k == i or k == j:
                        continue
                    triangle = Triangle(self.point_list[i], self.point_list[j], self.point_list[k])
                    if triangle.Area() > 0.0:
                        found = True
                        break
                if found:
                    break
            if found:
                break
        if not found:
            raise Exception('Failed to find initial triangle.')
        polygon = Polygon()
        polygon.vertex_list = [triangle.vertex_a, triangle.vertex_b, triangle.vertex_c]
        point_list = [point for point in self.point_list]
        random.seed(0)
        while True:
            new_point_list = []
            for point in point_list:
                if not polygon.ContainsPoint(point, assume_convex=True):
                    new_point_list.append(point)
            point_list = new_point_list
            if len(point_list) == 0:
                break
            # Perhaps randomly choosing a point will help us terminate quicker on average?
            point = random.choice(point_list)
            point_cloud = PointCloud()
            point_cloud.Add(polygon)
            j = None
            k = None
            for i in range(len(polygon.vertex_list)):
                vertex = polygon.vertex_list[i]
                line = Line()
                line.MakeForPoints(point, vertex)
                point_cloud_back, point_cloud_front, point_cloud_neither = point_cloud.Split(line)
                if point_cloud_front.Size() == 0:
                    j = i
                if point_cloud_back.Size() == 0:
                    k = i
                if j is not None and k is not None and j != k:
                    break
            else:
                raise Exception('Failed to determine how to add point to convex hull.')
            new_vertex_list = [point]
            i = k
            while True:
                new_vertex_list.append(polygon.vertex_list[i])
                if i == j:
                    break
                i = (i + 1) % len(polygon.vertex_list)
            polygon.vertex_list = new_vertex_list
        return polygon

    def Split(self, line, epsilon=1e-7):
        from math2d_line import Line
        point_cloud_back = PointCloud()
        point_cloud_front = PointCloud()
        point_cloud_neither = PointCloud()
        for point in self.point_list:
            side = line.CalcSide(point, epsilon=epsilon)
            if side == Line.SIDE_BACK:
                point_cloud_back.Add(point)
            elif side == Line.SIDE_FRONT:
                point_cloud_front.Add(point)
            elif side == Line.SIDE_NEITHER:
                point_cloud_neither.Add(point)
        return point_cloud_back, point_cloud_front, point_cloud_neither

    def GenerateSymmetries(self):
        reflection_list = []
        center_reflection_list = []
        center = self.AveragePoint()
        for i in range(len(self.point_list)):
            for j in range(i + 1, len(self.point_list)):
                line_segment = LineSegment(self.point_list[i], self.point_list[j])
                mid_point = line_segment.Lerp(0.5)
                normal = line_segment.Direction().Normalized().RotatedCCW90()
                reflection = AffineTransform()
                reflection.Reflection(mid_point, normal)
                center_reflected = reflection.Transform(center)
                if center_reflected.IsPoint(center):
                    center_reflection_list.append({'reflection': reflection, 'normal': normal})
                is_symmetry, total_error = self.IsSymmetry(reflection)
                if is_symmetry:
                    new_entry = {'reflection': reflection, 'total_error': total_error, 'center': mid_point, 'normal': normal}
                    for k, entry in enumerate(reflection_list):
                        if entry['reflection'].IsTransform(reflection):
                            if entry['total_error'] > total_error:
                                reflection_list[k] = new_entry
                            break
                    else:
                        reflection_list.append(new_entry)
        
        # Rotations are just double-reflections.  We return here a CCW rotational symmetry that generates
        # the sub-group of rotational symmetries of the overall group of symmetries of the cloud.  We also
        # return its inverse for convenience.  Of course, not all point clouds have any rotational symmetry.
        epsilon = 1e-7
        def SortKey(entry):
            if entry['normal'].y <= -epsilon:
                entry['normal'] = -entry['normal']
            angle = Vector(1.0, 0.0).SignedAngleBetween(entry['normal'])
            if angle < 0.0:
                angle += 2.0 * math.pi
            return angle
        ccw_rotation = None
        cw_rotation = None
        if len(reflection_list) >= 2:
            reflection_list.sort(key=SortKey)
            # Any 2 consecutive axes should be as close in angle between each other as possible.
            reflection_a = reflection_list[0]['reflection']
            reflection_b = reflection_list[1]['reflection']
            ccw_rotation = reflection_a * reflection_b
            cw_rotation = reflection_b * reflection_a
            # The following are just sanity checks.
            is_symmetry, total_error = self.IsSymmetry(ccw_rotation)
            if not is_symmetry:
                raise Exception('Failed to generate CCW rotational symmetry.')
            is_symmetry, total_error = self.IsSymmetry(cw_rotation)
            if not is_symmetry:
                raise Exception('Failed to generate CW rotational symmetry.')
        elif len(reflection_list) == 1:
            # If we found exactly one reflection, then I believe the cloud has no rotational symmetry.
            # Note that the identity transform is not considered a symmetry.
            pass
        else:
            # If we found no reflective symmetry, the cloud may still have rotational symmetry.
            # Furthermore, if it does, it must rotate about the average point.  I think there is a way
            # to prove this using strong induction.  Note that the statement holds for all point-clouds
            # made from vertices taken from regular polygons.  Now for any given point-cloud with any
            # given rotational symmetry, consider 1 point of that cloud.  Removing that point along
            # with the minimum number of other points necessary to keep the given rotational symmetry,
            # we must remove points making up a regular polygon's vertices.  By inductive hypothesis,
            # the remaining cloud has its average point at the center of the rotational symmetry.  Now
            # see that adding the removed points back does not change the average point of the cloud.
            # Is it true that every line of symmetry of the cloud contains the average point?  I believe
            # the answer is yes.  Take any point-cloud with a reflective symmetry and consider all but
            # 2 of its points that reflect into one another along that symmetry.  If the cloud were just
            # these 2 points, then the average point is on the line of symmetry.  Now notice that as you
            # add back points by pairs, each pair reflecting into one another, the average point of the
            # cloud remains on the line of symmetry.
            center_reflection_list.sort(key=SortKey)
            found = False
            for i in range(len(center_reflection_list)):
                for j in range(i + 1, len(center_reflection_list)):
                    ccw_rotation = center_reflection_list[i]['reflection'] * center_reflection_list[j]['reflection']
                    is_symmetry, total_error = self.IsSymmetry(ccw_rotation)
                    if is_symmetry:
                        # By stopping at the first one we find, we should be minimizing the angle of rotation.
                        found = True
                        break
                if found:
                    break
            if found:
                cw_rotation = ccw_rotation.Inverted()
            else:
                ccw_rotation = None
        
        return reflection_list, ccw_rotation, cw_rotation
    
    def AveragePoint(self):
        if len(self.point_list) == 0:
            return None
        avg_point = Vector(0.0, 0.0)
        for point in self.point_list:
            avg_point += point
        avg_point *= 1.0 / float(len(self.point_list))
        return avg_point
    
    def IsSymmetry(self, symmetry_transform, epsilon=1e-7):
        if(symmetry_transform.IsIdentity()):
            return False, None
        point_cloud = PointCloud()
        for point in self.point_list:
            point = symmetry_transform(point)
            point_cloud.Add(point)
        return self.IsPointCloud(point_cloud, epsilon)

    def Render(self):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_POINTS, glPointSize
        glBegin(GL_POINTS)
        #glPointSize(3.0)
        try:
            for i in range(len(self.point_list)):
                point = self.point_list[i]
                glVertex2f(point.x, point.y)
        finally:
            glEnd()