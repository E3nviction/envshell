import subprocess
import threading
import time
import re
import json


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

from widgets.popup_window import PopupWindow

from styledwidgets.styled import styler, style_dict
from styledwidgets.agents import margins, paddings, transitions, colors, shadows, borderradius, textsize
from styledwidgets.types import px, rem
from styledwidgets.color import alpha, hex

from .bluetooth import BluetoothDeviceSlot, BluetoohConnections

class BluetoothWindow(PopupWindow):
	def __init__(self, parent, **kwargs):
		super().__init__(
			parent=parent,
			layer="top",
			anchor="right top",
			margin="2px 10px 0px 0px",
			exclusivity="auto",
			keyboard_mode="on-demand",
			name="control-center-menu",
			visible=False,
			**kwargs,
		)

		self.blue = BluetoohConnections()

		self.box = Box(
			orientation="vertical",
			name="control-center-widgets",
			children=[
				self.blue
			]
		)

		self.event_box = EventBox(child=self.box, all_visible=True)

		self.children = [self.event_box]

		self.add_keybinding("Escape", self.toggle_bluetooth)

		self.fabricator = Fabricator(
			interval=5000,
			default_value=False,
			poll_from=self.can_scan,
			on_changed=self.change_scan
		)
		self.fabricator.start()

	def change_scan(self, f, v):
		if v == False:
			self.blue.client.scanning = False
		else:
			self.blue.client.scanning = True

	def can_scan(self, *_):
		return self.is_visible()

	def toggle_bluetooth(self, *_):
		self.set_visible(False)


"""
Thanks to @slumberdemon for the following code.
reference: https://github.com/SlumberDemon/dotfiles/blob/main/.config/fabric/widgets/sideleft/_player.py
"""
class player(Box):
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

		self.scale.connect("value-changed", lambda *_: self.scale.set_value(int(self.data["position"]) * 100 / int(self.data["duration"])))

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
class EnvControlCenter(Window):
	"""Control Center for envshell"""
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			title="envshell",
			anchor="right top",
			margin="2px 10px 0px 0px",
			exclusivity="auto",
			keyboard_mode="on-demand",
			name="control-center-menu",
			visible=False,
			**kwargs,
		)

		self.focus_mode = False

		volume = 100
		wlan = envshell_service.sc("wlan-changed", self.wlan_changed)
		bluetooth = envshell_service.sc("bluetooth-changed", self.bluetooth_changed)
		music = envshell_service.sc("music-changed", self.audio_changed)

		audio_service.connect("changed", self.audio_changed)
		audio_service.connect("changed", self.volume_changed)

		self.wlan_label = Label(wlan, name="wifi-widget-label", h_align="start")
		self.bluetooth_label = Label(bluetooth, name="bluetooth-widget-label", h_align="start")
		self.volume_icon = Label(" ", name="volume-widget-icon", h_align="start")
		self.volume_scale = Scale(value=volume, min_value=0, max_value=100, increments=(5, 5), name="volume-widget-slider", size=30, h_expand=True)
		self.volume_scale.connect("change-value", self.set_volume)

		self.music_widget = Box(
			name="music-widget",
			children=[player()]
		)

		self.bluetooth_window = BluetoothWindow(parent=self)

		self.bluetooth_svg = Svg(svg_file=get_relative_path("../../assets/svgs/bluetooth.svg" if bluetooth == "On" else "../../assets/svgs/bluetooth-off.svg"), style_classes="icon")

		self.bluetooth_widget = Button(
			name="bluetooth-widget",
			child=Box(
				orientation="h",
				children=[
					self.bluetooth_svg,
					Box(
						name="bluetooth-widget-info",
						orientation="vertical",
						children=[
							Label(label="Bluetooth", style_classes="title ct", h_align="start"),
							self.bluetooth_label
						]
					),
				]
			),
			on_clicked=self.toggle_bluetooth
		)
		self.bluetooth_window.set_pointing_to(self.bluetooth_widget)

		self.wlan_widget = Svg(svg_file=get_relative_path("../../assets/svgs/wifi.svg"), style_classes="icon") if wlan != "No Connection" else Svg(svg_file=get_relative_path("../../assets/svgs/wifi-off.svg"), style_classes="icon")

		self.focus_icon = Svg(svg_file=get_relative_path("../../assets/svgs/dnd-off.svg"), style_classes="icon")

		self.focus_widget = Button(
			name="focus-widget",
			child=Box(
				orientation="h",
				children=[
					self.focus_icon,
					Label(label="Focus", style_classes="title ct", h_align="start"),
				]
			),
			on_clicked=self.set_dont_disturb,
		)

		self.widgets = exml(
			file=get_relative_path("envcontrolcenter.xml"),
			root=Box,
			tags={
				"Box": Box,
				"Button": Button,
				"Label": Label,
				"Scale": Scale,
				"Svg": Svg
			},
			refs={
				"self.wlan_label": self.wlan_label,
				"self.bluetooth_label": self.bluetooth_label,
				"self.volume_scale": self.volume_scale,
				"self.music_widget": self.music_widget,
				"self.volume_icon": self.volume_icon,
				"self.bluetooth_widget": self.bluetooth_widget,
				"self.wlan_widget": self.wlan_widget,
				"self.focus_widget": self.focus_widget,
			}
		)

		self.center_box =CenterBox(
			start_children=[self.widgets]
		)

		self.children = self.center_box

		self.add_keybinding("Escape", self.toggle_cc)
		self.grab_focus()
		self.keyboard_mode = "exclusive"

		self.start_update_thread()

	def set_dont_disturb(self, *_):
		self.focus_mode = not self.focus_mode
		envshell_service.dont_disturb = self.focus_mode
		self.focus_icon.set_from_file(get_relative_path("../../assets/svgs/dnd.svg" if self.focus_mode else "../../assets/svgs/dnd-off.svg"))

	def set_volume(self, _, __, volume):
		audio_service.speaker.volume = round(volume) # type: ignore

	def toggle_bluetooth(self, *_):
		self.set_visible(False)
		self.bluetooth_window.set_visible(not self.bluetooth_window.is_visible())

	def toggle_cc(self, button, *_):
		if self.bluetooth_window.is_visible():
			self.bluetooth_window.set_visible(False)
		else:
			self.set_visible(not self.is_visible())
	def volume_changed(self, _, ):
		GLib.idle_add(lambda: self.volume_scale.set_value(int(audio_service.speaker.volume))) # type: ignore
	def wlan_changed(self, _, wlan):
		self.wlan_widget.set_from_file(get_relative_path("../../assets/svgs/wifi.svg" if wlan != "No Connection" else "../../assets/svgs/wifi-off.svg"))
		GLib.idle_add(lambda: self.wlan_label.set_property("label", wlan))
	def bluetooth_changed(self, _, bluetooth):
		self.bluetooth_svg.set_from_file(get_relative_path("../../assets/svgs/bluetooth.svg" if bluetooth == "On" else "../../assets/svgs/bluetooth-off.svg"))
		GLib.idle_add(lambda: self.bluetooth_label.set_property("label", bluetooth))
	def audio_changed(self, *_):
		pass
	def start_update_thread(self):
		def run():
			try:
				while True:
					self.smode = get_from_socket()[0]

					wlan = subprocess.run("iwgetid -r", shell=True, capture_output=True, text=True)
					if self.smode != True:
						envshell_service.wlan = "PhotonWeb5"
					else:
						envshell_service.wlan = "No Connection" if wlan.stdout.strip() == "" else wlan.stdout.strip()

					bluetooth = subprocess.run("bluetoothctl show | grep Powered | awk '{print $2}'", shell=True, capture_output=True, text=True)
					envshell_service.bluetooth = "On" if bluetooth.stdout.strip() == "yes" else "Off"

					time.sleep(0.5)
			except KeyboardInterrupt: pass

		threading.Thread(target=run, daemon=True).start()