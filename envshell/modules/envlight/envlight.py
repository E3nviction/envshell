from concurrent.futures import thread
import json
import operator
from collections.abc import Iterator
from re import sub
import socket
import subprocess
import threading
import time
from urllib.parse import quote
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler

from styledwidgets.styled import styler, style_dict
from styledwidgets.agents import colors, borderradius, transitions, margins, paddings
from styledwidgets.types import rem, px
from styledwidgets.color import alpha

from fabric.utils import exec_shell_command_async
from loguru import logger
from config.c import c
from utils.functions import create_socket_signal

class EnvLight(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor="center",
			title="envshell",
			exclusivity="none",
			keyboard_mode="on-demand",
			name="env-light",
			size=(480, 520),
			visible=False,
			all_visible=False,
			**kwargs,
		)
		self.add_keybinding("Escape", self.toggle)
		self.set_property("width-request", 400)
		self._arranger_handler: int = 0
		self._all_apps = get_desktop_applications()

		self.set_size_request(480, 520)

		self.viewport = Box(spacing=2, orientation="v")
		self.search_entry = Entry(
			placeholder="Light up your way!",
			style=styler({
				"default": style_dict(
					font_size=rem(1.2),
				),
			}),
			h_expand=True,
			notify_text=lambda entry, *_: self.arrange_viewport(entry.get_text()),
		)
		self.scrolled_window = ScrolledWindow(
			name="light-widget",
			min_content_size=(480, 520),
			max_content_size=(480 * 2, 520),
			overlay_scroll=True,
			h_scrollbar_policy="never",
			child=self.viewport,
		)

		self.socket = socket.socket()
		self.socket.bind(("localhost", 3262))

		self.add(
			Box(
				spacing=2,
				orientation="v",
				style="margin: 2px",
				children=[
					Box(
						spacing=2,
						orientation="h",
						style=styler({
							"default": style_dict(
								padding=px(10),
								margin=px(10),
							)
						}),
						children=[
							self.search_entry,
						],
					),
					self.scrolled_window,
				],
			)
		)

		threading.Thread(
			target=self.socket_loop,
			name="EnvLightSocketThread",
			args=(),
			daemon=True,
		).start()

	def socket_loop(self):
		while True:
			with open("/tmp/envctl.socket", "r") as sock:
				data = sock.read()
			try:
				data = json.loads(data)
				if data.get("command", {}).get("value", "") == "command:toggle envLight":
					create_socket_signal("envctl.socket", "command", {"value": ""})
					idle_add(lambda *_: self.toggle(None))
			except json.JSONDecodeError:
				logger.error("Failed to decode JSON data from socket")
			except Exception as e:
				logger.error(f"An error occurred: {e}")
			time.sleep(0.1)
	def toggle(self, b, *_):
		if c.get_rule("EnvLight.clear-search-on-toggle"):
			self.search_entry.set_text("")
		if self.get_visible():
			self.hide()
		else:
			self.show_all()

	def arrange_viewport(self, query: str = ""):
		remove_handler(self._arranger_handler) if self._arranger_handler else None

		self.viewport.children = []

		shortcuts: list[dict] = c.get_rule("EnvLight.shortcuts")

		if not shortcuts:
			return False

		filtered_apps_list: list = []

		for shortcut in shortcuts:
			if query.casefold().startswith(shortcut["keyword"].casefold()):
				filtered_apps_list.append(shortcut)

		filtered_apps_list.extend([
			app for app in self._all_apps
			if query.casefold()
			in (app.display_name or "") + (" " + app.name + " ") + (app.generic_name or "").casefold()
		])
		self._arranger_handler = idle_add(
			lambda list: self.add_applications(list, query),
			filtered_apps_list,
			pin=True,
		)

		return False

	def add_applications(self, apps_list: list[DesktopApp | dict], query: str = ""):
		for app in apps_list:
			if isinstance(app, dict):
				self.viewport.add(self.bake_shortcut_slot(app, query))
			else:
				self.viewport.add(self.bake_application_slot(app))

	def add_next_application(self, apps_iter: Iterator[DesktopApp]):
		if not (app := next(apps_iter, None)):
			return False

		self.viewport.add(self.bake_application_slot(app))
		return True

	def resize_viewport(self):
		self.scrolled_window.set_min_content_width(
			self.viewport.get_allocation().width  # type: ignore
		)
		return False

	def bake_shortcut_slot(self, shortcut: dict, query: str, **kwargs) -> Button:
		shortcut = shortcut.copy()
		if query.startswith(shortcut["keyword"] + " "):
			query = query.removeprefix(shortcut["keyword"] + " ")
		elif query.startswith(shortcut["keyword"]):
			query = query.removeprefix(shortcut["keyword"])
		old_query = f"{query}"
		# make query be url supportive
		if shortcut.get("type") == "url":
			query = quote(query)
			if not shortcut["command"].startswith("xdg-open"):
				shortcut["command"] = f"xdg-open {shortcut['command']}"
		if shortcut.get("description", None):
			result = shortcut.get("description-command", "echo ...")
			result = subprocess.run(result.replace("%s", query), shell=True, capture_output=True).stdout.decode("utf-8").strip()
			shortcut["description"] = shortcut["description"].replace("%c", result)
		return Button(
			child=Box(
				orientation="h",
				spacing=12,
				children=[
					#Image(pixbuf=app.get_icon_pixbuf(), h_align="start", size=32),
					Box(orientation="v", spacing=2, children=[
						Label(
							label=f"{shortcut["name"]}" or "Unknown",
							style=styler({
								"default": style_dict(
									font_size=px(14),
								),
							}),
							name="light-suggestion-label",
							v_align="start",
							h_align="start",
						),
						Label(
							label=(f"{shortcut.get("description", None) or shortcut["command"]}".replace("%s", old_query).replace("%S", query))[:c.get_rule("EnvLight.advanced.executable-max-length")],
							style=styler({
								"default": style_dict(
									font_size=px(12),
									color=colors.gray.three,
								),
							}),
							v_align="start",
							h_align="start",
						),
					] if c.get_rule("EnvLight.show-executable") else [
						Label(label=f"{shortcut["name"]}" or "Unknown", style=styler(font_size=px(14)), v_align="start", h_align="start"),
					]),
				],
			),
			style=styler({
				"default": style_dict(
					padding=rem(.5) + rem(1),
					margin=rem(.2),
					border_radius=px(5),
				),
				":focus": style_dict(
					background_color=alpha("#2369ff", 0.5),
				),
				":hover": style_dict(
					background_color="#2369ff",
				),
			}),
			name="light-suggestion",
			tooltip_text=shortcut["tooltip"],
			on_clicked=lambda *_: (self.launch_app(shortcut["command"].replace("%s", query)), self.toggle(None)),
			**kwargs,
		)

	def bake_application_slot(self, app: DesktopApp, **kwargs) -> Button:
		return Button(
			child=Box(
				orientation="h",
				spacing=12,
				children=[
					Image(pixbuf=app.get_icon_pixbuf(), h_align="start", size=32),
					Box(orientation="v", spacing=2, children=[
						Label(
							label=f"{app.display_name}" or "Unknown",
							style=styler({
								"default": style_dict(
									font_size=px(14),
								),
							}),
							name="light-suggestion-label",
							v_align="start",
							h_align="start",
						),
						Label(
							label=(f"{app.command_line}" if c.get_rule("EnvLight.advanced.full-executable") else app.executable or "Unknown").removesuffix("%U").removesuffix("%u").removesuffix("%f").removesuffix("%F").strip()[:c.get_rule("EnvLight.advanced.executable-max-length")],
							style=styler({
								"default": style_dict(
									font_size=px(12),
									color=colors.gray.three,
								),
							}),
							v_align="start",
							h_align="start",
						),
					] if c.get_rule("EnvLight.show-executable") else [
						Label(label=f"{app.display_name}" or "Unknown", style=styler(font_size=px(14)), v_align="start", h_align="start"),
					]),
				],
			),
			style=styler({
				"default": style_dict(
					padding=rem(.5) + rem(1),
					margin=rem(.2),
					border_radius=px(5),
				),
				":focus": style_dict(
					background_color=alpha("#2369ff", 0.5),
				),
				":hover": style_dict(
					background_color="#2369ff",
				),
			}),
			name="light-suggestion",
			tooltip_text=app.description,
			on_clicked=lambda *_: (self.launch_app(app.command_line), self.toggle(None)),
			**kwargs,
		)
	def launch_app(self, app: str | None):
		if app is None:
			return
		app = app.removesuffix("%U").removesuffix("%u").removesuffix("%f").removesuffix("%F").strip()
		logger.info("Launching: " + "nohup " + app)
		threading.Thread(
			target=lambda: subprocess.run("nohup " + app, shell=True),
			name="EnvLightLaunchAppThread",
			args=(),
			daemon=True,
		).start()