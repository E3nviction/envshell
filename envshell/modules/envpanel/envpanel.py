import threading
import time
import math
import subprocess
import gi

from fabric.core.service import Service, Signal, Property
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale
from fabric.widgets.scale import ScaleMark
from fabric.widgets.svg import Svg
from widgets.systrayv2 import SystemTray
from fabric.hyprland.widgets import ActiveWindow
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import FormattedString, truncate
from fabric.utils.helpers import exec_shell_command_async, get_relative_path
from gi.repository import GLib, Gtk, GdkPixbuf

from gi.repository.GLib import idle_add

global envshell_service
from utils.roam import envshell_service, audio_service
from utils.functions import app_name_class
from widgets.envdropdown import EnvDropdown, dropdown_divider
from widgets.osd_widget import OsdWindow

from modules.envcontrolcenter.envcontrolcenter import EnvControlCenter
from .about import About

from styledwidgets.styled import styler, style_dict
from styledwidgets.agents import margins, paddings, transitions, colors, shadows, borderradius, textsize
from styledwidgets.types import px, rem
from styledwidgets.color import alpha, hex


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
	def __init__(self, parent, **kwargs):
		super().__init__(
			dropdown_id="os-menu",
			parent=parent,
			dropdown_children=[
				dropdown_option(self, "About this PC", on_clicked=lambda b: About().toggle(b)),
				dropdown_divider("---------------------"),
				dropdown_option(self, "System Settings...", on_click=c.get_shell_rule(rule="panel-env-menu-option-settings-on-click")),
				dropdown_option(self, c.get_shell_rule(rule="panel-env-menu-option-store-label"), on_click=c.get_shell_rule(rule="panel-env-menu-option-store-on-click")),
				dropdown_divider("---------------------"),
				dropdown_option(self, "Force Quit", "", "hyprctl kill"),
				dropdown_divider("---------------------"),
				dropdown_option(self, "Sleep", "", "systemctl suspend"),
				dropdown_option(self, "Restart...", "", "systemctl restart"),
				dropdown_option(self, "Shut Down...", "", "shutdown now"),
				dropdown_divider("---------------------"),
				dropdown_option(self, "Lock Screen", "󰘳 L", "hyprlock"),
			],
			**kwargs,
		)

class ItemWidget:
	def __init__(self, parent, icon, icon_size=24, id_=None, dropdown=None):
		self.icon = icon
		self.id = id_
		self.parent = parent
		options = []
		for i in dropdown:
			if not (i.get("divider") and len(i) == 1):
				options.append(dropdown_option(self, i["label"], i.get("keybind", ""), on_click="hyprctl dispatch exec " + i.get("on-clicked", "")))
			if i.get("divider") is not None:
				options.append(dropdown_divider(""))
		self.menu = EnvDropdown(
			dropdown_id=self.id,
			parent=self.parent,
			dropdown_children=options,
		)
		self.button = Button(
			image=Svg(icon, size=icon_size),
			style_classes="button",
			on_clicked=lambda b: self.menu.toggle_dropdown(b, self.button),
		)
		self.menu.set_pointing_to(self.button)

	def build(self):
		return self.button

class EnvPanel(Window):
	"""Top Panel for envshell"""
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor=self.get_pos(),
			exclusivity="auto",
			margin=(0,0,0,0),
			name="env-panel",
			style_classes="",
			style=f"""
				border-radius: {10 if c.get_rule("Panel.mode") == "floating" else 0}px;
			""",
			size=(int(c.get_rule("Display.resolution").split("x")[0]), int(c.get_rule("Panel.height"))),
			**kwargs,
		)

		if c.get_rule("Panel.mode") == "floating":
			self.set_property("margin", (5, 5, 5, 5))
		elif c.get_rule("Panel.mode") == "normal":
			self.set_property("margin", (0, 0, 0, 0))

		self.set_property("height-request", c.get_rule("Panel.height"))


		self.envlight = EnvLight()
		self.date_time = DateTime(formatters=c.get_rule("Panel.date-format"), name="date-time")
		self.envsh_button_dropdown = Dropdown(parent=self)

		self.control_center = EnvControlCenter()
		self.control_center_image = Svg(get_relative_path("../../assets/svgs/control-center.svg"), name="control-center-image")
		self.control_center_button = Button(image=self.control_center_image, name="control-center-button", style_classes="button", on_clicked=self.control_center.toggle_cc)

		self.envsh_button = Button(label=c.get_rule("Panel.icon"), name="envsh-button", style_classes="button", on_clicked=lambda b: self.envsh_button_dropdown.toggle_dropdown(b, self.envsh_button))
		self.envsh_button_dropdown.set_pointing_to(self.envsh_button)
		self.power_button_image = Svg(get_relative_path("../../assets/svgs/battery.svg"), name="control-center-image")
		self.power_button = Button(image=self.power_button_image, name="power-button", style_classes="button")

		self.search_button_image = Svg(get_relative_path("../../assets/svgs/search.svg"), name="search-button-image")
		self.search_button = Button(image=self.search_button_image, name="search-button", style_classes="button")
		self.search_button.connect("clicked", self.envlight.toggle)

		wlan = envshell_service.sc("wlan-changed", self.wlan_changed)
		self.wifi_button_image = Svg(get_relative_path("../../assets/svgs/wifi-clear.svg"), name="wifi-button-image")
		self.wifi_button = Button(image=self.wifi_button_image, name="wifi-button", style_classes="button")

		bluetooth = envshell_service.sc("bluetooth-changed", self.bluetooth_changed)
		self.bluetooth_button_image = Svg(get_relative_path("../../assets/svgs/bluetooth-clear.svg"), size=24, name="bluetooth-button-image")

		self.global_title_menu_about = dropdown_option(self, f"About {envshell_service.current_active_app_name}")
		self.global_menu_title = EnvDropdown(
			dropdown_id="global-menu-title",
			parent=self,
			dropdown_children=[
				self.global_title_menu_about
			]
		)

		self.notch_spot = Box(
			name="notch-spot",
			size=(400, c.get_rule("Panel.height")),
			h_expand=True,
			v_expand=True
		)

		self.osd_window_scale = Scale(
			orientation="horizontal",
			name="osd-window-scale",
			h_align="center",
			v_align="center",
			h_expand=True,
			v_expand=True,
			min_value=0,
			max_value=100,
			style=styler({
				"#osd-window-scale": style_dict(
					margin_left="20px",
				)
			}),
			increments=(1, 1),
			marks=[ScaleMark(x, position="bottom", markup=str(x) if x % 20 == 0 else "") for x in range(10, 96, 10)],
			size=(230, 16),
		)

		self.osd_window_muted = audio_service.speaker.muted if audio_service.speaker else False

		self.osd_window_image = Svg(get_relative_path("../../assets/svgs/audio-volume.svg"), size=(64, 250), name="osd-image", h_align="center", v_align="center", h_expand=True, v_expand=True)

		self.osd_window = OsdWindow(
			_children=[
				self.osd_window_image,
				self.osd_window_scale
			],
			margin=(0, 0, 120, 0),
            anchor="center bottom",
            visible=False,
            all_visible=False,
			name="osd-window",
			h_expand=True,
			v_expand=True,
			h_align="center",
			v_align="center",
		)

		def update_osd_window(aservice):
			def set_image(self, num):
				self.osd_window_image.set_from_file(get_relative_path(f"../../assets/svgs/volume/audio-volume-{num}.svg"))

			def set_osd_mute(self, muted):
				self.osd_window_muted = muted

			if not aservice.speaker: return

			audio_level = 0 if aservice.speaker.muted else min(math.ceil(int(aservice.speaker.volume) / 33), 3)
			GLib.idle_add(lambda: self.osd_window_scale.set_value(int(aservice.speaker.volume)))
			set_image(self, audio_level)
			self.osd_window.show()
			if round(aservice.speaker.volume) == round(self.osd_window_scale.get_value()) and not self.osd_window_muted and not aservice.speaker.muted:
				set_osd_mute(self, aservice.speaker.muted)
				self.osd_window.force_hide()
			else:
				GLib.idle_add(lambda: self.osd_window_scale.set_value(int(aservice.speaker.volume)))
				set_osd_mute(self, aservice.speaker.muted)
				set_image(self, audio_level)
				self.osd_window.show()
			set_osd_mute(self, aservice.speaker.muted)

		audio_service.connect("changed", update_osd_window)

		self.osd_window.set_property("width-request", 250)
		self.osd_window.set_property("height-request", 250)


		self.global_menu_file   = None
		self.global_menu_edit   = None
		self.global_menu_view   = EnvDropdown(
			dropdown_id="global-menu-view",
			parent=self,
			dropdown_children=[
				dropdown_option(self, "Enter Full Screen", on_click="hyprctl dispatch fullscreen"),
			]
		)
		self.global_menu_go     = None
		self.global_menu_window = EnvDropdown(
			dropdown_id="global-menu-window",
			parent=self,
			dropdown_children=[
				dropdown_option(self, "Zoom", on_clicked=lambda b: subprocess.run("bash ~/.config/scripts/zoomer.sh", shell=True)),
				dropdown_option(self, "Move Window to Left", on_click="hyprctl dispatch movewindow l"),
				dropdown_option(self, "Move Window to Right", on_click="hyprctl dispatch movewindow r"),
				dropdown_option(self, "Cycle Through Windows", on_click="hyprctl dispatch cyclenext"),
				dropdown_divider("---------------------"),
				dropdown_option(self, "Float", on_click="hyprctl dispatch togglefloating"),
				dropdown_option(self, "Quit", on_click="hyprctl dispatch killactive"),
				dropdown_option(self, "Pseudo", on_click="hyprctl dispatch pseudo"),
				dropdown_option(self, "Toggle Split", on_click="hyprctl dispatch togglesplit"),
				dropdown_option(self, "Center", on_click="hyprctl dispatch centerwindow"),
				dropdown_option(self, "Group", on_click="hyprctl dispatch togglegroup"),
				dropdown_option(self, "Pin", on_clicked=lambda b: subprocess.run("bash ~/.config/scripts/winpin.sh", shell=True)),
			]
		)

		self.global_menu_help   = EnvDropdown(
			dropdown_id="global-menu-help",
			parent=self,
			dropdown_children=[
				dropdown_option(self, "envShell", on_clicked=lambda b: subprocess.run("xdg-open https://github.com/E3nviction/envshell", shell=True)),
				dropdown_divider("---------------------"),
				dropdown_option(self, "nixOS Help", on_clicked=lambda b: subprocess.run("xdg-open https://wiki.nixos.org/wiki/NixOS_Wiki", shell=True)),
			]
		)
		self.bluetooth_menu = EnvDropdown(
			dropdown_id="bluetooth-menu",
			parent=self,
			dropdown_children=[
				dropdown_option(self, "Toggle Bluetooth", on_clicked=lambda b: exec_shell_command_async(f"bluetoothctl power {'off' if envshell_service.bluetooth == 'On' else 'on'}")),
			]
		)

		envshell_service.connect("current-active-app-name-changed", lambda _, value: self.global_title_menu_about.set_property("label", f"About {value}"))
		self.global_menu_button_title = Button(
			child=ActiveWindow(formatter=FormattedString("{ format_window('None', 'None') if win_title == '' and win_class == '' else format_window(win_title, win_class) }", format_window=self.format_window)),
			name="global-title-button",
			style_classes="button",
			on_clicked=lambda b: self.global_menu_title.toggle_dropdown(b, self.global_menu_button_title),
		)
		self.global_menu_title.set_pointing_to(self.global_menu_button_title)

		self.global_menu_button_file   = Button(label="File",   name="global-menu-button-file",   style_classes="button")
		self.global_menu_button_edit   = Button(label="Edit",   name="global-menu-button-edit",   style_classes="button")
		self.global_menu_button_view   = Button(label="View",   name="global-menu-button-view",   style_classes="button", on_clicked=lambda b: self.global_menu_view.toggle_dropdown(b, self.global_menu_button_view))
		self.global_menu_view.set_pointing_to(self.global_menu_button_view)
		self.global_menu_button_go     = Button(label="Go",     name="global-menu-button-go",     style_classes="button")
		self.global_menu_button_window = Button(label="Window", name="global-menu-button-window", style_classes="button", on_clicked=lambda b: self.global_menu_window.toggle_dropdown(b, self.global_menu_button_window))
		self.global_menu_window.set_pointing_to(self.global_menu_button_window)
		self.global_menu_button_help   = Button(label="Help",   name="global-menu-button-help",   style_classes="button", on_clicked=lambda b: self.global_menu_help.toggle_dropdown(b, self.global_menu_button_help))
		self.global_menu_help.set_pointing_to(self.global_menu_button_help)
		self.bluetooth_button = Button(
			image=self.bluetooth_button_image,
			name="bluetooth-button",
			style_classes="button",
			on_clicked=lambda b: self.bluetooth_menu.toggle_dropdown(b, self.bluetooth_button)
		)
		self.bluetooth_menu.set_pointing_to(self.bluetooth_button)

		self.systray = SystemTray(
			name="system-tray",
			icon_size=16,
			spacing=4,
		)

		self.systray_button = Button(
			label="",
			name="systray-button",
			style_classes="button",
			on_clicked=self.toggle_systray,
		)

		envshell_service.connect("current-dropdown-changed", self.changed_dropdown)
		envshell_service.connect("dropdowns-hide-changed", self.hide_dropdowns)

		left_widgets = []

		if c.get_rule("Panel.Widgets.info-menu.enable"): left_widgets.append(self.envsh_button)
		if c.get_rule("Panel.Widgets.global-title.enable"): left_widgets.append(self.global_menu_button_title)
		if c.get_rule("Panel.Widgets.global-menu.enable"):
			left_widgets.extend([
				self.global_menu_button_file,
				self.global_menu_button_edit,
				self.global_menu_button_view,
				self.global_menu_button_go,
				self.global_menu_button_window,
				self.global_menu_button_help,
			])

		right_widgets = []

		if c.get_rule("Panel.Widgets.system-tray.enable"): right_widgets.append(self.systray)
		if c.get_rule("Panel.Widgets.system-tray.expandable"): right_widgets.append(self.systray_button)
		if c.get_rule("Panel.Widgets.battery.enable"): right_widgets.append(self.power_button)
		if c.get_rule("Panel.Widgets.wifi.enable"): right_widgets.append(self.wifi_button)
		if c.get_rule("Panel.Widgets.bluetooth.enable"): right_widgets.append(self.bluetooth_button)
		if c.get_rule("Panel.Widgets.search.enable"): right_widgets.append(self.search_button)
		if c.get_rule("Panel.Widgets.control-center.enable"): right_widgets.append(self.control_center_button)
		if c.get_rule("Panel.Widgets.date.enable"): right_widgets.append(self.date_time)
		if c.get_rule("Mods") is not None:
			mods = c.get_rule("Mods")

			for mod in mods:
				right_widgets.insert(0, ItemWidget(self, mods[mod]["icon"], mods[mod].get("icon-size", 24), mod, mods[mod]["options"]).build())

		self.children = CenterBox(
			h_expand=True,
			h_align="fill",
			start_children=left_widgets if c.get_rule("Panel.Widgets.left.enable") else [],
			center_children=[self.notch_spot],
			end_children=right_widgets if c.get_rule("Panel.Widgets.right.enable") else [],
		)

	def wlan_changed(self, _, wlan):
		self.wifi_button_image.set_from_file(get_relative_path("../../assets/svgs/wifi-clear.svg" if wlan != "No Connection" else "../../assets/svgs/wifi-off-clear.svg"))
	def bluetooth_changed(self, _, bluetooth):
		self.bluetooth_button_image.set_from_file(get_relative_path("../../assets/svgs/bluetooth-clear.svg" if bluetooth != "Off" else "../../assets/svgs/bluetooth-off-clear.svg"))

	def hide_dropdowns(self, _, value):
		self.envsh_button.remove_style_class("active")
		self.global_menu_button_edit.remove_style_class("active")
		self.global_menu_button_file.remove_style_class("active")
		self.global_menu_button_go.remove_style_class("active")
		self.global_menu_button_help.remove_style_class("active")
		self.global_menu_button_title.remove_style_class("active")
		self.global_menu_button_view.remove_style_class("active")
		self.global_menu_button_window.remove_style_class("active")

	def changed_dropdown(self, _, dropdown_id):
		self.hide_dropdowns(_, True)
		if dropdown_id == "os-menu":
			self.envsh_button.add_style_class("active")
		if dropdown_id == "global-menu-edit":
			self.global_menu_button_edit.add_style_class("active")
		if dropdown_id == "global-menu-file":
			self.global_menu_button_file.add_style_class("active")
		if dropdown_id == "global-menu-go":
			self.global_menu_button_go.add_style_class("active")
		if dropdown_id == "global-menu-help":
			self.global_menu_button_help.add_style_class("active")
		if dropdown_id == "global-menu-title":
			self.global_menu_button_title.add_style_class("active")
		if dropdown_id == "global-menu-view":
			self.global_menu_button_view.add_style_class("active")
		if dropdown_id == "global-menu-window":
			self.global_menu_button_window.add_style_class("active")

	def toggle_systray(self, b):
		if "hidden" in self.systray.style_classes:
			idle_add(lambda: self.systray_button.set_property("label", ""))
			self.systray.remove_style_class("hidden")
			self.systray.show()
		else:
			idle_add(lambda: self.systray_button.set_property("label", ""))
			self.systray.add_style_class("hidden")
			self.systray.hide()

	def get_pos(self):
		full = c.get_rule("Panel.full")
		return "top left right center" if full else "top center"

	def format_window(self, title, wmclass):
		name = app_name_class.format_app_name(title, wmclass, True)
		if c.is_window_autohide(wmclass=name, title=name):
			self.add_style_class("empty")
		else:
			self.remove_style_class("empty")
		return name