import os
import math
import uuid
import xml.etree.ElementTree
import helper
from analyzer import Analyzer
from flask import Flask, render_template, request, jsonify, url_for
from svg.path import Path, parse_path
from collections import namedtuple

Stroke = namedtuple('Stroke', 'start uvec')

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
			p_vec = path.point(1) - path.point(0)
			p_uvec = helper.complex_uvec(p_vec)
			strokeSet.append(Stroke(path.point(0), p_uvec))

		kanji[fname] = strokeSet

@app.route('/')
def index():
	uid = uuid.uuid4()
	user_data[uid] = Analyzer(3)
	return render_template('index.html', uuid=uid)

@app.route('/reset_line', methods=['POST'])
def reset_line():
	uid = uuid.UUID(request.get_json()['uuid'])
	user_data[uid] = Analyzer(3)
	return jsonify(result='Success')

@app.route('/compare_line', methods=['POST'])
def compare_line():
	req = request.get_json();
	uid = uuid.UUID(req['uuid'])
	analyzer = user_data[uid]
	
	uvec = complex(req['line']['uvec'][0], req['line']['uvec'][1])
	start = complex(req['line']['start'][0], req['line']['start'][1])
	stroke = Stroke(start, uvec)
	
	return jsonify(analyzer.next(stroke, kanji))