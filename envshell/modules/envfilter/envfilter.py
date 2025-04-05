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
from styledwidgets.color import alpha, constrain, rgb

from config.c import c
from utils.functions import get_from_socket

from gi.repository import GtkLayerShell # type: ignore

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
					border_radius=px(12),
					transition=transitions.normal,
					padding=px(0),
				)
			}),
			**kwargs,
		)

		if c.get_rule("ScreenFilter.effect") in self.get_effects():
			self.set_style(self.get_effects()[c.get_rule("ScreenFilter.effect")])

		GtkLayerShell.set_exclusive_zone(self, -1)

		self.set_size_request(1920, 1080)

		self.children = []
		self.show_all()

		self.start_update_thread()

	def get_effects(self):
		temperature = constrain(c.get_rule("ScreenFilter.redshift.temperature"), 1000, 10000)
		temppercent = (temperature/10000) * 2
		val = constrain(int(127.5 * temppercent), 0, 255)

		effects = {
			"none": styler({
				"default": style_dict(
					background_color=alpha(colors.orange, 0),
				)
			}),
			"redshift": styler({
				"default": style_dict(
					background_color=alpha(
						rgb(
							constrain(val*c.get_rule("ScreenFilter.redshift.brightness"), 0, 255),
							constrain(50*c.get_rule("ScreenFilter.redshift.brightness"), 0, 255),
							constrain(50*c.get_rule("ScreenFilter.redshift.brightness"), 0, 255)
						),
						c.get_rule("ScreenFilter.redshift.strength")
					),
				)
			}),
			"nightshift": styler({
				"default": style_dict(
					background_color=alpha(
						rgb(
							constrain(val*c.get_rule("ScreenFilter.nightshift.brightness"), 0, 255),
							constrain(165*c.get_rule("ScreenFilter.nightshift.brightness"), 0, 255),
							constrain(100*c.get_rule("ScreenFilter.nightshift.brightness"), 0, 255),
						),
						c.get_rule("ScreenFilter.nightshift.strength")
					),
					border_radius=px(0),
					transition=transitions.normal,
					padding=px(0),
				)
			}),
		}
		return effects

	def start_update_thread(self):
		rules: list[dict] = c.get_rule("ScreenFilter.rules")
		def run():
			try:
				while True:

					for rule in rules:
						type = rule["type"]
						ifcmd = rule["if"]
						iscmd = rule["is"]
						then = rule["then"]
						if type == "shell":
							output = subprocess.check_output(ifcmd, shell=True).decode().strip()
							if output == iscmd:
								if not (then in self.get_effects()):
									print(f"Invalid effect: {then}")
									continue
								self.set_style(self.get_effects()[then], append=True)
						elif type == "python":
							output = exec(ifcmd)
							if output == iscmd:
								if not (then in self.get_effects()):
									print(f"Invalid effect: {then}")
									continue
								self.set_style(self.get_effects()[then], append=True)
					time.sleep(c.get_rule("ScreenFilter.advanced.update_interval"))
			except KeyboardInterrupt: pass

		threading.Thread(target=run, daemon=True).start()