import os
import math
import sys
import uuid
import xml.etree.ElementTree
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

app = Flask(__name__)

@app.before_first_request
def calculate_paths():
	global strokes
	dirPath = os.path.join(app.root_path, 'static', 'kanji')
	files = os.listdir(dirPath)
	for fname in files:
		e = xml.etree.ElementTree.parse(os.path.join(dirPath, fname)).getroot()
		strokeSet = []
		for stroke in e.iter("{http://www.w3.org/2000/svg}path"):
			path = parse_path(stroke.attrib['d'])
			p_start = path.point(0)
			p_end = path.point(1)
			p_vec = p_end-p_start
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

		s = sset[1][data.strokeCount]
		dot = s.real * vec.real + s.imag * vec.imag
		if abs(dot) > 0.95:
			data.candidates[sset[0]] += 1
		elif abs(dot) < 0.2:
			data.candidates[sset[0]] = -100

	data.strokeCount += 1

	best = None
	bestRat = -sys.maxsize - 1
	for k, v in data.candidates.items():
		if v > bestRat and len(kanji[k]) == data.strokeCount:
			bestRat = v
			best = k

	return jsonify(best=url_for('static', filename='kanji/' + best))