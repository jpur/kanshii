from collections import defaultdict
import queue
import sys

class Analyzer:
	def __init__(self, best_max_size):
		self.candidates = defaultdict(int)
		self.best_max_size = best_max_size
		self.stroke_count = 0

	def next(self, next_stroke, kanji_list, kanji_dict):
		for stroke_set in kanji_list:
			# Ignore kanji with less strokes than have been made so far
			if len(stroke_set[1]) <= self.stroke_count:
				continue

			kanji_stroke = stroke_set[1][self.stroke_count]

			# Dot product of new stroke and corresponding stroke in kanji. We'll clean this up later.
			dot = kanji_stroke.real * next_stroke.real + kanji_stroke.imag * next_stroke.imag
			if abs(dot) > 0.95:
				self.candidates[stroke_set[0]] += 2
			elif abs(dot) > 0.8:
				self.candidates[stroke_set[0]] += 1
			elif abs(dot) < 0.2:
				self.candidates[stroke_set[0]] = -100

		self.stroke_count += 1

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