import datetime
import os
import json
import re
import sys
import subprocess
import tomllib
import shutil
from typing import Dict, List, Literal

import gi # type: ignore
from fabric.utils import exec_shell_command, exec_shell_command_async, get_relative_path
from fabric.widgets.image import Image
from gi.repository import Gdk, GLib, Gtk # type: ignore
from loguru import logger


global envshell_service
from utils.roam import envshell_service

from config.c import c

def apply_style(app):
	logger.info("[Main] Applying CSS")
	app.set_stylesheet_from_file(get_relative_path("../envshell.css"))

def set_socket(value):
	try:
		with open(f"/tmp/envshell.socket", "w") as f:
			# clear file
			f.truncate(0)
			# write value
			f.write(value)
	except Exception as e:
		logger.error("[Main] Failed to create socket:", e)
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
		logger.error("[Main] Failed to read from socket:", e)
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
		logger.error("[Main] Failed to write to socket:", e)
		sys.exit(1)

def get_socket_signal(socket):
	if not os.path.exists(os.path.join("/tmp/", socket)):
		with open(os.path.join("/tmp/", socket), "w") as f:
			f.write("{}")
	with open(os.path.join("/tmp/", socket), "r") as f:
		return json.load(f)

class AppName:
	def __init__(self, path="/run/current-system/sw/share/applications"):
		self.files = os.listdir(path)
		self.path = path

	def get_app_name(self, wmclass, format_=False):
		desktop_file = ""
		for f in self.files:
			if f.startswith(wmclass + ".desktop"): desktop_file = f

		desktop_app_name = wmclass

		if desktop_file == "": return wmclass
		with open(os.path.join(self.path, desktop_file), "r") as f:
			lines = f.readlines()
			for line in lines:
				if line.startswith("Name="):
					desktop_app_name = line.split("=")[1].strip()
					break
		return desktop_app_name

	def format_app_name(self, title, wmclass, update=False):
		name = wmclass
		if name == "": name = title
		manual = c.get_rule("Window.translate.force-manual")
		smart = c.get_rule("Window.translate.smart-title")
		if c.has_title(wmclass=wmclass):
			name = c.get_title(wmclass=wmclass)
		else:
			name = self.get_app_name(wmclass=wmclass)
		if smart:
			name = str(name).title()
			if "." in name:
				name = name.split(".")[-1]
		if update: envshell_service.current_active_app_name = name
		return name

global app_name_class
app_name_class = AppName()