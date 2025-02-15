import threading
import time
import sys
import os

from fabric import Application
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from fabric.widgets.svg import Svg
from fabric.widgets.box import Box
from fabric.widgets.entry import Entry
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib

from config.c import c

apps = {
	"Brave Browser": "brave",
	"Vesktop": "vesktop",
	"Files": "nautilus",
	"Settings": "XDG_CURRENT_DESKTOP=GNOME gnome-control-center",
	"Software": "gnome-software",
	"Disks": "gnome-disks",
	"Calculator": "gnome-calculator",
	"Clocks": "gnome-clocks",
	"Terminal": "gnome-terminal",
	"Maps": "gnome-maps",
	"ChatGPT": "brave --app=https://chat.openai.com/",
}

class EnvLight(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="overlay",
			anchor="center center",
			exclusivity="auto",
			name="env-light",
			all_visible=False,
			h_expand=True,
			v_expand=True,
			size=(600, 64),
			visible=False,
			keyboard_mode="on-demand",
			pass_through=False,
			**kwargs,
		)

		self.entry = Entry(placeholder="Envlight Search", name="light-entry", h_expand=True)

		self.entry.connect("activate", self.submit)
		self.entry.connect("changed", self.update_suggestions)

		self.light = Box(
			name="light-content",
			h_expand=True,
			v_expand=True,
			h_align="start",
			orientation="v",
			size=(600, 64),
			children=[
				Box (
					name="light-header",
					h_expand=True,
					v_expand=True,
					h_align="start",
					orientation="h",
					size=(600, 64),
					children=[
						self.entry,
					]
				),
				Box(
					name="light-suggestions",
					h_expand=True,
					v_expand=True,
					h_align="start",
					orientation="v",
					size=(600, 64),
				),
			],
		)

		# exit keybind
		self.add_keybinding("Escape", lambda *_: self.hide())

		self.children = [
			self.light
		]

	def toggle(self, b):
		if self.get_visible():
			self.hide()
		else:
			self.show_light()

	def show_light(self):
		self.entry.set_text("")
		self.show_all()

	def submit(self, b):
		print(self.entry.get_text())
		self.hide()

	def update_suggestions(self, b):
		# use apps
		SUGGESTIONS = 5
		text = self.entry.get_text()
		fitting = []

		for app in apps.items():
			if str(app[0]).startswith(text):
				fitting.append(
					Button(
						label=app[0],
						name="light-suggestion",
						h_align="start",
						h_expand=True,
						v_expand=True
					)
				)
			if len(fitting) == SUGGESTIONS:
				break

		self.light.children[1].children = fitting
