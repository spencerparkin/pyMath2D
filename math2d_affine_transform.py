# math2d_affine_transform.py

from math2d_vector import Vector
from math2d_line_segment import LineSegment
from math2d_linear_transform import LinearTransform

class AffineTransform(object):
    def __init__(self, x_axis=None, y_axis=None, translation=None):
        self.linear_transform = LinearTransform(x_axis, y_axis)
        self.translation = translation if translation is not None else Vector(0.0, 0.0)
    
    def Copy(self):
        return AffineTransform(self.linear_transform.x_axis.Copy(), self.linear_transform.y_axis.Copy(), self.translation.Copy())
    
    def Serialize(self):
        json_data = {
            'linear_transform': self.linear_transform.Serialize(),
            'translation': self.translation.Serialize()
        }
        return json_data

    def Deserialize(self, json_data):
        self.linear_transform = LinearTransform().Deserialize(json_data['linear_transform'])
        self.translation = Vector().Deserialize(json_data['translation'])
        return self
    
    def IsTransform(self, transform, epsilon=1e-7):
        if not self.linear_transform.IsTransform(transform.linear_transform, epsilon):
            return False
        if not self.translation.IsPoint(transform.translation, epsilon):
            return False
        return True
    
    def Identity(self):
        self.linear_transform.Identity()
        self.translation = Vector(0.0, 0.0)
    
    def IsIdentity(self, epsilon=1e-7):
        if not self.linear_transform.IsIdentity(epsilon):
            return False
        return True if self.translation.IsZero(epsilon) else False
    
    def Transform(self, object):
        from math2d_polygon import Polygon
        from math2d_region import Region, SubRegion
        if isinstance(object, Vector):
            return self.linear_transform.Transform(object) + self.translation
        elif isinstance(object, AffineTransform):
            transform = AffineTransform()
            transform.linear_transform.x_axis = self.linear_transform.Transform(object.linear_transform.x_axis)
            transform.linear_transform.y_axis = self.linear_transform.Transform(object.linear_transform.y_axis)
            transform.translation = self.Transform(object.translation)
            return transform
        elif isinstance(object, LineSegment):
            return LineSegment(self.Transform(object.point_a), self.Transform(object.point_b))
        elif isinstance(object, Polygon):
            polygon = Polygon()
            for vertex in object.vertex_list:
                polygon.vertex_list.append(self.Transform(vertex))
            return polygon
        elif isinstance(object, Region):
            region = Region()
            for sub_region in object.sub_region_list:
                region.sub_region_list.append(self.Transform(sub_region))
            return region
        elif isinstance(object, SubRegion):
            sub_region = SubRegion()
            sub_region.polygon = self.Transform(object.polygon)
            for hole in object.hole_list:
                sub_region.hole_list.append(self.Transform(hole))
            return sub_region
    
    def __call__(self, object):
        return self.Transform(object)
    
    def __mul__(self, other):
        return self.Transform(other)
    
    def Determinant(self):
        return self.linear_transform.Determinant()
    
    def Invert(self):
        self.linear_transform.Invert()
        self.translation = -self.linear_transform.Transform(self.translation)
    
    def Inverted(self):
        inverse = self.Copy()
        inverse.Invert()
        return inverse
    
    def Rotation(self, center, angle):
        translation_a = AffineTransform(None, None, -center)
        translation_b = AffineTransform(None, None, center)
        rotation = AffineTransform()
        rotation.linear_transform.Rotation(angle)
        transform = translation_b * rotation * translation_a
        self.linear_tranfsorm = transform.linear_transform
        self.translation = transform.translation
    
    def Reflection(self, center, vector):
        translation_a = AffineTransform(None, None, -center)
        translation_b = AffineTransform(None, None, center)
        reflection = AffineTransform()
        reflection.linear_transform.Reflection(vector)
        transform = translation_b * reflection * translation_a
        self.linear_transform = transform.linear_transform
        self.translation = transform.translation
    
    def Translation(self, translation):
        self.linear_transform.Identity()
        self.translation = translation
    
    def RigidBodyMotion(self, rotation_angle, translation):
        self.linear_transform.Rotation(rotation_angle)
        self.translation = translation
    
    def Decompose(self):
        pass