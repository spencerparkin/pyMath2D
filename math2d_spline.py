# math2d_spline.py

# TODO: Not all splines just use control points.  Some use tangent points (i.e., point/vector pairs.)

class Spline(object):
    def __init__(self):
        self.point_list = []

    def Interpolate(self, value):
        # All derivatives should provide a parametrization in [0,1].
        # Ideally, if the curve has length L, then a parameter P would yield
        # the point on the curve along it at length L*P.  If this property is
        # satisfied, then we'll say the curve has a uniform parameterization.
        raise Exception('Pure virtual call.')

    def Length(self):
        pass
        # A default implementation here could integrate along the spline.
        # We would want to use adaptive step sizing to account for non-uniform parametrizations.

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

class BezierSpline(object):
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