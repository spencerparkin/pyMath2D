# math2d_point_cloud.py

import math

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
    
    def GenerateConvexHull(self):
        from math2d_polygon import Polygon
        pass
        # TODO: Write this.
    
    def GenerateSymmetries(self):

        # TODO: Some shapes have rotational symmetry, but not reflective symmetry.
        #       How do we find the rotational symmetry in that case?

        reflection_list = []
        for i in range(len(self.point_list)):
            for j in range(i + 1, len(self.point_list)):
                line_segment = LineSegment(self.point_list[i], self.point_list[j])
                mid_point = line_segment.Lerp(0.5)
                normal = line_segment.Direction().Normalized().RotatedCCW90()
                reflection = AffineTransform()
                reflection.Reflection(mid_point, normal)
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
        ccw_rotation = None
        cw_rotation = None
        if len(reflection_list) >= 2:
            def SortKey(entry):
                angle = entry['normal'].SignedAngleBetween(Vector(1.0, 0.0))
                if angle < 0.0:
                    angle += 2.0 * math.pi
                return angle
            reflection_list.sort(key=SortKey)
            # Any 2 consecutive axes should be as close in angle between each other as possible.
            reflection_a = reflection_list[0]['reflection']
            reflection_b = reflection_list[1]['reflection']
            ccw_rotation = reflection_b * reflection_a
            cw_rotation = reflection_a * reflection_b
            # The following are just sanity checks.
            is_symmetry, total_error = self.IsSymmetry(ccw_rotation)
            if not is_symmetry:
                raise Exception('Failed to generate CCW rotational symmetry.')
            is_symmetry, total_error = self.IsSymmetry(cw_rotation)
            if not is_symmetry:
                raise Exception('Failed to generate CW rotational symmetry.')
        
        return reflection_list, ccw_rotation, cw_rotation
    
    def IsSymmetry(self, symmetry_transform, epsilon=1e-7):
        point_cloud = PointCloud()
        for point in self.point_list:
            point = symmetry_transform(point)
            point_cloud.Add(point)
        return self.IsPointCloud(point_cloud, epsilon)