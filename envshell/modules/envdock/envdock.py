import threading
import time
import sys
import os

from fabric import Application
from fabric.widgets.button import Button
from fabric.widgets.svg import Svg
from fabric.widgets.image import Image
from fabric.widgets.label import Label
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib


from config.c import c, app_list

from utils.functions import app_name_class
from utils.icon_resolver import IconResolver

global instance
global envshell_service
from utils.roam import create_instance, envshell_service
instance = create_instance()

class EnvDock(Window):
	"""Hackable dock for envshell."""
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor=self.get_pos(),
			exclusivity="auto",
			name="env-dock",
			h_expand=True,
			v_expand=True,
			margin=(0,0,0,0) if c.get_rule("Dock.style.mode") == "full" else (5,5,5,5),
			**kwargs,
		)

		self.icon_resolver = IconResolver()

		if self.get_orientation() == "horizontal":
			self.set_property("height-request", c.get_rule("Dock.style.height"))
		else:
			self.set_property("width-request", c.get_rule("Dock.style.height"))
		self.set_property("margin", (0,0,0,0) if c.get_rule("Dock.style.mode") == "full" else (5,5,5,5))
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
			border-radius: {0 if c.get_rule('Dock.style.mode') == 'full' else 19.2}px;
			""",
			h_expand=True,
			v_expand=True,
			h_align="fill" if c.get_rule("Dock.style.mode") == "full" else "center",
			v_align="fill" if c.get_rule("Dock.style.mode") == "full" else "center",
		)

		self.children = self.dock_box

		self.start_update_thread()

	def get_pos(self):
		pos = c.get_rule("Dock.style.position")
		full = c.get_rule("Dock.style.mode") == "full"
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
		pos = c.get_rule("Dock.style.position")
		orientation = "horizontal"
		if pos == "bottom": orientation = "horizontal"
		elif pos == "left": orientation = "vertical"
		elif pos == "right": orientation = "vertical"
		return orientation


	def dock_apps_changed(self, _apps):
		"""Update UI safely in the main thread."""
		def focus(b): os.system("hyprctl dispatch focuswindow address:" + b.get_name())
		def launch(b): os.system("hyprctl dispatch exec " + c.dock_pinned[b.get_name()])
		def dock_apps_changed_update():
			self.dock_box.children = []
			apps = _apps
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
				svg     = Svg(svg_file=app_list["NotFOUND"], size=(c.get_rule("Dock.style.icon-size", 32)), name="dock-app-icon")
				svg_mag = Svg(svg_file=app_list["NotFOUND"], size=(64), name="dock-app-icon")
				app_i = app
				app_i = c.get_translation(wmclass=app)
				icon_svg = self.icon_resolver.get_icon_pixbuf(app_i, c.get_rule("Dock.style.icon-size", 32))
				svg     = Image(pixbuf=icon_svg, size=(c.get_rule("Dock.style.icon-size", 32)), name="dock-app-icon")
				svg_mag = Image(pixbuf=icon_svg, size=(64), name="dock-app-icon")
				app = self.format_window(wmclass=app, title=title)
				if running:
					self.button = Button(
						child=svg,
						name=f"{address}",
						style_classes=("active" if active else "", "dock-app-button", "running"),
						h_align="center",
						v_align="center",
						on_clicked=focus,
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
								on_clicked=launch,
								tooltip_text=f"{app}",
							),
						],
					)
				self.dock_box.add(app_button)
			if not len(apps) == 0:
				self.dock_box.add(Box(orientation="horizontal", name="dock-seperator", h_expand=True, v_expand=True))
			for app, pid, title, address, active in apps:
				app = c.get_translation(wmclass=app)
				icon_svg = self.icon_resolver.get_icon_pixbuf(app, c.get_rule("Dock.style.icon-size", 32))
				svg = Image(pixbuf=icon_svg, size=(c.get_rule("Dock.style.icon-size", 32)), name="dock-app-icon")
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
							on_clicked=focus,
							tooltip_text=f"{app} ({f"{title[:25]}..."})",
						),
						Svg(svg_file="./assets/svgs/indicator.svg", size=(6), name="dock-app-indicator", h_align="center", v_align="center"),
					],
				)
				self.dock_box.add(app_button)
			self.dock_box.show_all()

		GLib.idle_add(dock_apps_changed_update)

		envshell_service.dock_width = self.get_allocation().width
		envshell_service.dock_height = self.get_allocation().height

	def format_window(self, title, wmclass):
		name = app_name_class.format_app_name(title, wmclass, False)
		return name

	def start_update_thread(self):
		"""Start a background thread to monitor open applications."""
		def run():
			while True:
				windows = instance.get_windows()
				open_apps = []
				for window in windows:
					pid = window.pid
					title = window.title
					address = window.address
					app_name = window.wm_class
					if app_name == "":
						app_name = window.title
					if not (c.is_window_ignored(wmclass=str(app_name).lower()) or c.is_window_ignored(wmclass=str(app_name)) or c.is_workspace_ignored(id_=window.workspace_id)):
						try:
							iaddress = instance.get_active_window().address
						except:
							iaddress = None
						open_apps.append([app_name, pid, str(title), address, iaddress == address])
				# sort alphabetically
				open_apps = sorted(open_apps, key=lambda x: x[0])
				envshell_service.dock_apps = str(open_apps)
				time.sleep(0.25)

		threading.Thread(target=run, daemon=True).start()

class EnvDockHotspot(Window):
	def __init__(self, dock, **kwargs):
		super().__init__(
			name="envdock-hotspot",
			layer="bottom",
			anchor="left top",
			size=(64, 64),
			margin=(0, 0, 0, 0),
			style="background-color: #f00;",
			visible=True,
			style_classes="envdock-hotspot",
			**kwargs
		)

		self.dock = dock

		x = self.dock.get_allocation().x
		y = self.dock.get_allocation().y
		self.set_property("margin", (0 if y is None else y, 0, 0, 0 if x is None else x))

		envshell_service.connect(
			"dock-width-changed",
			lambda _, width: self.set_property("width-request", width),
		)

		envshell_service.connect(
			"dock-height-changed",
			lambda _, height: self.set_property("height-request", height),
		)