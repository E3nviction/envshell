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

from .bluetooth import BluetoohConnections
from .player import Player

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
			children=[Player()]
		)

		self.has_bluetooth_open = False

		self.bluetooth_svg = Svg(svg_file=get_relative_path("../../assets/svgs/bluetooth.svg" if bluetooth == "On" else "../../assets/svgs/bluetooth-off.svg"), style_classes="icon")

		self.bluetooth_man = BluetoohConnections(self)
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
			on_clicked=self.open_bluetooth
		)

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

		self.bluetooth_widgets = exml(
			file=get_relative_path("envcontrolcenter-bluetooth.xml"),
			root=Box,
			tags={
				"Box": Box,
				"Button": Button,
				"Label": Label,
				"Scale": Scale,
				"Svg": Svg
			},
			refs={"self.bluetooth_man": self.bluetooth_man}
		)

		self.center_box =CenterBox(
			start_children=[self.widgets]
		)

		self.bluetooth_center_box =CenterBox(
			start_children=[self.bluetooth_widgets]
		)

		self.children = self.center_box

		self.bluetooth_fabricator = Fabricator(
			interval=5000,
			default_value=False,
			poll_from=self.bluetooth_can_scan,
			on_changed=self.bluetooth_change_scan
		)
		self.bluetooth_fabricator.start()

		self.start_update_thread()

	def set_dont_disturb(self, *_):
		self.focus_mode = not self.focus_mode
		envshell_service.dont_disturb = self.focus_mode
		self.focus_icon.set_from_file(get_relative_path("../../assets/svgs/dnd.svg" if self.focus_mode else "../../assets/svgs/dnd-off.svg"))

	def set_volume(self, _, __, volume):
		audio_service.speaker.volume = round(volume) # type: ignore

	def bluetooth_can_scan(self, *_):
		return self.has_bluetooth_open

	def set_children(self, children): self.children = children

	def open_bluetooth(self, *_):
		idle_add(lambda *_: self.set_children(self.bluetooth_center_box))
		self.has_bluetooth_open = True

	def close_bluetooth(self, *_):
		idle_add(lambda *_: self.set_children(self.center_box))
		self.has_bluetooth_open = False

	def _set_mousecatcher(self, visible: bool):
		self.set_visible(visible)
		if not visible:
			self.close_bluetooth()
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

	def bluetooth_change_scan(self, f, v):
		if v == False:
			self.bluetooth_man.client.scanning = False
		else:
			self.bluetooth_man.client.scanning = True
	def start_update_thread(self):
		def run():
			try:
				while True:
					self.smode = get_from_socket()[0]

					wlan = subprocess.run("iwgetid -r", shell=True, capture_output=True, text=True)
					if self.smode != True:
						envshell_service.wlan = c.get_rule("Wifi.sentry-mode-wifi")
					else:
						envshell_service.wlan = "No Connection" if wlan.stdout.strip() == "" else wlan.stdout.strip()

					bluetooth = subprocess.run("bluetoothctl show | grep Powered | awk '{print $2}'", shell=True, capture_output=True, text=True)
					envshell_service.bluetooth = "On" if bluetooth.stdout.strip() == "yes" else "Off"

					time.sleep(0.5)
			except KeyboardInterrupt: pass

		threading.Thread(target=run, daemon=True).start()
