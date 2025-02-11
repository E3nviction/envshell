import subprocess
import threading
import time
import gi

from fabric.core.service import Service, Signal, Property
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale
from fabric.widgets.svg import Svg
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib, Gtk, GdkPixbuf

global instance
global envshell_service
from utils.roam import instance, envshell_service

from .controlcenter import ControlCenter
from .about import About

from config.c import c

def dropdown_option(self, label: str = "", keybind: str = "", on_click="echo \"EnvPanelDropdown Action\"", on_clicked=None):
	def on_click_subthread(button):
		self.toggle_dropdown(button)
		if on_clicked: on_clicked(button)
		else: subprocess.run(on_click, shell=True)
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
def dropdown_divider(comment): return Box(children=[Box(name="dropdown-divider", h_expand=True)], name="dropdown-divider-box", h_align="fill", h_expand=True, v_expand=True,)

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

		self.children = CenterBox(start_children=[self.dropdown])
	def toggle_dropdown(self, button): self.set_visible(not self.is_visible())
	def on_enter(self, widget, event): self.show()
	def on_leave(self, widget, event): self.hide()

class EnvPanel(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor="left top right",
			exclusivity="auto",
			name="env-panel",
			style_classes="",
			size=(1920, 24),
			**kwargs,
		)

		self.date_time = DateTime(formatters="%a %b %d %H:%M", name="date-time")
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
		self.current_active_app_name = Button(label="Fetching...", name="current_window")

		envshell_service.connect("current-active-app-name-changed", self.current_active_app_name_changed)

		self.children = CenterBox(
			start_children=[self.envsh_button, self.current_active_app_name],
			end_children=[self.power_button, self.control_center_button, self.date_time],
		)

		self.start_update_thread()

	def current_active_app_name_changed(self, _, new_name):
		GLib.idle_add(lambda: self.current_active_app_name.set_property("label", new_name))
		if c.is_window_autohide(wmclass=new_name, title=new_name): self.add_style_class("empty")
		else: self.remove_style_class("empty")

	def start_update_thread(self):
		def run():
			try:
				while True:
					try:
						result = instance.get_active_window()
						if not result:
							envshell_service.current_active_app_name = "Hyprland"
							continue
						window_title = result.wm_class
						if window_title == "": window_title = result.title
						window_title = c.get_title(wmclass=result.wm_class, title=result.title)
						envshell_service.current_active_app_name = window_title
					except Exception as e: envshell_service.current_active_app_name = "Hyprland"
					time.sleep(0.1)
			except KeyboardInterrupt: pass

		threading.Thread(target=run, daemon=True).start()
