import helper
import math
from bisect import bisect_left, bisect_right

class UVList:
	def __init__(self, vectors, key):
		self.angles = [(self.get_angle(key(v)), v) for v in vectors]
		self.angles.sort(key=lambda v: v[0])
		self.keys = [v[0] for v in self.angles]

	def get_angle(self, v):
		return math.atan2(v.real, v.imag)

	def find_nearest_all(self, v, max_angle_diff):
		left_idx = bisect_left(self.keys, self.get_angle(v) - max_angle_diff)
		right_idx = bisect_left(self.keys, self.get_angle(v) + max_angle_diff)
		return [self.angles[i][1] for i in range(left_idx, min(right_idx, len(self.keys)))]

	def find_nearest(self, v):
		idx = bisect_left(self.keys, self.get_angle(v))
		return self.angles[idx][1]