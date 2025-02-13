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

class NotchCorner(Box):
	def __init__(self, corner, size=20):
		super().__init__(
			name="corner-container",
			children=Corner(
				name="notch-corner",
				orientation=corner,
				size=size,
			),
		)

class Corners(Window):
	def __init__(self):
		super().__init__(
			name="corners",
			layer="overlay",
			margin=(-24, 0, -57, 0),
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


class EnvNotch(Window):
	"""Desktop Notch for envshell"""
	def __init__(self, **kwargs):
		super().__init__(
			layer="overlay",
			anchor="top center",
			exclusivity="none",
			name="env-notch",
			all_visible=True,
			visible=True,
			margin=(-24, 10, 10, 10),
			**kwargs,
		)

		self.corners = Corners()

		self.hidden = False

		self.corner_left = Box(
			name="notch-corner-left",
			orientation="h",
			v_align="start",
			h_align="start",
			children=[
				NotchCorner("top-right", 5),
				Box(),
			]
		)

		self.corner_right = Box(
			name="notch-corner-right",
			orientation="h",
			v_align="start",
			h_align="start",
			children=[
				NotchCorner("top-left", 5),
				Box(),
			]
		)

		self.button = Button(
			name="notch-button",
			h_align="fill",
			h_expand=True,
			v_expand=True,
			on_clicked=self.toggle_notch,
		)

		self.smode = get_from_socket()[0]

		self.notch_indicators = Box(name="notch-indicators", orientation="horizontal", h_align="end", v_align="center", h_expand=True, children=[
			Label("●", name="notch-indicator", tooltip_text="Sentry Mode", style_classes="off" if self.smode else ""), # Sentry Mode Indicator
			Label("●", name="notch-indicator", style_classes="off"),                                                   # NotImplemented
		])

		self.notch = Box(
			name="notch-content",
			h_expand=True,
			v_expand=True,
			children=[
				self.button,
				self.notch_indicators,
			],
			size=(200, 24),
		)

		self.children = [
			CenterBox(
				name="notch-box",
				orientation="h",
				h_align="center",
				v_align="center",
				h_expand=True,
				v_expand=True,
				start_children=Box(
					children=[
						self.corner_left,
					],
				),
				center_children=[
					self.notch
				],
				end_children=Box(
					children=[
						self.corner_right,
					]
				)
			),
			self.corners,
		]
		self.show_all()

		self.start_update_thread()

	def toggle_notch(self, b):
		if self.hidden:
			self.remove_style_class("hide")
			self.hidden = False
		else:
			self.add_style_class("hide")
			self.hidden = True

	def start_update_thread(self):
		def run():
			try:
				while True:
					self.smode = get_from_socket()[0]
					self.notch_indicators.children[0].style_classes = "off" if self.smode else ""
					time.sleep(0.5)
			except KeyboardInterrupt: pass

		threading.Thread(target=run, daemon=True).start()
