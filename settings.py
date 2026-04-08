import os
import json

def load(file):
	if not os.path.isfile(file) or len(open(file, "r").read().strip()) == 0:
		with open(file, "w") as f:
			f.write("{}")

	with open(file, "r") as f:
		return json.loads(f.read())

def write(file, settings):
	with open(file, "w") as f:
		f.write(json.dumps(settings))
