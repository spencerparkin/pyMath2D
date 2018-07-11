# math2d_vector.py

import math
import random

class Vector(object):
    def __init__(self, x=0.0, y=0.0, radius=None, angle=None):
        if angle is not None:
            if radius is None:
                radius = 1.0
            self.x = radius * math.cos(angle)
            self.y = radius * math.sin(angle)
        else:
            self.x = x
            self.y = y
    
    def Serialize(self):
        json_data = {
            'x': self.x,
            'y': self.y
        }
        return json_data

    def Deserialize(self, json_data):
        self.x = json_data['x']
        self.y = json_data['y']
        return self
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)
    
    def __div__(self, other):
        return Vector(self.x / other, self.y / other)
    
    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __hash__(self):
        return hash(str(self.x) + ',' + str(self.y))

    def Copy(self):
        return Vector(self.x, self.y)
    
    def IsPoint(self, point, epsilon=1e-7):
        return True if (point - self).Length() < epsilon else False
    
    def IsZero(self, epsilon=1e-7):
        return self.IsPoint(Vector(0.0, 0.0), epsilon)
    
    def Length(self):
        return math.sqrt(self.Dot(self))
    
    def Normalize(self):
        try:
            self.Scale(1.0 / self.Length())
            return True
        except ZeroDivisionError:
            return False
    
    def Normalized(self):
        normalized = self.Copy()
        normalized.Normalize()
        return normalized
    
    def Scale(self, scale):
        self.x *= scale
        self.y *= scale
        return self
    
    def Scaled(self, scale):
        scaled = self.Copy()
        scaled.Scale(scale)
        return scaled
    
    def Dot(self, other):
        return self.x * other.x + self.y * other.y
    
    def Cross(self, other):
        return self.x * other.y - self.y * other.x
    
    def Reflected(self, normal):
        return self.Projected(normal) - self.Rejected(normal)
    
    def Projected(self, normal):
        return normal * self.Dot(normal)
    
    def Rejected(self, normal):
        return self - self.Projected(normal)
    
    def Rotated(self, angle):
        result = self.Complex() * Vector(angle=angle).Complex()
        return Vector(result.real, result.imag)

    def RotatedCCW90(self):
        return Vector(-self.y, self.x)

    def RotatedCW90(self):
        return Vector(self.y, -self.x)
    
    def Complex(self):
        return complex(self.x, self.y)
    
    def AngleBetween(self, vector):
        normal_vector_a = self.Copy()
        normal_vector_a.Normalize()
        normal_vector_b = vector.Copy()
        normal_vector_b.Normalize()
        dot = normal_vector_a.Dot(normal_vector_b)
        try:
            angle = math.acos(dot)
        except ValueError:
            if dot < -1.0:
                dot = -1.0
            elif dot > 1.0:
                dot = 1.0
            angle = math.acos(dot)
        return angle

    def SignedAngleBetween(self, vector):
        angle = self.AngleBetween(vector)
        return angle if self.Cross(vector) >= 0.0 else -angle

    def Render(self, point, arrow_head_length=0.3):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_LINES
        from math2d_affine_transform import AffineTransform
        from math2d_line_segment import LineSegment
        transform = AffineTransform()
        transform.linear_transform.x_axis = self.Normalized()
        transform.linear_transform.y_axis = transform.linear_transform.x_axis.Rotated(math.pi / 2.0)
        transform.translation = point
        line_segment_list = []
        head = Vector(self.Length(), 0.0)
        line_segment_list.append(LineSegment(Vector(0.0, 0.0), head))
        line_segment_list.append(LineSegment(head, head + Vector(radius=arrow_head_length, angle=(7.0 / 8.0) * math.pi)))
        line_segment_list.append(LineSegment(head, head + Vector(radius=arrow_head_length, angle=-(7.0 / 8.0) * math.pi)))
        glBegin(GL_LINES)
        try:
            for line_segment in line_segment_list:
                line_segment = transform * line_segment
                glVertex2f(line_segment.point_a.x, line_segment.point_a.y)
                glVertex2f(line_segment.point_b.x, line_segment.point_b.y)
        finally:
            glEnd()
    
    def Random(self, component_min=0.0, component_max=1.0):
        self.x = random.uniform(component_min, component_max)
        self.y = random.uniform(component_min, component_max)
        return self