import os
import math
import uuid
import helper
import utils
from uvlist import UVList
from analyzer import Analyzer
from flask import Flask, render_template, request, jsonify, url_for

# Holds all kanji stroke data
kanji = {}

# Holds analyzers for each user
user_data = {}

# The number of closest matches to return to the user
max_matches = 3

app = Flask(__name__)

@app.before_first_request
def precompute():
	# Initialize stroke data on first request
	global kanji
	svgDataPath = os.path.join(app.root_path, 'static', 'kanji')
	kanji = utils.calculate_paths(svgDataPath)

@app.route('/')
def index():
	uid = uuid.uuid4()
	user_data[uid] = Analyzer(max_matches)
	return render_template('index.html', uuid=uid)

@app.route('/reset_line', methods=['POST'])
def reset_line():
	# Reset the analyzer of the user
	uid = uuid.UUID(request.get_json()['uuid'])
	user_data[uid] = Analyzer(max_matches)
	return jsonify(result='Success')

@app.route('/compare_line', methods=['POST'])
def compare_line():
	req = request.get_json();
	uid = uuid.UUID(req['uuid'])
	analyzer = user_data[uid]
	
	# Get the directional vector of the stroke
	uvec = complex(req['line']['uvec'][0], req['line']['uvec'][1])
	# Get the start position of the stroke
	start = complex(req['line']['start'][0], req['line']['start'][1])
	stroke = utils.Stroke(start, uvec)
	
	res = analyzer.next(stroke, kanji)
	return jsonify(res)