import threading
import time
import sys
import os

from datetime import datetime

from fabric import Application, Fabricator
from fabric.widgets.button import Button
from fabric.widgets.svg import Svg
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.centerbox import CenterBox
from fabric.utils.helpers import exec_shell_command_async, get_relative_path
from fabric.hyprland.widgets import get_hyprland_connection
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib # type: ignore
import json

from loguru import logger

from gi.repository.GLib import idle_add


from config.c import c, app_list

from utils.functions import app_name_class
from utils.icon_resolver import IconResolver

global envshell_service
from utils.roam import envshell_service

class EnvDock(Window):
	"""Hackable dock for envshell."""
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor=self.get_pos(),
			exclusivity="auto" if c.get_rule("Dock.exclusive") else "none",
			name="env-dock",
			h_expand=True,
			v_expand=True,
			size=(round(c.get_rule("Dock.size") * 64), round(c.get_rule("Dock.size") * 64)),
			margin=(0,0,0,0) if c.get_rule("Dock.mode") == "full" else (5,5,5,5),
			**kwargs,
		)

		if c.get_rule("Dock.autohide"):
			self.is_hidden = True

		self.is_hidden = False
		self._hide()
		self.is_hovered = False
		self.last_hovered = datetime.now()

		self.icon_resolver = IconResolver()

		if self.get_orientation() == "horizontal": idle_add(lambda: self.set_property("height-request", round(c.get_rule("Dock.size") * 64)))
		else: idle_add(lambda: self.set_property("width-request", round(c.get_rule("Dock.size") * 64)))
		idle_add(lambda: self.set_property("margin", (0,0,0,0) if c.get_rule("Dock.mode") == "full" else (5,5,5,5)))
		idle_add(lambda: self.set_property("anchor", self.get_pos()))

		envshell_service.connect(
			"dock-apps-changed",
			lambda _, apps: self.dock_apps_changed(apps),
		)

		self.dock_box = Box(
			orientation=self.get_orientation(),
			name="dock-box",
			children=[],
			style=f"""
			border-radius: {0 if c.get_rule('Dock.mode') == 'full' else 19.2}px;
			""",
			h_expand=True,
			v_expand=True,
			h_align="fill" if c.get_rule("Dock.mode") == "full" else "center",
			v_align="fill" if c.get_rule("Dock.mode") == "full" else "center",
		)

		self.dock_event_box = EventBox()
		self.dock_event_box.add(self.dock_box)
		self.dock_event_box.connect("enter-notify-event", self.update_hover)
		self.dock_event_box.connect("leave-notify-event", self.update_hover)

		self.connect("size-allocate", self.update_size)
		self.update_size(None)

		self.hover_activator = EventBox()
		self.hover_activator.set_size_request(-1, 1)
		self.hover_activator.connect("enter-notify-event", self.update_hover)
		self.hover_activator.connect("leave-notify-event", self.update_hover)

		self.main_box = Box(orientation="v", children=[self.dock_event_box, self.hover_activator])
		self.add(self.main_box)

		self.connection = get_hyprland_connection()

		if self.connection.ready:
			self.refresh_apps()
			GLib.timeout_add(500, self._hide)
		else:
			self.connection.connect("event::ready", lambda *_: self.refresh_apps())
			self.connection.connect("event::ready", lambda *_: self._hide())

		for event in (
			"activewindow",
			"openwindow",
			"closewindow",
			"changefloatingmode",
			"changeworkspace",
		):
			self.connection.connect(f"event::{event}", lambda *_: self.refresh_apps())
		self.connection.connect("event::workspace", self._hide)

		self.hoverer = Fabricator(
			interval=50,
			default_value=False,
			poll_from=self.is_not_hovered,
			on_changed=self.hide_dock,
		)

	def is_not_hovered(self, *_):
		dock_lazy_time_seconds = (int(c.get_rule("Dock.lazy-time")) / 1000)
		delta_seconds = (datetime.now() - self.last_hovered).total_seconds()

		is_timeout = delta_seconds > dock_lazy_time_seconds
		return  is_timeout and not self.dock_event_box.is_hovered()
	def show_dock(self, *_):
		self.steal_input()
		self.is_hidden = False
		self._hide()
	def hide_dock(self, f, v):
		is_workspace_empty = self.fetch_clients_current_workspace() if c.get_rule("Dock.show-on-workspace") else True
		if v and is_workspace_empty:
			self.return_input()
			self.is_hidden = True
			self._hide()
	def update_hover(self, *_):
		self.last_hovered = datetime.now()
		self.is_hidden = False
		self._hide()
	def _hide(self, *_):
		if not c.get_rule("Dock.autohide"): return
		if self.is_hidden:
			idle_add(lambda: self.set_property("margin", (0,0,-(self.get_allocation().height - 1),0)))
			if self.get_orientation() == "vertical":
				if c.get_rule("Dock.position") == "left":
					idle_add(lambda: self.set_property("margin", (0,0,0,-(self.get_allocation().width - 1))))
				elif c.get_rule("Dock.position") == "right":
					idle_add(lambda: self.set_property("margin", (0,-(self.get_allocation().width - 1),0,0)))
		else: idle_add(lambda: self.set_property("margin", (0,0,0,0) if c.get_rule("Dock.mode") == "full" else (5,5,5,5)))
	def update_size(self, *_):
		envshell_service.dock_width = self.get_allocation().width
		envshell_service.dock_height = self.get_allocation().height
	def get_pos(self):
		pos = c.get_rule("Dock.position")
		full = c.get_rule("Dock.mode") == "full"
		if full:
			if pos == "bottom": pos = "bottom left right center"
			elif pos == "left": pos = "left top bottom center"
			elif pos == "right": pos = "right top bottom center"
		else:
			if pos == "bottom": pos = "bottom center"
			elif pos == "left": pos = "left center"
			elif pos == "right": pos = "right center"
		return pos
	def get_orientation(self):
		pos = c.get_rule("Dock.position")
		orientation = "horizontal"
		if pos == "bottom": orientation = "horizontal"
		elif pos == "left": orientation = "vertical"
		elif pos == "right": orientation = "vertical"
		return orientation
	def focus_app(self, b):
		exec_shell_command_async("hyprctl dispatch focuswindow address:" + b.get_name())
	def launch_app(self, b: Button):
		logger.info("Launching: " + b.get_name())
		exec_shell_command_async(f"hyprctl dispatch exec {c.dock_pinned[b.get_name()]}")
	def dock_apps_changed(self, apps):
		"""Update UI safely in the main thread."""
		def create_button(icon, name, active, running, on_click, tooltip):
			button = Button(
				child=icon,
				name=name,
				style_classes=("active" if active else "", "dock-app-button", "running" if running else ""),
				h_align="center",
				v_align="center",
				on_clicked=on_click,
				tooltip_text=tooltip,
			)
			app_button = None
			if running:
				app_button = Box(orientation="vertical", children=[
					button,
					Svg(svg_file=get_relative_path("../../assets/svgs/indicator.svg"), size=(6), name="dock-app-indicator", h_align="center", v_align="center"),
				])
			else:
				app_button = Box(orientation="vertical", children=[button])
			return app_button
		def dock_apps_changed_update(apps):
			self.dock_box.children = []
			pinned_apps = {}
			temporary_apps = []
			# We have to eval the string to get the list, because Signals don't work with lists. Atleast I haven't found a way
			is_apps_list = apps[0] == "[" and apps[-1] == "]"
			if is_apps_list:
				apps: list = eval(apps)

			# Here we sort out the pinned apps, that are running, and move them to running_pinned_apps
			running_pinned_apps = [app for app in apps if app[0] in c.dock_pinned]
			apps = [app for app in apps if app[0] not in c.dock_pinned]

			# enrichen pinned apps with apps
			for p in c.dock_pinned:
				names_of_running_pinned_apps = [app[0] for app in running_pinned_apps]
				current_app = [app for app in running_pinned_apps if app[0] == p]
				if p not in names_of_running_pinned_apps:
					pinned_apps[p] = [p, None, None, None, None, False]
				else:
					pinned_apps[p] = [p, current_app[0][1], current_app[0][2], current_app[0][3], current_app[0][4], True]

			# Then we sort by config order
			pinned_apps = dict(sorted(pinned_apps.items(), key=lambda item: list(c.dock_pinned.keys()).index(item[0])))

			for app_ in pinned_apps:
				app, pid, title, address, active, running = pinned_apps[app_]
				svg = Image(
					pixbuf=self.icon_resolver.get_icon_pixbuf(c.get_translation(wmclass=app), round(c.get_rule("Dock.size") * 32)),
					size=(round(c.get_rule("Dock.size") * 32)),
					name="dock-app-icon"
				)
				app_button = create_button(
					svg,
					address if address else app,
					active,
					running,
					self.focus_app if running else self.launch_app,
					self.format_window(wmclass=app, title=title)
				)
				self.dock_box.add(app_button)

			if len(apps) != 0:
				self.dock_box.add(Box(orientation="horizontal", name="dock-seperator", h_expand=True, v_expand=True))

			for app, pid, title, address, active in apps:
				app = c.get_translation(wmclass=app)
				svg = Image(
					pixbuf=self.icon_resolver.get_icon_pixbuf(app, round(c.get_rule("Dock.size") * 32)),
					size=(round(c.get_rule("Dock.size") * 32)),
					name="dock-app-icon"
				)
				app = self.format_window(wmclass=app, title=title)
				app_button = create_button(
					svg,
					address,
					active,
					True,
					self.focus_app,
					f"{app} ({f"{title[:c.get_rule('Dock.title.limit')]}..."})"
				)
				self.dock_box.add(app_button)
			self.dock_box.show_all()

		GLib.idle_add(dock_apps_changed_update, apps)
	def format_window(self, title, wmclass):
		return app_name_class.format_app_name(title, wmclass, False)
	def refresh_apps(self):
		windows = self.fetch_clients()
		is_on_empty_workspace = self.fetch_clients_current_workspace() == []
		if is_on_empty_workspace:
			self.is_hidden = False
			self._hide()
		open_apps = []
		for window in windows:
			pid = window["pid"]
			title = window["title"]
			address = window["address"]
			app_name = window["initialClass"] if window["initialClass"] != "" else window["title"]
			if not (c.is_window_ignored(wmclass=str(app_name).lower()) or c.is_window_ignored(wmclass=str(app_name)) or c.is_workspace_ignored(id_=window["workspace"]["id"])):
				focused_address = self.get_focused_window()
				open_apps.append([app_name, pid, str(title), address, focused_address == address])
		# sort alphabetically
		open_apps = sorted(open_apps, key=lambda x: x[0])
		envshell_service.dock_apps = str(open_apps)
	def fetch_clients(self):
		"""Retrieve open windows from Hyprland."""
		try: return json.loads(self.connection.send_command("j/clients").reply.decode())
		except json.JSONDecodeError: return []
	def fetch_clients_current_workspace(self):
		"""Retrieve open windows from Hyprland."""
		try:
			clients   = json.loads(self.connection.send_command("j/clients").reply.decode())
			workspace = json.loads(self.connection.send_command("j/activeworkspace").reply.decode())
			return [client for client in clients if client["workspace"]["id"] == workspace["id"]]
		except json.JSONDecodeError: return []
	def get_focused_window(self):
		"""Get the currently focused window's address."""
		try: return json.loads(self.connection.send_command("j/activewindow").reply.decode()).get("address", "")
		except json.JSONDecodeError:return ""
