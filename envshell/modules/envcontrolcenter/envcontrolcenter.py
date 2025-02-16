import subprocess
import threading
import time


from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale
from fabric.widgets.svg import Svg
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.utils.helpers import exec_shell_command_async
from fabric.audio import Audio
from fabric.bluetooth import BluetoothClient, BluetoothDevice
from gi.repository import GLib

global envshell_service
global audio_service
from utils.roam import envshell_service, audio_service
from utils.exml import exml

from utils.functions import get_from_socket

from .bluetooth import BluetoothDeviceSlot, BluetoohConnections

class BluetoothWindow(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor="right top",
			margin="2px 10px 0px 0px",
			exclusivity="auto",
			keyboard_mode="on-demand",
			name="control-center-menu",
			visible=False,
			**kwargs,
		)

		self.children = Box(
			orientation="vertical",
			name="control-center-widgets",
			children=[
				BluetoohConnections()
			]
		)

		self.add_keybinding("Escape", self.toggle_bluetooth)

	def toggle_bluetooth(self, *_):
		self.set_visible(False)


class EnvControlCenter(Window):
	"""Control Center for envshell"""
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor="right top",
			margin="2px 10px 0px 0px",
			exclusivity="auto",
			keyboard_mode="on-demand",
			name="control-center-menu",
			visible=False,
			**kwargs,
		)

		# Default Values
		volume = envshell_service.sc("volume-changed", self.volume_changed, 100)
		wlan = envshell_service.sc("wlan-changed", self.wlan_changed)
		bluetooth = envshell_service.sc("bluetooth-changed", self.bluetooth_changed)
		music = envshell_service.sc("music-changed", self.audio_changed)

		audio_service.connect("changed", self.audio_changed)

		# Labels
		self.wlan_label = Label(wlan, name="wifi-widget-label", h_align="start")
		self.bluetooth_label = Label(bluetooth, name="bluetooth-widget-label", h_align="start")
		self.volume_icon = Label(" ", name="volume-widget-icon", h_align="start")
		self.volume_scale = Scale(value=volume, min_value=0, max_value=100, name="volume-widget-slider", size=30, h_expand=True)
		self.volume_scale.connect("change-value", self.set_volume)
		self.music_label = Label(music, name="music-widget-label", h_align="start")

		self.bluetooth_widget = Button(
			name="bluetooth-widget",
			child=Box(
				orientation="h",
				children=[
					Svg(svg_file="./assets/svgs/bluetooth.svg", style_classes="icon"),
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

		self.bluetooth_window = BluetoothWindow()

		# Widgets
		self.widgets = exml(
			file="./modules/envcontrolcenter/envcontrolcenter.xml",
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
				"self.music_label": self.music_label,
				"self.volume_icon": self.volume_icon,
				"self.bluetooth_widget": self.bluetooth_widget
			}
		)

		self.center_box =CenterBox(
			start_children=[self.widgets]
		)

		# Add Children to Window
		self.children = self.center_box

		self.add_keybinding("Escape", self.toggle_cc)

		# Start Update Thread
		self.start_update_thread()

	def set_volume(self, _, __, volume):
		audio_service.speaker.volume = volume

	def toggle_bluetooth(self, *_):
		self.set_visible(False)
		self.bluetooth_window.set_visible(not self.bluetooth_window.is_visible())

	def toggle_cc(self, button, *_):
		if self.bluetooth_window.is_visible():
			self.bluetooth_window.set_visible(False)
		else:
			self.set_visible(not self.is_visible())
	def volume_changed(self, _, volume): GLib.idle_add(lambda: self.volume_scale.set_value(int(volume)))
	def wlan_changed(self, _, wlan): GLib.idle_add(lambda: self.wlan_label.set_property("label", wlan))
	def bluetooth_changed(self, _, bluetooth): GLib.idle_add(lambda: self.bluetooth_label.set_property("label", bluetooth))
	def audio_changed(self, *_):
		if not audio_service.speaker:
			return
		envshell_service.volume = round(audio_service.speaker.volume)
	def start_update_thread(self):
		def run():
			try:
				while True:
					self.smode = get_from_socket()[0]

					wlan = subprocess.run("iwgetid -r", shell=True, capture_output=True, text=True)
					if self.smode == True:
						envshell_service.wlan = "PhotonWeb5"
					else:
						envshell_service.wlan = "No Connection" if wlan.stdout.strip() == "" else wlan.stdout.strip()

					bluetooth = subprocess.run("bluetoothctl show | grep Powered | awk '{print $2}'", shell=True, capture_output=True, text=True)
					envshell_service.bluetooth = "On" if bluetooth.stdout.strip() == "yes" else "Off"

					time.sleep(0.5)
			except KeyboardInterrupt: pass

		threading.Thread(target=run, daemon=True).start()