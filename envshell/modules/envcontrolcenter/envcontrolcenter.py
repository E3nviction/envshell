import subprocess
import threading
import time
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
from gi.repository import GLib, Gtk
from fabric import Fabricator

global envshell_service
global audio_service
from utils.roam import envshell_service, audio_service
from utils.exml import exml

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
			h_expand=True,
			orientation="h",
		)

		self.player = player

		self.art = Button(
			name="left-player-art",
			style=styler({
				"#left-player-art": style_dict(
					padding=px(5) + px(20),
					background_size="cover",
					background_color=alpha(colors.black, 0.2),
					border_radius=px(6),
					margin=px(8),
				)
			})
		)
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
			children=[self.title, self.artist, self.controls],
			orientation="v",
			v_align="center",
			h_expand=True,
		)

		self.details = Box(children=[self.info], h_expand=True, v_expand=True)

		self.playerInfo = Fabricator(
			poll_from='playerctl '+("-p "+self.player if self.player else '')+' --follow metadata --format \'{"status": "{{status}}", "artUrl": "{{mpris:artUrl}}", "title": "{{ markup_escape(title) }}", "artist": "{{ markup_escape(artist) }}"}\'',
			stream=True,
			interval=1000,
		)

		def extract_metadata(_, value):
			if value:
				data = json.loads(value)

				self.art.set_style(f"background-image: url('{data['artUrl']}');", append=True)
				self.title.set_label(data["title"])
				self.artist.set_label(data["artist"])
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
				self.art.set_style("background-image: none;", append=True)
				self.title.set_label("Nothing playing")
				self.artist.set_label("")
				self.status.set_markup("")

		self.playerInfo.connect("changed", extract_metadata)

		for connector in [self.backward, self.play, self.forward, self.art]:
			bulk_connect(
				connector,
				{
					"enter-notify-event": lambda *args: self.set_cursor("pointer"),
					"leave-notify-event": lambda *args: self.set_cursor("default"),
					"button-press-event": self.on_button_press,
				},
			)

		self.add(self.art)
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
			anchor="right top",
			margin="2px 10px 0px 0px",
			exclusivity="auto",
			keyboard_mode="on-demand",
			name="control-center-menu",
			visible=False,
			**kwargs,
		)

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

		self.bluetooth_widget = Button(
			name="bluetooth-widget",
			child=Box(
				orientation="h",
				children=[
					Svg(svg_file=get_relative_path("../../assets/svgs/bluetooth.svg"), style_classes="icon"),
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
				"self.wlan_widget": self.wlan_widget
			}
		)

		self.center_box =CenterBox(
			start_children=[self.widgets]
		)

		self.children = self.center_box

		self.add_keybinding("Escape", self.toggle_cc)

		self.start_update_thread()

	def set_volume(self, _, __, volume):
		audio_service.speaker.volume = round(volume)

	def toggle_bluetooth(self, *_):
		self.set_visible(False)
		self.bluetooth_window.set_visible(not self.bluetooth_window.is_visible())

	def toggle_cc(self, button, *_):
		if self.bluetooth_window.is_visible():
			self.bluetooth_window.set_visible(False)
		else:
			self.set_visible(not self.is_visible())
	def volume_changed(self, _, ):
		GLib.idle_add(lambda: self.volume_scale.set_value(int(audio_service.speaker.volume)))
	def wlan_changed(self, _, wlan): GLib.idle_add(lambda: self.wlan_label.set_property("label", wlan))
	def bluetooth_changed(self, _, bluetooth): GLib.idle_add(lambda: self.bluetooth_label.set_property("label", bluetooth))
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