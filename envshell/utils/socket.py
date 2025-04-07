import os
import json
import sys

def set_socket(value):
	try:
		with open(f"/tmp/envshell.socket", "w") as f:
			# clear file
			f.truncate(0)
			# write value
			f.write(value)
	except Exception as e:
		sys.exit(1)

def get_from_socket():
	try:
		with open(f"/tmp/envshell.socket", "r") as f:
			lines = []
			for line in f:
				line = line.strip()
				if line == "\n": continue
				if line == "false":
					lines.append(False)
					continue
				if line == "true":
					lines.append(True)
					continue
				lines.append(line)
			return lines
	except Exception as e:
		sys.exit(1)

def create_socket_signal(socket: str, name: str, signal: dict):
	try:
		file = "{}"
		if not os.path.exists(os.path.join("/tmp/", os.path.dirname(socket))):
			os.makedirs(os.path.join("/tmp/", os.path.dirname(socket)))
		if not os.path.exists(os.path.join("/tmp/", socket)):
			with open(os.path.join("/tmp/", socket), "w") as f:
				f.write("{}")
		with open(os.path.join("/tmp/", socket), "r") as f:
			file = f.read()
			f.close()
		with open(os.path.join("/tmp/", socket), "w") as f:
			if file == "": file = "{}"
			data = json.loads(file)
			data[name] = signal
			f.write(json.dumps(data))
	except Exception as e:
		sys.exit(1)

def get_socket_signal(socket):
	if not os.path.exists(os.path.join("/tmp/", socket)):
		with open(os.path.join("/tmp/", socket), "w") as f:
			f.write("{}")
	with open(os.path.join("/tmp/", socket), "r") as f:
		return json.load(f)
