# math2d_dsf.py

class DisjointSet(object):
    def __init__(self, data=None):
        self.rep = None
        self.data = data

    def FindRepresentative(self):
        if self.rep is None:
            return self
        else:
            rep = self.rep.FindRepresentative()
            self.rep = rep # This is strictly an optimization.  It is not needed for correctness.
            return rep

    def MergeWith(self, dsf_set):
        if self != dsf_set:
            rep = dsf_set.FindRepresentative()
            rep.rep = self

    def __eq__(self, other):
        rep_a = self.FindRepresentative()
        rep_b = other.FindRepresentative()
        return True if rep_a is rep_b else False