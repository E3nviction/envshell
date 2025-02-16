import threading
import time
import subprocess
import gi

from fabric.core.service import Service, Signal, Property
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale
from fabric.widgets.svg import Svg
from fabric.system_tray import SystemTray
from fabric.hyprland.widgets import ActiveWindow
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import FormattedString, truncate
from fabric.utils.helpers import exec_shell_command_async
from gi.repository import GLib, Gtk, GdkPixbuf

global instance
global envshell_service
from utils.roam import instance, envshell_service
from shared.envdropdown import EnvDropdown, dropdown_divider

from modules.envcontrolcenter.envcontrolcenter import EnvControlCenter
from .about import About

from modules.envlight.envlight import EnvLight

from config.c import c

def dropdown_option(self, label: str = "", keybind: str = "", on_click="echo \"EnvPanelDropdown Action\"", on_clicked=None):
	def on_click_subthread(button):
		envshell_service.current_dropdown = -1
		if on_clicked: on_clicked(button)
		else: exec_shell_command_async(on_click)
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

class Dropdown(EnvDropdown):
	"""EnvMenu for envshell"""
	def __init__(self, **kwargs):
		super().__init__(
			x=0,
			y=0,
			w=150,
			h=258,
			dropdown_children=[
				dropdown_option(self, c.get_shell_rule(rule="panel-env-menu-option-1-label"), on_clicked=lambda b: About().toggle(b)),
				dropdown_divider("---------------------"),
				dropdown_option(self, c.get_shell_rule(rule="panel-env-menu-option-2-label"), on_click=c.get_shell_rule(rule="panel-env-menu-option-2-on-click")),
				dropdown_option(self, c.get_shell_rule(rule="panel-env-menu-option-3-label"), on_click=c.get_shell_rule(rule="panel-env-menu-option-3-on-click")),
				dropdown_divider("---------------------"),
				dropdown_option(self, c.get_shell_rule(rule="panel-env-menu-option-4-label"), c.get_shell_rule(rule="panel-env-menu-option-4-keybind"), c.get_shell_rule(rule="panel-env-menu-option-4-on-click")),
				dropdown_divider("---------------------"),
				dropdown_option(self, c.get_shell_rule(rule="panel-env-menu-option-5-label"), c.get_shell_rule(rule="panel-env-menu-option-5-keybind"), c.get_shell_rule(rule="panel-env-menu-option-5-on-click")),
				dropdown_option(self, c.get_shell_rule(rule="panel-env-menu-option-6-label"), c.get_shell_rule(rule="panel-env-menu-option-6-keybind"), c.get_shell_rule(rule="panel-env-menu-option-6-on-click")),
				dropdown_option(self, c.get_shell_rule(rule="panel-env-menu-option-7-label"), c.get_shell_rule(rule="panel-env-menu-option-7-keybind"), c.get_shell_rule(rule="panel-env-menu-option-7-on-click")),
				dropdown_divider("---------------------"),
				dropdown_option(self, c.get_shell_rule(rule="panel-env-menu-option-8-label"), c.get_shell_rule(rule="panel-env-menu-option-8-keybind"), c.get_shell_rule(rule="panel-env-menu-option-8-on-click")),
			],
			**kwargs,
		)

class EnvPanel(Window):
	"""Top Panel for envshell"""
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor=c.get_shell_rule(rule="panel-position"),
			exclusivity="auto",
			margin=c.get_shell_rule(rule="panel-margin"),
			name="env-panel",
			style_classes="",
			style=f"""
				border-radius: {c.get_shell_rule(rule="panel-rounding")};
			""",
			size=(c.get_shell_rule(rule="panel-width"), c.get_shell_rule(rule="panel-height")),
			**kwargs,
		)

		self.set_property("width-request", c.get_shell_rule(rule="panel-width"))
		self.set_property("height-request", c.get_shell_rule(rule="panel-height"))


		self.envlight = EnvLight()
		self.date_time = DateTime(formatters=c.get_shell_rule(rule="panel-date-format"), name="date-time")
		self.envsh_button_dropdown = Dropdown()

		self.control_center = EnvControlCenter()
		self.control_center_image = Svg("./assets/svgs/control-center.svg", name="control-center-image")
		self.control_center_button = Button(image=self.control_center_image, name="control-center-button", style_classes="button", on_clicked=self.control_center.toggle_cc)

		self.envsh_button = Button(label=c.get_shell_rule(rule="panel-icon"), name="envsh-button", style_classes="button", on_clicked=self.envsh_button_dropdown.toggle_dropdown)
		self.power_button_image = Svg("./assets/svgs/battery.svg", name="control-center-image")
		self.power_button = Button(image=self.power_button_image, name="power-button", style_classes="button")

		self.search_button_image = Svg("./assets/svgs/search.svg", name="search-button-image")
		self.search_button = Button(image=self.search_button_image, name="search-button", style_classes="button")
		self.search_button.connect("clicked", self.envlight.toggle)

		self.wifi_button_image = Svg("./assets/svgs/wifi-clear.svg", name="wifi-button-image")
		self.wifi_button = Button(image=self.wifi_button_image, name="wifi-button", style_classes="button")
		self.global_title_menu_about = dropdown_option(self, f"About {envshell_service.current_active_app_name}")
		self.global_title_dropdown = EnvDropdown(
			45,
			0,
			dropdown_children=[
				self.global_title_menu_about
			]
		)
		self.global_menu_file   = None
		self.global_menu_edit   = None
		self.global_menu_view   = EnvDropdown(0, 0,
			dropdown_children=[
				dropdown_option(self, "Enter Full Screen", on_click="hyprctl dispatch fullscreen"),
			]
		)
		self.global_menu_go     = None
		self.global_menu_window = EnvDropdown(0, 0,
			dropdown_children=[
				dropdown_option(self, "Zoom", on_clicked=lambda b: subprocess.run("bash ~/.config/scripts/zoomer.sh", shell=True)),
				dropdown_option(self, "Move Window to Left", on_click="hyprctl dispatch movewindow l"),
				dropdown_option(self, "Move Window to Right", on_click="hyprctl dispatch movewindow r"),
				dropdown_option(self, "Cycle Through Windows", on_click="hyprctl dispatch cyclenext"),
				dropdown_divider("---------------------"),
				dropdown_option(self, "Float", on_click="hyprctl dispatch togglefloating"),
				dropdown_option(self, "Center", on_click="hyprctl dispatch centerwindow"),
				dropdown_option(self, "Group", on_click="hyprctl dispatch togglegroup"),
				dropdown_option(self, "Pin", on_clicked=lambda b: subprocess.run("bash ~/.config/scripts/winpin.sh", shell=True)),
			]
		)
		self.global_menu_help   = EnvDropdown(0, 0,
			dropdown_children=[
				dropdown_option(self, "EnvShell", on_clicked=lambda b: subprocess.run("xdg-open https://github.com/E3nviction/envshell", shell=True)),
				dropdown_divider("---------------------"),
				dropdown_option(self, "nixOS Help", on_clicked=lambda b: subprocess.run("xdg-open https://wiki.nixos.org/wiki/NixOS_Wiki", shell=True)),
			]
		)
		envshell_service.connect("current-active-app-name-changed", lambda _, value: self.global_title_menu_about.set_property("label", f"About {value}"))
		self.global_title = Button(
			child=ActiveWindow(formatter=FormattedString("{ format_window('None', 'None') if win_title == '' and win_class == '' else format_window(win_title, win_class) }", format_window=self.format_window)),
			name="global-title-button",
			style_classes="button",
			on_clicked=self.global_title_dropdown.toggle_dropdown,
		)

		self.global_menu_button_file   = Button(label="File",   name="global-menu-button-file",   style_classes="button")
		self.global_menu_button_edit   = Button(label="Edit",   name="global-menu-button-edit",   style_classes="button")
		self.global_menu_button_view   = Button(label="View",   name="global-menu-button-view",   style_classes="button", on_clicked=lambda b: self.global_menu_view.toggle_dropdown(b, self.global_menu_button_view))
		self.global_menu_button_go     = Button(label="Go",     name="global-menu-button-go",     style_classes="button")
		self.global_menu_button_window = Button(label="Window", name="global-menu-button-window", style_classes="button", on_clicked=lambda b: self.global_menu_window.toggle_dropdown(b, self.global_menu_button_window))
		self.global_menu_button_help   = Button(label="Help",   name="global-menu-button-help",   style_classes="button", on_clicked=lambda b: self.global_menu_help.toggle_dropdown(b, self.global_menu_button_help))

		self.systray = SystemTray()

		self.systray_box = Box(
			name="system-tray-box",
		)

		self.children = CenterBox(
			start_children=[self.envsh_button, self.global_title, self.global_menu_button_file, self.global_menu_button_edit, self.global_menu_button_view, self.global_menu_button_go, self.global_menu_button_window, self.global_menu_button_help],
			end_children=[self.systray_box, self.power_button, self.wifi_button, self.search_button, self.control_center_button, self.date_time],
		)

	def format_window(self, title, wmclass):
		name = wmclass
		if name == "": name = title
		name = c.get_title(wmclass=wmclass, title=title)
		envshell_service.current_active_app_name = name
		if c.is_window_autohide(wmclass=name, title=name):
			self.add_style_class("empty")
		else:
			self.remove_style_class("empty")
		return name
