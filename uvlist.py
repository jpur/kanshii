import helper
import math
from bisect import bisect_left, bisect_right

# A collection for efficiently searching for similar vectors within a given angle
class UVList:
	# Initialize the collection with a list and a key function which returns a vector given an item from that list
	def __init__(self, vectors, key):
		# Sort all vectors according to their position on the unit circle
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