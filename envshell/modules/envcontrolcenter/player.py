import subprocess
import threading
import time
import re
import json


from fabric.utils import idle_add
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.scale import Scale
from fabric.widgets.svg import Svg
from fabric.widgets.stack import Stack
from fabric.widgets.revealer import Revealer
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.utils.helpers import exec_shell_command_async, get_relative_path, bulk_connect, exec_shell_command
from fabric.audio import Audio
from fabric.bluetooth import BluetoothClient, BluetoothDevice
from gi.repository import GLib, Gtk # type: ignore
from fabric import Fabricator

global envshell_service
global audio_service
from utils.roam import envshell_service, audio_service
from utils.exml import exml

from config.c import c

from utils.functions import get_from_socket

from widgets.popup_window_custom import PopupWindow

from styledwidgets.styled import styler, style_dict
from styledwidgets.agents import margins, paddings, transitions, colors, shadows, borderradius, textsize
from styledwidgets.types import px, rem
from styledwidgets.color import alpha, hex

"""
Thanks to @slumberdemon for the following code.
reference: https://github.com/SlumberDemon/dotfiles/blob/main/.config/fabric/widgets/sideleft/_player.py
"""
class Player(Box):
	def __init__(self, player=None) -> None:
		super().__init__(
			name="left-player",
			style_classes="control-center-widgets",
			h_expand=True,
			orientation="h",
		)

		self.player = player

		self.title = Label(
			label="Nothing playing",
			name="left-player-title",
			justification="center",
			ellipsization="end",
			character_max_width=24,
		)
		self.artist = Label(
			name="left-player-artist",
			justification="center",
			ellipsization="end",
			character_max_width=20,
		)

		self.backward = Button(
			child=Label(markup="", name="left-player-icon")
		)
		self.forward = Button(
			child=Label(markup="", name="left-player-icon")
		)
		self.status = Label(
			markup="", name="left-player-icon", style=styler(font_size=px(36))
		)
		self.play = Button(child=self.status)
		self.time_dur = Label("0:00", name="left-player-duration-label")
		self.time_pos = Label("0:00", name="left-player-position-label")
		self.time = CenterBox(
			name="left-player-time",
			start_children=[self.time_pos],
			end_children=[self.time_dur],
		)

		self.scale = Scale(
			value=0,
			min_value=0,
			max_value=100,
			increments=(5, 5),
			name="left-player-scale",
			style_classes="small",
			size=2,
			h_expand=True,
		)

		self.scale.connect(
			"value-changed",
			lambda *_:
				self.scale.set_value(
					int(self.data["position"]) * 100 / int(self.data["duration"]) if int(self.data["duration"]) > 0 else 0
				)
		)

		self.controls = CenterBox(
			name="left-player-controls",
			start_children=[self.backward],
			center_children=[self.play],
			end_children=[self.forward],
			orientation="h",
			h_expand=True,
		)
		self.info = Box(
			name="left-player-info",
			children=[self.title, self.artist, self.controls, self.time, self.scale],
			orientation="v",
			v_align="center",
			h_expand=True,
		)

		self.details = Box(children=[self.info], h_expand=True, v_expand=True)

		self.playerInfo = Fabricator(
			poll_from='playerctl '+("-p "+self.player if self.player else '')+' --follow metadata --format \'{"status": "{{status}}", "artUrl": "{{mpris:artUrl}}", "title": "{{ markup_escape(title) }}", "artist": "{{ markup_escape(artist) }}", "position": "{{position}}", "duration": "{{mpris:length}}", "sposition": "{{duration(position)}}", "sduration": "{{duration(mpris:length)}}"}\'',
			stream=True,
			interval=1000,
		)

		self.data = {}

		def extract_metadata(_, value):
			if value:
				data = json.loads(value)
				self.data = data
				for i in c.get_rule("MusicPlayer.ignore"):
					if re.match(i["title"]["regex"], data["title"]):
						return
				self.set_style(f"""
					background-image: url('{data['artUrl']}');
					background-size: cover;
					background-color: rgba(0, 0, 0, 0.6); /* 50% black overlay */
					background-blend-mode: darken;
				""", append=True)
				self.title.set_markup(data["title"])
				self.artist.set_label(data["artist"])
				self.time_dur.set_label(
					data["sduration"] if data["sduration"] else "0:00"
				)
				self.time_pos.set_label(
					data["sposition"] if data["sposition"] else "0:00"
				)
				if data["duration"] == "":
					data["duration"] = "0"
				if int(data["duration"]) == 0:
					self.scale.set_value(0)
				else:
					self.scale.set_value(int(data["position"]) * 100 / int(data["duration"]))
				self.status.set_markup(
					(
						""
						if data["status"] == "Stopped"
						else (
							"" if data["status"] == "Playing" else ""
						)
					)
				)
			else:
				self.set_style("background-image: none;background-size: cover;", append=True)
				self.title.set_label("Nothing playing")
				self.time_dur.set_label("0:00")
				self.time_pos.set_label("0:00")
				self.artist.set_label("")
				self.status.set_markup("")
				self.scale.set_value(0)

		self.playerInfo.connect("changed", extract_metadata)

		for connector in [self.backward, self.play, self.forward]:
			bulk_connect(
				connector,
				{
					"enter-notify-event": lambda *args: self.set_cursor("pointer"),
					"leave-notify-event": lambda *args: self.set_cursor("default"),
					"button-press-event": self.on_button_press,
				},
			)
		self.add(self.details)

	def on_button_press(self, button: Button, event):
		if event.button == 1 and event.type == 4:
			if button == self.backward:
				exec_shell_command("playerctl previous")
			elif button == self.play:
				exec_shell_command("playerctl play-pause")
			elif button == self.forward:
				exec_shell_command("playerctl next")
