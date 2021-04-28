# math2d_spline.py

import math

from math2d_vector import Vector

class Spline(object):
    def __init__(self):
        self.point_list = []

    def Deserialize(self, json_data):
        self.point_list = [Vector().Deserialize(point_data) for point_data in json_data]
        return self

    def Serialize(self):
        return [point.Serialize() for point in self.point_list]

    def Interpolate(self, value):
        # All derivatives should provide a parametrization in [0,1].
        # Ideally, if the curve has length L, then a parameter P would yield
        # the point on the curve along it at length L*P.  If this property is
        # satisfied, then we'll say the curve has a uniform parameterization.
        raise Exception('Pure virtual call.')

    def FindStepSizeForDistance(self, value, distance, step_size_delta = 0.05, eps = 0.01):
        step_size = 0.05
        pointA = self.Interpolate(value)
        while True:
            pointB = self.Interpolate(value + step_size)
            length = (pointA - pointB).Length()
            if math.fabs(length - distance) < eps:
                break
            if (length > distance and step_size_delta > 0.0) or (length < distance and step_size_delta < 0.0):
                step_size_delta = -step_size_delta / 2.0
            step_size += step_size_delta
        return step_size

    def Length(self):
        pass
        # A default implementation here could integrate along the spline.
        # We would want to use adaptive step sizing to account for non-uniform parametrizations.

    def Render(self, step_length=0.0, step_size=0.5):
        from OpenGL.GL import glBegin, glEnd, glVertex2f, GL_LINE_STRIP
        glBegin(GL_LINE_STRIP)
        value = 0.0
        try:
            while value < 1.0:
                point = self.Interpolate(value)
                glVertex2f(point.x, point.y)
                if step_length > 0.0:
                    step_size = self.FindStepSizeForDistance(value, step_length)
                value += step_size
            value = 1.0
            point = self.Interpolate(value)
            glVertex2f(point.x, point.y)
        finally:
            glEnd()

class PolylineSpline(Spline):
    def __init__(self):
        super().__init__()

    def Interpolate(self, value, length=None):
        from math2d_line_segment import LineSegment
        if length is None:
            length = self.Length()
        distance = length * value
        if distance < 0.0 or distance > length:
            raise Exception('Invalid parameter value.')
        i = 0
        point = None
        while distance >= 0.0:
            point = self.point_list[i]
            line_segment = LineSegment(self.point_list[i], self.point_list[i + 1])
            segment_length = line_segment.Lenght()
            if segment_length < distance:
                distance -= segment_length
                i += 1
            else:
                lerp_value = segment_length / distance
                point = line_segment.Lerp(lerp_value)
                break
        return point

    def Length(self):
        from math2d_line_segment import LineSegment
        if len(self.point_list) < 2:
            return 0.0
        length = 0.0
        for i in range(len(self.point_list) - 1):
            line_segment = LineSegment(self.point_list[i], self.point_list[i + 1])
            length += line_segment.Length()
        return length

class BezierSpline(Spline):
    def __init__(self):
        super().__init__()

    def Interpolate(self, value):
        from math2d_line_segment import LineSegment
        point_list = [point for point in self.point_list]
        while len(point_list) > 1:
            new_point_list = []
            for i in range(len(point_list) - 1):
                line_segment = LineSegment(point_list[i], point_list[i + 1])
                new_point_list.append(line_segment.Lerp(value))
            point_list = new_point_list
        return point_list[0]

class HermiteSpline(Spline):
    def __init__(self):
        super().__init__()

    def Deserialize(self, json_data):
        if type(json_data) is list:
            return super().Deserialize(json_data)
        elif type(json_data) is dict:
            self.point_list = []
            self.point_list.append(Vector().Deserialize(json_data['start_pos']))
            self.point_list.append(Vector().Deserialize(json_data['end_pos']))
            self.point_list.append(Vector().Deserialize(json_data['start_tan']))
            self.point_list.append(Vector().Deserialize(json_data['end_tan']))
            return self

    def Serialize(self):
        json_data = {
            'start_pos': self.point_list[0].Serialize(),
            'end_pos': self.point_list[1].Serialize(),
            'start_tan': self.point_list[2].Serialize(),
            'end_tan': self.point_list[3].Serialize()
        }
        return json_data

    def Interpolate(self, value):
        value_squared = value * value
        value_cubed = value_squared * value
        start_pos = self.point_list[0]
        end_pos = self.point_list[1]
        start_tan = self.point_list[2]
        end_tan = self.point_list[3]
        return (start_pos * ((2.0 * value_cubed) - (3.0 * value_squared) + 1.0)) +\
               (start_tan * (value_cubed - (2.0 * value_squared) + value)) +\
               (end_tan * (value_cubed - value_squared)) +\
               (end_pos * ((-2.0 * value_cubed) + (3.0 * value_squared)))