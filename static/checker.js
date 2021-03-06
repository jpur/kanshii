var canvas, ctx;
var writing = false;
var currX, currY;
var currLine = []
var pad;

function getMouseX(e) {
	return e.clientX - pad.offset().left;
}

function getMouseY(e) {
	return e.clientY - pad.offset().top;
}

function init() {
	canvas = document.getElementById("write-pad");
	ctx = canvas.getContext("2d");
	pad = $('#write-pad');

	$('#reset-btn').click(reset)

	pad.mousedown(function (e) {
		writing = true;
		currX = getMouseX(e);
		currY = getMouseY(e);
		ctx.beginPath(currX, currY);
	});

	pad.mouseup(function (e) {		
		if (writing) {
			writing = false;
			var res = getLineType(currLine);
			currLine = []
			if (res == null) return;
			sendLine(res);
		}
	});

	pad.mouseout(function (e) {
		if (writing) {
			writing = false;
			var res = getLineType(currLine);
			currLine = []
			if (res == null) return;
			sendLine(res);
		}
	});

	pad.mousemove(function (e) {
		if (writing) {
			var x = getMouseX(e);
			var y = getMouseY(e);
			ctx.moveTo(currX, currY);
			ctx.lineTo(x, y);
			ctx.stroke();
			currX = x;
			currY = y;
			currLine.push([x, y]);
		}
	});
}

function lerp(min, max, p) {
	return min + (max - min) * p;
}

function sendLine(line) {
	var data = {
		'uuid': uuid,
		'line': line
	};

	$.ajax({
		type: "POST",
		url: comp_line_url,
		contentType: "application/json",
		data: JSON.stringify(data),
		dataType: "json",
		success: function(response) {
			max = response[0].score;
			min = response[response.length-1].score;

			$('.best-match').each(function(idx, val) {
				if (idx >= response.length) {
					$(this).css('opacity', 0.1);
					return;
				}

				var p = (response[idx].score - min) / (max - min);
				var bestRatio = response[idx].score / response[0].score;
				$(this).children('.best-match-img').attr("src", kanji_url + "/" + response[idx].img)
				$(this).children('.best-match-img').css('opacity', lerp(0.25, 1, p));
			});
		}
	});
}

function getLineType(line) {
	if (line.length == 0) return;

	var firstPoint = line[0];
	var lastPoint = line[line.length-1];
	var vec = [lastPoint[0]-firstPoint[0], lastPoint[1]-firstPoint[1]];
	var mag = Math.sqrt(Math.pow(vec[0], 2) + Math.pow(vec[1], 2));

	if (mag == 0) {
		return null;
	}

	// Unit vector
	var uvec = [vec[0]/mag, vec[1]/mag]

	// Drift value (currently unused)
	var drift = 0;
	for (var i = 1; i < line.length - 1; i++) {
		var dir = [line[i][0]-line[i-1][0], line[i][1]-line[i-1][1]]
		var mag = Math.sqrt(Math.pow(dir[0], 2) + Math.pow(dir[1], 2));
		var udir = [dir[0]/mag, dir[1]/mag]
		drift += Math.sqrt(Math.pow(udir[0]-uvec[0], 2) + Math.pow(udir[1]-uvec[1], 2));
	}

	return { 'uvec': uvec, 'start': firstPoint };
}

function reset() {
	$.ajax({
		type: "POST",
		url: reset_line_url,
		contentType: "application/json",
		data: JSON.stringify({ "uuid": uuid }),
		dataType: "json",
		success: function(response) {
			ctx.clearRect(0, 0, canvas.width, canvas.height)
		}
	});
}

$(document).ready(init);