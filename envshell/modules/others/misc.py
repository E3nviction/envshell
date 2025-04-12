import subprocess
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
from styledwidgets.color import alpha, color, constrain, rgb

from config.c import c
from utils.functions import get_from_socket

from gi.repository import GtkLayerShell # type: ignore

class ActivateLinux(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer=c.get_rule("Misc.activate-linux.layer") if c.get_rule("Misc.activate-linux.layer") in ['background', 'bottom', 'top', 'overlay'] else "overlay",
			anchor="bottom right",
			exclusivity="none",
			title="envshell-misc-activatelinux",
			name="env-filter",
			all_visible=True,
			visible=True,
			pass_through=True,
			margin=(0, 15, 15, 0),
			style=styler({
				"default": style_dict(
					background_color=alpha(colors.orange, 0),
					border_radius=px(12),
					transition=transitions.normal,
					padding=px(0),
				)
			}),
			**kwargs,
		)

		GtkLayerShell.set_exclusive_zone(self, -1)

		self.children = []
		self.show_all()

		self.add(Box(orientation="v",
			children=[
				Label(
					markup="Activate Linux",
					h_align="start",
					style=styler(
						font_size=rem(1.7),
						color=alpha("#eeeeff", 0.5),
					)
				),
				Label(
					markup="Go to Settings to activate Linux.",
					h_align="start",
					style=styler(
						font_size=rem(1.2),
						color=alpha(colors.white, 0.4),
					)
				)
			]
		))