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

from config.c import c
from utils.functions import get_from_socket

class EnvFilter(Window):
	"""Screen Filters for envshell, like Nightlight, Redshift, etc."""
	def __init__(self, **kwargs):
		super().__init__(
			layer="overlay",
			anchor="top bottom left right",
			exclusivity="none",
			name="env-filter",
			all_visible=True,
			visible=True,
			style=styler({
				"default": style_dict(
					background_color=colors.black,
					transition=transitions.normal,
					border_radius=borderradius(0, 0, 0, 0),
					padding=paddings(0, 0, 0, 0),
					margin=margins(0, 0, 0, 0),
				)
			}),
			margin=(-(c.get_rule("Panel.height")), 10, 10, 10),
			**kwargs,
		)

		self.children = []
		self.show_all()