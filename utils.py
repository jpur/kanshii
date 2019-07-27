import os
import xml.etree.ElementTree
import helper
from collections import namedtuple
from svg.path import Path, parse_path

Stroke = namedtuple('Stroke', 'start uvec')

# Populate dictionary with kanji stroke data from SVGs contained in the given directory
def calculate_paths(dirPath):
	# Populate our kanji stroke data dictionary
	kanji = {}
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
	return kanji