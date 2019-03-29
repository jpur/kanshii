from collections import defaultdict
import sys
import helper
import heapq

class Analyzer:
	def __init__(self, best_max_size):
		self.candidates = defaultdict(int)
		self.best_max_size = best_max_size
		self.stroke_count = 0
		self.strokes = []

	def get_similarity(self, next_stroke, stroke_set):
		# Ignore kanji with less strokes than have been made so far
		if len(stroke_set) <= self.stroke_count:
			return -1

		count_stroke = stroke_set[self.stroke_count]

		# Dot product of new stroke and corresponding stroke in kanji. For now, we ignore negative/positive diffs.
		sim = abs(helper.complex_dot(count_stroke.uvec, next_stroke.uvec))
		if self.stroke_count > 0:
			# Unit vector between current and previous stroke in kanji we're checking
			a = helper.complex_uvec(count_stroke.start - stroke_set[self.stroke_count - 1].start)
			# Unit vector between next stroke and previous stroke in our analyzer
			b = helper.complex_uvec(next_stroke.start - self.strokes[-1].start)
			# This contributes to the similarity somehow ..
			sim2 = abs(helper.complex_dot(a, b))
			sim = sim * 0.75 + sim2 * 0.25

		return sim

	def next(self, next_stroke, kanji):
		for k, v in kanji.items():
			sim = self.get_similarity(next_stroke, v)
			if sim < 0: 
				continue

			if abs(sim) > 0.95:
				self.candidates[k] += 2
			elif abs(sim) > 0.8:
				self.candidates[k] += 1
			elif abs(sim) < 0.2:
				self.candidates[k] = -100

		self.stroke_count += 1
		self.strokes.append(next_stroke)

		# Get best matching best_max_size kanji
		pq = []
		bestRat = -sys.maxsize - 1
		for k, v in self.candidates.items():
			if v >= bestRat and len(kanji[k]) == self.stroke_count:
				if len(pq) == self.best_max_size:
					heapq.heapreplace(pq, (v, k)) 
				else:
					heapq.heappush(pq, (v, k))
				bestRat = pq[0][0]
		
		return [{ 'score': pq[i][0], 'img': pq[i][1] } for i in range(len(pq)-1, -1, -1)]