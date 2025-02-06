from hmac import new
import subprocess
import threading
import time
import json
import sys
import gi

from fabric import Application
from fabric.core.service import Service, Signal, Property
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale
from fabric.widgets.svg import Svg
from fabric.widgets.wayland import WaylandWindow as Window
gi.require_version("Rsvg", "2.0")
from gi.repository import GLib, Gtk, GdkPixbuf, Rsvg, cairo # type: ignore

from .services import AppNameService

from hyprpy import Hyprland

global instance
from utils.roam import instance

app_names = json.load(open("./envpanel/app_names.json"))


def dropdown_option(self, label: str = "", keybind: str = "", on_click="echo \"EnvPanelDropdown Action\"", on_clicked=None):
	def on_click_subthread(button):
		self.toggle_dropdown(button)
		if on_clicked:
			on_clicked(button)
		else:
			subprocess.run(on_click, shell=True)
	return Button(
		child=CenterBox(
			start_children=[
				Label(label=label, h_align="start", name="dropdown-option-label"),
			],
			end_children=[
				Label(label=keybind, h_align="end", name="dropdown-option-keybind")
			],
			orientation="horizontal",
			h_align="fill",
			h_expand=True,
			v_expand=True,
		),
		name="dropdown-option",
		h_align="fill",
		on_clicked=on_click_subthread,
		h_expand=True,
		v_expand=True,
	)

def dropdown_divider(comment):
	return Box(
		children=[Box(name="dropdown-divider", h_expand=True)],
		name="dropdown-divider-box",
		h_align="fill",
		h_expand=True,
		v_expand=True,
	)

class About(Gtk.Window):
	def __init__(self):
		super().__init__(title="About Menu")
		self.set_default_size(250, 355)
		self.set_size_request(250, 355)
		self.set_resizable(False)
		self.set_wmclass("esh-about-menu", "esh-about-menu")
		self.set_name("about-menu")
		self.set_visible(False)

		# Main vertical box
		main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		main_box.set_margin_top(20)
		main_box.set_margin_bottom(20)
		main_box.set_margin_start(20)
		main_box.set_margin_end(20)

		# About logo
		logo_box = Gtk.Box(halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
		pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
			"./assets/svgs/imac.svg", 158, 108, preserve_aspect_ratio=True
		)
		logo = Gtk.Image.new_from_pixbuf(pixbuf)
		logo_box.pack_start(logo, False, False, 0)

		# Labels
		name_label = Gtk.Label(label="Env Shell", name="about-name-label")
		date_label = Gtk.Label(label="ESH, 2024", name="about-date-label")

		# Info Section
		info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		info_title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)
		info_box_labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)

		# Titles
		info_title_box.pack_start(Gtk.Label(label="SO", halign=Gtk.Align.END), False, False, 0)
		info_title_box.pack_start(Gtk.Label(label="Chip", halign=Gtk.Align.END), False, False, 0)
		info_title_box.pack_start(Gtk.Label(label="Memory", halign=Gtk.Align.END), False, False, 0)

		# Values
		so_label = Gtk.Label(
			label=subprocess.run(
				"cat /etc/*-release | grep '^PRETTY_NAME=' | cut -d '\"' -f 2",
				shell=True,
				capture_output=True,
				text=True,
			).stdout.strip(),
			halign=Gtk.Align.START
		)
		chip_label = Gtk.Label(
			label=subprocess.run(
				"lscpu | grep 'Model name:' | awk '{print $5}'",
				shell=True,
				capture_output=True,
				text=True,
			).stdout.strip(),
			halign=Gtk.Align.START
		)
		mem_label = Gtk.Label(
			label=subprocess.run(
				"free -h --giga | grep Mem | tr -s ' ' | cut -d ' ' -f 2",
				shell=True,
				capture_output=True,
				text=True,
			).stdout.strip(),
			halign=Gtk.Align.START
		)

		info_box_labels.pack_start(so_label, False, False, 0)
		info_box_labels.pack_start(chip_label, False, False, 0)
		info_box_labels.pack_start(mem_label, False, False, 0)

		info_box.pack_start(info_title_box, False, False, 10)
		info_box.pack_start(info_box_labels, False, False, 10)

		# More Info Button
		button_box = Gtk.Box(halign=Gtk.Align.CENTER)
		more_info_button = Gtk.Button(label="More Info...", name="more-info-button")
		more_info_button.connect("clicked", self.open_more_info)
		button_box.pack_start(more_info_button, False, False, 0)

		# Add everything to the main box
		main_box.pack_start(logo_box, False, False, 0)
		main_box.pack_start(name_label, False, False, 0)
		main_box.pack_start(date_label, False, False, 0)
		main_box.pack_start(info_box, False, False, 0)
		main_box.pack_start(button_box, False, False, 0)

		# Add main box to the window
		self.add(main_box)

	def open_more_info(self, button):
		subprocess.run("xdg-open https://github.com/E3nviction/envshell", shell=True)

	def toggle(self, b):
		if self.get_visible():
			self.hide()
		else:
			self.show_all()

class Dropdown(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor="left top",
			exclusivity="auto",
			name="dropdown-menu",
			visible=False,
			**kwargs,
		)

		self.dropdown = Box(
			children=[
				dropdown_option(self, "About this PC", on_clicked=lambda b: About().toggle(b)),
				dropdown_divider("---------------------"),
				dropdown_option(self, "System Settings...", on_click="code ~/.config/"),
				dropdown_option(self, "Nix Store...", on_click="xdg-open https://search.nixos.org/packages"),
				dropdown_divider("---------------------"),
				dropdown_option(self, "Force Quit App", "󰘶 󰘳 C", "hyprctl activewindow -j | jq -r .pid | xargs kill -9"),
				dropdown_divider("---------------------"),
				dropdown_option(self, "Sleep", "󰘶 󰘳 M", "systemctl suspend"),
				dropdown_option(self, "Restart...", "󰘶 󰘳 M", "systemctl restart"),
				dropdown_option(self, "Shut Down...", "󰘶 󰘳 M", "shutdown now"),
				dropdown_divider("---------------------"),
				dropdown_option(self, "Lock Screen", "󰘳 L", "hyprlock"),
			],
			h_expand=True,
			name="dropdown-options",
			orientation="vertical",
		)

		#self.connect("enter_notify_event", self.on_enter)
		#self.connect('focus-out-event', self.on_leave)

		self.children = CenterBox(
			start_children=[self.dropdown],
		)
	def toggle_dropdown(self, button):
		if self.is_visible():
			self.hide()
		else:
			self.show()

	def on_enter(self, widget, event):
		self.show()

	def on_leave(self, widget, event):
		self.hide()

class ControlCenter(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor="right top",
			margin="2px 10px 0px 0px",
			exclusivity="auto",
			name="control-center-menu",
			visible=False,
			**kwargs,
		)

		volume = subprocess.run("wpctl get-volume @DEFAULT_AUDIO_SINK@ | awk '{print $2}'", shell=True, capture_output=True, text=True)
		volume = volume.stdout.strip()
		volume = round(float(volume) * 100)

		wlan = subprocess.run("iwgetid -r", shell=True, capture_output=True, text=True)
		wlan = wlan.stdout.strip()
		if wlan == "":
			wlan = "No Connection"

		bluetooth = subprocess.run("bluetoothctl show | grep Powered | awk '{print $2}'", shell=True, capture_output=True, text=True)
		bluetooth = bluetooth.stdout.strip()
		if bluetooth == "yes":
			bluetooth = "On"
		else:
			bluetooth = "Off"

		self.widgets = Box(
			children=[
				Box(name="top-widget-menu", orientation="horizontal", h_expand=True,
					children=[
						Box(name="wb-menu", orientation="vertical", spacing=5, children=[
							Button(name="wifi-widget", child=Box(orientation="horizontal", children=[
								Svg("./assets/svgs/wifi.svg", name="wifi-widget-icon"),
								Box(name="wifi-widget-info", orientation="vertical", children=[
									Label("Wi-Fi", name="wifi-widget-title", h_align="start"),
									Label(wlan, name="wifi-widget-label", h_align="start"),
								])
							])),
							Button(name="bluetooth-widget", child=Box(orientation="horizontal", children=[
								Svg("./assets/svgs/bluetooth.svg", name="bluetooth-widget-icon"),
								Box(name="bluetooth-widget-info", orientation="vertical", children=[
									Label("Bluetooth", name="bluetooth-widget-title", h_align="start"),
									Label(bluetooth, name="bluetooth-widget-label", h_align="start"),
								])
							])),
						]),
						Box(name="dnd-menu", h_expand=True, children=[
							Svg("./assets/svgs/dnd.svg", name="dnd-menu-icon"),
							Label("Focus", name="dnd-menu-title")
						])
					]
				),
				Box(name="brightness-widget-menu", orientation="vertical", h_expand=True, children=[
					Label(label="Display", name="brightness-widget-title", h_align="start"),
					Scale(value=100, min_value=0, max_value=100, name="brightness-slider", h_expand=True),
				]),
				Box(name="volume-widget-menu", orientation="vertical", children=[
					Label("Sound", h_align="start"),
					Scale(value=volume, min_value=0, max_value=100, name="volume-slider", h_expand=True),
				])
			],
			h_expand=True,
			name="control-center-widgets",
			orientation="vertical",
		)

		self.children = CenterBox(
			start_children=[self.widgets],
		)

	def toggle_cc(self, button):
		if self.is_visible():
			self.hide()
		else:
			self.show()

class EnvPanel(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor="left top right",
			exclusivity="auto",
			name="env-panel",
			size=(1920, 24),
			**kwargs,
		)

		self.date_time = DateTime(
			formatters="%a %b %d %H:%M",
			name="date-time",
		)
		self.dropdown = Dropdown()
		self.control_center = ControlCenter()
		self.control_center_image = Svg("./assets/svgs/control-center.svg", name="control-center-image")
		self.control_center_indicators = Box(name="control-center-indicators", orientation="vertical", children=[
			Box(name="control-center-indicator-row", orientation="horizontal", children=[
				Label("·", name="control-center-indicator", h_align="start"),
				Label("·", name="control-center-indicator", h_align="start"),
			]),
			Box(name="control-center-indicator-row", orientation="horizontal", children=[
				Label("·", name="control-center-indicator", h_align="start"),
				Label("·", name="control-center-indicator", h_align="start"),
			])
		])
		self.control_center_button = Button(image=self.control_center_image, name="control-center-button", on_clicked=self.control_center.toggle_cc)
		self.envsh_button = Button(label="", name="envsh-button", on_clicked=self.dropdown.toggle_dropdown)
		self.power_button_image = Svg("./assets/svgs/battery.svg", name="control-center-image")
		self.power_button = Button(image=self.power_button_image, name="power-button")
		self.curr_window = Button(label="Fetching...", name="current_window")

		self.app_name_service = AppNameService()
		self.app_name_service.connect(
			"name-changed",
			lambda _, name: self.update_ui_thread_safe(name),
		)

		self.children = CenterBox(
			start_children=[self.envsh_button, self.curr_window],
			end_children=[self.power_button, self.control_center_button, self.date_time],
		)
		self.start_window_update_thread()

	def update_ui_thread_safe(self, new_name):
		"""Update UI safely in the main thread."""
		GLib.idle_add(lambda: self.curr_window.set_property("label", new_name))

	def start_window_update_thread(self):
		"""Start a background thread to update the active window."""
		def fetch_active_window():
			while True:
				try:
					result = instance.get_active_window()
					if result:
						window_title = result.wm_class
						if window_title == "":
							window_title = result.title
						if window_title in app_names:
							window_title = app_names[window_title]
						self.app_name_service.name = window_title
					else:
						self.app_name_service.name = "Hyprland"
				except Exception as e:
					self.app_name_service.name = "Hyprland"
				time.sleep(0.1) # == 100ms

		threading.Thread(target=fetch_active_window, daemon=True).start()