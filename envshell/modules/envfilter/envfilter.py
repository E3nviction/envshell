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
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib # type: ignore

from styledwidgets.styled import styler, style_dict
from styledwidgets.agents import colors, borderradius, transitions, margins, paddings
from styledwidgets.types import rem, px
from styledwidgets.color import alpha

from config.c import c
from utils.functions import get_from_socket

class BorderGlow(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="overlay",
			anchor="top bottom left right",
			exclusivity="none",
			title="envshell-glow",
			name="env-glow",
			all_visible=True,
			visible=True,
			pass_through=True,
			style=styler({
				"default": style_dict(
					background_color=alpha(colors.orange, 0),
					box_shadow="inset 0 0 10px 1px #f00",
					border_radius=px(12),
					transition=transitions.normal,
					padding=px(0),
				)
			}),
			**kwargs,
		)

		self.set_size_request(1920, 1080)

		if c.get_rule("Panel.mode") == "floating":
			self.set_property("margin", (-(c.get_rule("Panel.height") + 10), 0, 0, 0))
		elif c.get_rule("Panel.mode") == "normal":
			self.set_property("margin", (-(c.get_rule("Panel.height")), 0, 0, 0))

		self.children = []
		self.show_all()

class EnvFilter(Window):
	"""Screen Filters for envshell, like Nightlight, Redshift, etc."""
	def __init__(self, **kwargs):
		super().__init__(
			layer="overlay",
			anchor="top bottom left right",
			exclusivity="none",
			title="envshell-filter",
			name="env-filter",
			all_visible=True,
			visible=True,
			pass_through=True,
			style=styler({
				"default": style_dict(
					background_color=alpha(colors.orange, 0),
					border="1px solid #f00",
					border_radius=px(12),
					transition=transitions.normal,
					padding=px(0),
				)
			}),
			**kwargs,
		)

		self.set_size_request(1920, 1080)

		if c.get_rule("Panel.mode") == "floating":
			self.set_property("margin", (-(c.get_rule("Panel.height") + 10), 0, 0, 0))
		elif c.get_rule("Panel.mode") == "normal":
			self.set_property("margin", (-(c.get_rule("Panel.height")), 0, 0, 0))

		self.children = []
		self.show_all()