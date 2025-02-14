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

class EnvLight(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="overlay",
			anchor="center center",
			exclusivity="auto",
			name="env-light",
			all_visible=True,
			size=(600, 64),
			visible=True,
			keyboard_mode="exclusive",
			pass_through=False,
			**kwargs,
		)

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
						Entry(placeholder="Envlight Search", name="light-entry"),
					]
				),
				Label("Suggestion 1", name="light-suggestions-label", h_align="start"),
				Label("Suggestion 2", name="light-suggestions-label", h_align="start"),
				Label("Suggestion 3", name="light-suggestions-label", h_align="start"),
				Label("Suggestion 4", name="light-suggestions-label", h_align="start"),
				Label("Suggestion 5", name="light-suggestions-label", h_align="start"),
			],
		)

		# exit keybind
		self.add_keybinding("Escape", lambda *_: self.hide())

		self.children = [
			self.light
		]
		self.show_all()