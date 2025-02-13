import threading
import time
import sys
import os

from fabric import Application
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from fabric.widgets.svg import Svg
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib

from config.c import c

class EnvLight(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="overlay",
			anchor="center center",
			exclusivity="none",
			name="env-light",
			all_visible=True,
			visible=True,
			margin=(0, 0, 0, 0),
			**kwargs,
		)

		self.light = Box(
			name="light-content",
			h_expand=True,
			v_expand=True,
			children=[
			],
			size=(200, 24),
		)

		self.children = []