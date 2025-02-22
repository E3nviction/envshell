import threading
import time
import sys
import os

from fabric import Application
from fabric.widgets.button import Button
from fabric.widgets.label import Label
from fabric.widgets.shapes import Corner
from fabric.widgets.svg import Svg
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib

from config.c import c
from utils.functions import get_from_socket

class ScreenCorner(Box):
	def __init__(self, corner, size=20):
		super().__init__(
			name="corner-container",
			children=Corner(
				name="corner",
				orientation=corner,
				size=size,
			),
		)

class EnvCorners(Window):
	def __init__(self):
		super().__init__(
			name="corners",
			layer="overlay",
			margin=(-c.get_rule("Panel.height"), 0, -(round(c.get_rule("Dock.size") * 64) + 0 if c.get_rule("Dock.mode") == "full" else 10), 0),
			anchor="top bottom left right",
			exclusivity="normal",
			pass_through=True,
			visible=False,
			all_visible=False,
		)

		self.all_corners = Box(
			name="all-corners",
			orientation="v",
			h_expand=True,
			v_expand=True,
			h_align="fill",
			v_align="fill",
			children=[
				Box(
					name="top-corners",
					orientation="h",
					h_align="fill",
					children=[
						ScreenCorner("top-left"),
						Box(h_expand=True),
						ScreenCorner("top-right"),
					],
				),
				Box(v_expand=True),
				Box(
					name="bottom-corners",
					orientation="h",
					h_align="fill",
					children=[
						ScreenCorner("bottom-left"),
						Box(h_expand=True),
						ScreenCorner("bottom-right"),
					],
				),
			],
		)

		self.add(self.all_corners)

		self.show_all()