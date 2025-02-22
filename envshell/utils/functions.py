import datetime
import os
import json
import re
import subprocess
import tomllib
import shutil
from typing import Dict, List, Literal

import gi
from fabric.utils import exec_shell_command, exec_shell_command_async, get_relative_path
from fabric.widgets.image import Image
from gi.repository import Gdk, GLib, Gtk
from loguru import logger


global envshell_service
from utils.roam import envshell_service

from config.c import c

def set_socket(value):
	try:
		with open(f"/tmp/envshell.socket", "w") as f:
			# clear file
			f.truncate(0)
			# write value
			f.write(value)
	except Exception as e:
		print("Failed to create socket:", e)
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
		print("Failed to read from socket:", e)
		sys.exit(1)

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
		if c.has_title(wmclass=wmclass, title=title):
			name = c.get_title(wmclass=wmclass, title=title)
		else:
			name = self.get_app_name(wmclass=wmclass)
		if smart:
			name = str(name).split(" ")
			name = " ".join([n[0].upper() + n[1:] for n in name])
			if "." in name:
				name = name.split(".")[-1]
		if update: envshell_service.current_active_app_name = name
		return name

global app_name_class
app_name_class = AppName()