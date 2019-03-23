import os
import math
import sys
import uuid
import xml.etree.ElementTree
import queue
from collections import defaultdict
from flask import Flask, render_template, request, jsonify, url_for
from svg.path import Path, parse_path

class DrawData:
	def __init__(self):
		self.candidates = defaultdict(int)
		self.strokeCount = 0

strokes = []
kanji = {}
user_data = {}
max_matches = 3

app = Flask(__name__)

@app.before_first_request
def calculate_paths():
	dirPath = os.path.join(app.root_path, 'static', 'kanji')
	for fname in os.listdir(dirPath):
		e = xml.etree.ElementTree.parse(os.path.join(dirPath, fname)).getroot()
		strokeSet = []
		for stroke in e.iter("{http://www.w3.org/2000/svg}path"):
			path = parse_path(stroke.attrib['d'])

			# Add unit vector of path between start and end points to stroke set
			p_vec = path.point(1)-path.point(0)
			mag = math.sqrt(p_vec.real**2 + p_vec.imag**2)
			p_uvec = complex(p_vec.real/mag, p_vec.imag/mag) if mag else complex(0, 0)
			strokeSet.append(p_uvec)

		strokes.append((fname, strokeSet))
		kanji[fname] = strokeSet

@app.route('/')
def index():
	uid = uuid.uuid4()
	user_data[uid] = DrawData()
	return render_template('index.html', uuid=uid)

@app.route('/reset_line', methods=['POST'])
def reset_line():
	uid = uuid.UUID(request.get_json()['uuid'])
	user_data[uid].strokeCount = 0
	user_data[uid].candidates.clear()
	return jsonify(result='Success')

@app.route('/compare_line', methods=['POST'])
def compare_line():
	uid = uuid.UUID(request.get_json()['uuid'])
	data = user_data[uid]

	req = request.get_json();
	vec = complex(req['line'][0], req['line'][1])
	
	for sset in strokes:
		if len(sset[1]) <= data.strokeCount:
			continue

		# We'll clean this up later
		s = sset[1][data.strokeCount]
		dot = s.real * vec.real + s.imag * vec.imag
		if abs(dot) > 0.95:
			data.candidates[sset[0]] += 2
		elif abs(dot) > 0.8:
			data.candidates[sset[0]] += 1
		elif abs(dot) < 0.2:
			data.candidates[sset[0]] = -100

	data.strokeCount += 1


	pq = queue.PriorityQueue(max_matches)
	best = None
	bestRat = -sys.maxsize - 1
	for k, v in data.candidates.items():
		if v >= bestRat and len(kanji[k]) == data.strokeCount:
			bestRat = v
			best = k
			if pq.full():
				pq.get()
			pq.put((bestRat, best))

	res = []
	while not pq.empty():
		n = pq.get()
		res.append({ 'score': n[0], 'img': url_for('static', filename='kanji/' + n[1]) })

	return jsonify(res[::-1])