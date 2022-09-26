# math2d_line_segment.py

import math

from math2d_vector import Vector

class LineSegment(object):
    def __init__(self, point_a=None, point_b=None):
        self.point_a = point_a if point_a is not None else Vector(0.0, 0.0)
        self.point_b = point_b if point_b is not None else Vector(0.0, 0.0)

    def Serialize(self):
        json_data = {
            'point_a': self.point_a.Serialize(),
            'point_b': self.point_b.Serialize()
        }
        return json_data

    def Deserialize(self, json_data):
        self.point_a = Vector().Deserialize(json_data['point_a'])
        self.point_b = Vector().Deserialize(json_data['point_b'])
        return self

    def Copy(self):
        return LineSegment(self.point_a.Copy(), self.point_b.Copy())
    
    def Direction(self):
        return self.point_b - self.point_a
    
    def Length(self):
        return self.Direction().Length()
    
    def Lerp(self, lerp_value):
        return self.point_a + (self.point_b - self.point_a) * lerp_value
    
    def LerpValue(self, point, epsilon=1e-7):
        try:
            vector_a = self.point_b - self.point_a
            vector_b = point - self.point_a
            cross = vector_a.Cross(vector_b)
            if math.fabs(cross) >= epsilon:
                return None
            lerp_value = vector_a.Dot(vector_b) / vector_a.Dot(vector_a)
            return lerp_value
        except ZeroDivisionError:
            return None
    
    def ContainsPoint(self, point, epsilon=1e-7):
        lerp_value = self.LerpValue(point, epsilon)
        if lerp_value is None:
            return False
        return True if -epsilon < lerp_value < 1.0 + epsilon else False
    
    def IsEndPoint(self, point, epsilon=1e-7):
        return self.point_a.IsPoint(point, epsilon) or self.point_b.IsPoint(point, epsilon)

    def IntersectWith(self, other, epsilon=1e-7):
        if isinstance(other, LineSegment):
            numer_a = (other.point_b - other.point_a).Cross(self.point_a - other.point_a)
            numer_b = (self.point_b - self.point_a).Cross(other.point_a - self.point_a)
            denom = (self.point_b - self.point_a).Cross(other.point_b - other.point_a)
            try:
                lerp_value_a = numer_a / denom
                lerp_value_b = numer_b / -denom
            except ZeroDivisionError:
                return None
            if -epsilon <= lerp_value_a <= 1.0 + epsilon and -epsilon <= lerp_value_b <= 1.0 + epsilon:
                point = self.Lerp(lerp_value_a)
                # Let's scrutinize further.  Two disjoint and parallel line segments sometimes warrant this.
                if self.ContainsPoint(point, epsilon) and other.ContainsPoint(point, epsilon):
                    return point
                else:
                    return None
    
    def Distance(self, point):
        return (point - self.ClosestPoint(point)).Length()
    
    def ClosestPoint(self, point):
        vector = (self.point_b - self.point_a).Normalized()
        length = (point - self.point_a).Dot(vector)
        if length < 0.0:
            return self.point_a
        elif length > self.Length():
            return self.point_b
        else:
            return self.point_a + vector * length

    # TODO: I believe this algorithm, although it often returns the right result, is wrong.
    #       I can think of a case where it fails.  Fix it.  Note that the divide and conqur
    #       technique here is pointless and the "arbitrarily choose list B" thing is wrong.
    @staticmethod
    def ReduceLineList(given_line_list, epsilon):
        if len(given_line_list) < 2:
            return given_line_list
        else:
            i = int(len(given_line_list) / 2 if len(given_line_list) % 2 == 0 else (len(given_line_list) + 1) / 2)
            line_list_a = given_line_list[0:i]
            line_list_b = given_line_list[i:]
            line_list_a = LineSegment.ReduceLineList(line_list_a, epsilon)
            line_list_b = LineSegment.ReduceLineList(line_list_b, epsilon)

            pair_queue = []
            for i in range(len(line_list_a)):
                for j in range(len(line_list_b)):
                    pair_queue.append((i, j))

            while(len(pair_queue) > 0):
                pair = pair_queue.pop()
                line_seg_a = line_list_a[pair[0]]
                line_seg_b = line_list_b[pair[1]]
                line_seg = LineSegment.CompressLineSegments(line_seg_a, line_seg_b, epsilon)
                if line_seg is not None:
                    line_list_a[pair[0]] = None
                    line_list_b[pair[1]] = None
                    pair_queue = [queued_pair for queued_pair in pair_queue if queued_pair[0] != pair[0] and queued_pair[1] != pair[1]]
                    line_list_b.append(line_seg)        # Arbitrarily choose list B.
                    for i in range(len(line_list_a)):
                        if line_list_a[i] is not None:
                            pair_queue.append((i, len(line_list_b) - 1))

            line_list_a = [line for line in line_list_a if line is not None]
            line_list_b = [line for line in line_list_b if line is not None]
            return line_list_a + line_list_b

    @staticmethod
    def CompressLineSegments(line_seg_a, line_seg_b, epsilon):
        if line_seg_a.point_a.IsPoint(line_seg_b.point_a, epsilon) and line_seg_a.point_b.IsPoint(line_seg_b.point_b, epsilon):
            return line_seg_a
        elif line_seg_a.point_a.IsPoint(line_seg_b.point_b, epsilon) and line_seg_a.point_b.IsPoint(line_seg_b.point_a, epsilon):
            return line_seg_a

        mid_point = None
        if line_seg_a.IsEndPoint(line_seg_b.point_a):
            mid_point = line_seg_b.point_a
        elif line_seg_a.IsEndPoint(line_seg_b.point_b):
            mid_point = line_seg_b.point_b

        if mid_point is not None:
            point_a = line_seg_a.point_a if not line_seg_a.point_a.IsPoint(mid_point, epsilon) else line_seg_a.point_b
            point_b = line_seg_b.point_a if not line_seg_b.point_a.IsPoint(mid_point, epsilon) else line_seg_b.point_b

            new_line_seg = LineSegment(point_a=point_a, point_b=point_b)
            distance = new_line_seg.Distance(mid_point)
            if distance < epsilon:
                return new_line_seg