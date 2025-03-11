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
from fabric.widgets.centerbox import CenterBox
from fabric.utils.helpers import exec_shell_command_async
from fabric.hyprland.widgets import get_hyprland_connection
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib
import json


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
			self.hotspot = EnvDockHotspot(self)
			envshell_service.dock_hidden = True

		self.icon_resolver = IconResolver()

		self.connection = get_hyprland_connection()

		if self.connection.ready:
			self.refresh_apps()
		else:
			self.connection.connect("event::ready", lambda *_: self.refresh_apps())

		for event in (
			"activewindow",
			"openwindow",
			"closewindow",
			"changefloatingmode",
			"changeworkspace",
			# add workspace events
		):
			self.connection.connect(f"event::{event}", lambda *_: self.refresh_apps())

		if self.get_orientation() == "horizontal":
			self.set_property("height-request", round(c.get_rule("Dock.size") * 64))
		else:
			self.set_property("width-request", round(c.get_rule("Dock.size") * 64))
		self.set_property("margin", (0,0,0,0) if c.get_rule("Dock.mode") == "full" else (5,5,5,5))
		self.set_property("anchor", self.get_pos())

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

		self.connect("size-allocate", self.update_size)
		envshell_service.dock_width = self.get_allocation().width
		envshell_service.dock_height = self.get_allocation().height


		self.children = self.dock_box

		self.connect("enter-notify-event", self.do_check_hide)
		self.connect("leave-notify-event", self.do_check_hide)

		if c.get_rule("Dock.autohide"):
			envshell_service.connect(
				"dock-hidden-changed",
				self.do_check_hide,
			)

	def show_dock(self, *_):
		self.steal_input()
		envshell_service.dock_hidden = False

	def do_check_hover(self, *_):
		x, y = self.get_pointer()
		allocation = self.get_allocation()
		if y == 0:
			envshell_service.dock_hidden = False
			return
		if not (0 < x < allocation.width and 0 < y < allocation.height + 5):
			envshell_service.dock_hidden = True
		else:
			envshell_service.dock_hidden = False

	def do_check_hide(self, *_):
		if envshell_service.dock_hidden:
			self.set_property("margin", (0,0,-(self.get_allocation().height),0))
			if self.get_orientation() == "vertical":
				if c.get_rule("Dock.position") == "left":
					self.set_property("margin", (0,0,0,-(self.get_allocation().width)))
				elif c.get_rule("Dock.position") == "right":
					self.set_property("margin", (0,-(self.get_allocation().width),0,0))
		else:
			self.set_property("margin", (0,0,0,0) if c.get_rule("Dock.mode") == "full" else (5,5,5,5))


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
		os.system("hyprctl dispatch focuswindow address:" + b.get_name())

	def launch_app(self, b):
		exec_shell_command_async(f"hyprctl dispatch exec {c.dock_pinned[b.get_name()]}")

	def dock_apps_changed(self, _apps):
		"""Update UI safely in the main thread."""
		def dock_apps_changed_update():
			self.dock_box.children = []
			apps = _apps
			total_apps = len(apps)
			# We have to eval the string to get the list, because Signals don't work with lists. Atleast I haven't found a way
			if apps[0] == "[" and apps[-1] == "]": apps: list = eval(apps)
			pinned_apps = {}
			apps_new = []
			for i, app in enumerate(apps):
				if app[0] not in c.dock_pinned:
					apps_new.append(app)
					continue
				pinned_apps[app[0]] = [app[0], app[1], app[2], app[3], app[4], True]
			apps = apps_new
			for p in c.dock_pinned:
				if p not in pinned_apps:
					pinned_apps[p] = [p, None, None, None, None, False]
			pinned_apps = dict(sorted(pinned_apps.items(), key=lambda item: list(c.dock_pinned.keys()).index(item[0])))
			for app_ in pinned_apps:
				app, pid, title, address, active, running = pinned_apps[app_]
				svg     = Svg(svg_file=app_list["NotFOUND"], size=(round(c.get_rule("Dock.size") * 32)), name="dock-app-icon")
				app_i = app
				app_i = c.get_translation(wmclass=app)
				icon_svg = self.icon_resolver.get_icon_pixbuf(app_i, round(c.get_rule("Dock.size") * 32))
				svg     = Image(pixbuf=icon_svg, size=(round(c.get_rule("Dock.size") * 32)), name="dock-app-icon")
				app = self.format_window(wmclass=app, title=title)
				if running:
					self.button = Button(
						child=svg,
						name=f"{address}",
						style_classes=("active" if active else "", "dock-app-button", "running"),
						h_align="center",
						v_align="center",
						on_clicked=self.focus_app,
						tooltip_text=f"{app}",
					)
					app_button = Box(
						orientation="vertical",
						children=[
							self.button,
							Svg(svg_file="./assets/svgs/indicator.svg", size=(6), name="dock-app-indicator", h_align="center", v_align="center"),
						],
					)
				else:
					app_button = Box(
						orientation="vertical",
						children=[
							Button(
								child=svg,
								name=f"{pinned_apps[app_][0]}",
								style_classes=("active" if active else "", "dock-app-button"),
								h_align="center",
								v_align="center",
								on_clicked=self.launch_app,
								tooltip_text=f"{app}",
							),
						],
					)
				self.dock_box.add(app_button)
			if not len(apps) == 0:
				self.dock_box.add(Box(orientation="horizontal", name="dock-seperator", h_expand=True, v_expand=True))
			for app, pid, title, address, active in apps:
				app = c.get_translation(wmclass=app)
				icon_svg = self.icon_resolver.get_icon_pixbuf(app, round(c.get_rule("Dock.size") * 32))
				svg = Image(pixbuf=icon_svg, size=(round(c.get_rule("Dock.size") * 32)), name="dock-app-icon")
				app = self.format_window(wmclass=app, title=title)
				app_button = Box(
					orientation="vertical",
					children=[
						Button(
							child=svg,
							name=f"{address}",
							style_classes=("active" if active else "", "dock-app-button", address),
							h_align="center",
							v_align="center",
							on_clicked=self.focus_app,
							tooltip_text=f"{app} ({f"{title[:c.get_rule('Dock.title.limit')]}..."})",
						),
						Svg(svg_file="./assets/svgs/indicator.svg", size=(6), name="dock-app-indicator", h_align="center", v_align="center"),
					],
				)
				self.dock_box.add(app_button)
			self.dock_box.show_all()

		GLib.idle_add(dock_apps_changed_update)

	def format_window(self, title, wmclass):
		name = app_name_class.format_app_name(title, wmclass, False)
		return name

	def refresh_apps(self):
		windows = self.fetch_clients()
		open_apps = []
		for window in windows:
			pid = window["pid"]
			title = window["title"]
			address = window["address"]
			app_name = window["initialClass"]
			if app_name == "":
				app_name = window["title"]
			if not (c.is_window_ignored(wmclass=str(app_name).lower()) or c.is_window_ignored(wmclass=str(app_name)) or c.is_workspace_ignored(id_=window["workspace"]["id"])):
				try:
					iaddress = self.get_focused_window()["address"]
				except:
					iaddress = None
				open_apps.append([app_name, pid, str(title), address, iaddress == address])
		# sort alphabetically
		open_apps = sorted(open_apps, key=lambda x: x[0])
		envshell_service.dock_apps = str(open_apps)

	def fetch_clients(self):
		"""Retrieve open windows from Hyprland."""
		try:
			return json.loads(self.connection.send_command("j/clients").reply.decode())
		except json.JSONDecodeError:
			return []

	def get_focused_window(self):
		"""Get the currently focused window's address."""
		try:
			return json.loads(
				self.connection.send_command("j/activewindow").reply.decode()
			).get("address", "")
		except json.JSONDecodeError:
			return ""

class EnvDockHotspot(Window):
	def __init__(self, dock, **kwargs):
		super().__init__(
			name="envdock-hotspot",
			layer="top",
			anchor=self.get_pos(),
			style="background-color: alpha(#f00, 0.1);" if c.get_rule("Dock.debug") else "",
			size=(768, c.get_rule("Dock.size") * 64),
			margin=(0, 0, 0, 0),
			visible=True,
			style_classes="envdock-hotspot",
			**kwargs
		)

		self.dock = dock
		if self.get_orientation() == "horizontal":
			self.dock_height = c.get_rule("Dock.size") * 64
			self.dock_width = 768
		else:
			self.dock_height = 768
			self.dock_width = c.get_rule("Dock.size") * 64

		envshell_service.connect(
			"dock-width-changed",
			self.set_width,
		)

		envshell_service.connect(
			"dock-height-changed",
			self.set_height,
		)

		envshell_service.connect(
			"dock-hidden-changed",
			self.do_check_hide,
		)

		self.connect("enter-notify-event", self.show_dock)

	def show_dock(self, *_):
		envshell_service.dock_hidden = not envshell_service.dock_hidden

	def do_check_hide(self, *_):
		if envshell_service.dock_hidden:
			pos = c.get_rule("Dock.position")
			full = c.get_rule("Dock.mode") == "full"
			if not full:
				if pos == "left":
					self.set_property("anchor", "left center")
				elif pos == "right":
					self.set_property("anchor", "right center")
				else:
					self.set_property("anchor", "bottom center")
			self.set_property("width-request", self.dock_width)
			self.set_property("height-request", self.dock_height)
			if self.get_orientation() == "vertical":
				if c.get_rule("Dock.position") == "left":
					self.set_property("margin", (0,0,0,-(self.dock_width - 1)))
				elif c.get_rule("Dock.position") == "right":
					self.set_property("margin", (0,-(self.dock_width - 1),0,0))
			else:
				self.set_property("margin", (0,0,-(self.dock_height),0))
		else:
			self.set_property("anchor", self.get_pos())
			if self.get_orientation() == "horizontal":
				self.set_property("width-request", int(c.get_rule("Display.resolution").split("x")[0]))
			else:
				self.set_property("height-request", int(c.get_rule("Display.resolution").split("x")[1]))
			if not c.get_rule("Dock.exclusive"):
				if self.get_orientation() == "vertical":
					if c.get_rule("Dock.position") == "left":
						self.set_property("margin", (-(c.get_rule("Panel.height")),0,0,(self.dock_width + 10)))
					elif c.get_rule("Dock.position") == "right":
						self.set_property("margin", (-(c.get_rule("Panel.height")),(self.dock_width + 10),0,0))
				else:
					self.set_property("margin", (0,0,self.dock_height + 5,0) if c.get_rule("Dock.mode") == "full" else (0,0,self.dock_height + 10,0))
			else:
				self.set_property("margin", (-(c.get_rule("Panel.height")),0,0,0))

	def set_height(self, _, height):
		self.dock_height = height
		self.set_property("height-request", height)

	def set_width(self, _, width):
		self.dock_width = width
		self.set_property("width-request", width)

	def get_pos(self):
		pos = c.get_rule("Dock.position")
		full = c.get_rule("Dock.mode") == "full"
		if full:
			if pos == "bottom": pos = "bottom left right center"
			elif pos == "left": pos = "left top bottom center"
			elif pos == "right": pos = "right top bottom center"
		else:
			if pos == "bottom": pos = "bottom center"
			elif pos == "left": pos = "left top bottom center"
			elif pos == "right": pos = "right top bottom center"
		return pos

	def get_orientation(self):
		pos = c.get_rule("Dock.position")
		orientation = "horizontal"
		if pos == "bottom": orientation = "horizontal"
		elif pos == "left": orientation = "vertical"
		elif pos == "right": orientation = "vertical"
		return orientation
