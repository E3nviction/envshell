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
from fabric.hyprland.widgets import ActiveWindow
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import FormattedString, truncate
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
	"""EnvMenu for envshell"""
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
			h_expand=True,
			name="dropdown-options",
			orientation="vertical",
		)

		self.children = CenterBox(start_children=[self.dropdown])
	def toggle_dropdown(self, button): self.set_visible(not self.is_visible())
	def on_enter(self, widget, event): self.show()
	def on_leave(self, widget, event): self.hide()

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
			size=(1920, 24),
			**kwargs,
		)

		self.date_time = DateTime(formatters=c.get_shell_rule(rule="panel-date-format"), name="date-time")
		self.dropdown = Dropdown()
		self.control_center = ControlCenter()
		self.control_center_image = Svg("./assets/svgs/control-center.svg", name="control-center-image")
		self.control_center_button = Button(image=self.control_center_image, name="control-center-button", style_classes="button", on_clicked=self.control_center.toggle_cc)
		self.envsh_button = Button(label=c.get_shell_rule(rule="panel-icon"), name="envsh-button", style_classes="button", on_clicked=self.dropdown.toggle_dropdown)
		self.power_button_image = Svg("./assets/svgs/battery.svg", name="control-center-image")
		self.power_button = Button(image=self.power_button_image, name="power-button", style_classes="button")
		self.search_button_image = Svg("./assets/svgs/search.svg", name="search-button-image")
		self.search_button = Button(image=self.search_button_image, name="search-button", style_classes="button")
		self.wifi_button_image = Svg("./assets/svgs/wifi-clear.svg", name="wifi-button-image")
		self.wifi_button = Button(image=self.wifi_button_image, name="wifi-button", style_classes="button")
		self.global_title = ActiveWindow(formatter=FormattedString("{ format_window('None', 'None') if win_title == '' and win_class == '' else format_window(win_title, win_class) }", format_window=self.format_window))

		self.children = CenterBox(
			start_children=[self.envsh_button, self.global_title],
			end_children=[self.power_button, self.wifi_button, self.search_button, self.control_center_button, self.date_time],
		)

	def format_window(self, title, wmclass):
		name = wmclass
		if name == "": name = title
		name = c.get_title(wmclass=wmclass, title=title)
		if c.is_window_autohide(wmclass=name, title=name):
			self.add_style_class("empty")
		else:
			self.remove_style_class("empty")
		return name