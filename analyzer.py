from collections import defaultdict
import queue
import sys
import helper

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

	def next(self, next_stroke, kanji_list, kanji_dict):
		for k in kanji_list:
			sim = self.get_similarity(next_stroke, k[1])
			if sim < 0: 
				continue

			if abs(sim) > 0.95:
				self.candidates[k[0]] += 2
			elif abs(sim) > 0.8:
				self.candidates[k[0]] += 1
			elif abs(sim) < 0.2:
				self.candidates[k[0]] = -100

		self.stroke_count += 1
		self.strokes.append(next_stroke)

		# Get best matching best_max_size kanji
		pq = queue.PriorityQueue(self.best_max_size)
		bestRat = -sys.maxsize - 1
		for k, v in self.candidates.items():
			if v >= bestRat and len(kanji_dict[k]) == self.stroke_count:
				bestRat = v
				if pq.full():
					pq.get()
				pq.put((bestRat, k))

		res = []
		while not pq.empty():
			n = pq.get()
			res.append({ 'score': n[0], 'img': n[1] })

		return res[::-1]