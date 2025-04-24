from concurrent.futures import thread
import json
import operator
from collections.abc import Iterator
from re import sub
import socket
import subprocess
import threading
import time
import os
import asyncio
from types import EllipsisType
from typing import Generator
from urllib.parse import quote
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import DesktopApp, exec_shell_command, get_desktop_applications, idle_add, remove_handler

from fabric.widgets.widget import Widget
from styledwidgets.styled import styler, style_dict
from styledwidgets.agents import colors, borderradius, transitions, margins, paddings
from styledwidgets.types import rem, px
from styledwidgets.color import alpha

from fabric.utils import exec_shell_command_async
from loguru import logger
from config.c import c, load_config_file, config_location
from widgets.mousecapture import MouseCapture
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

		load_config_file(verbose_extensions=True)

		self._arranger_handler: int = 0
		self._arrange_vp_handler: int = 0
		self._all_apps = get_desktop_applications()

		self.set_size_request(480, 520)

		self.viewport = Box(spacing=2, orientation="v")
		self.search_entry = Entry(placeholder="Search...", h_expand=True,
			style=styler(font_size=rem(1.2)),
			notify_text=lambda entry, *_: idle_add(self.entry_changed, entry.get_text()),
		)
		self.scrolled_window = ScrolledWindow(name="light-widget",
			min_content_size=(480, 520), max_content_size=(480 * 2, 520),
			overlay_scroll=True, h_scrollbar_policy="never", child=self.viewport,
		)

		self.add(Box(spacing=2, orientation="v", style="margin: 2px", children=[
			Box(spacing=2, orientation="h", style=styler(padding=px(10), margin=px(10)), children=[self.search_entry]),
			self.scrolled_window,
		]))

		threading.Thread(
			target=self.socket_loop,
			name="EnvLightSocketThread",
			args=(),
			daemon=True,
		).start()

	def _init_mousecapture(self, mousecapture: MouseCapture):
		self._mousecapture_parent = mousecapture
		self.add_keybinding("Escape", self._mousecapture_parent.toggle_mousecapture)

	def _set_mousecapture(self, visible: bool):
		if c.get_rule("EnvLight.clear-search-on-toggle"): self.search_entry.set_text("")
		self.keyboard_mode = "exclusive" if visible else "none"
		self.set_visible(visible)
		self.pass_through = not visible

	def socket_loop(self):
		while True:
			with open("/tmp/envctl.socket", "r") as sock: data = sock.read()
			try:
				data = json.loads(data)
				if data.get("command", {}).get("value", "") == "command:toggle envLight":
					create_socket_signal("envctl.socket", "command", {"value": ""})
					idle_add(lambda *_: self._mousecapture_parent.toggle_mousecapture()) # type: ignore

			except json.JSONDecodeError: logger.error("Failed to decode JSON data from socket")
			except Exception as e: logger.error(f"An error occurred: {e}")
			time.sleep(0.1)

	def multi_option_slots(self, filtered_apps_list: list, extension: dict):
		if extension.get("type", "command") == "multi-options":
			old_path = os.getcwd()
			os.chdir(os.path.join(config_location, "envshell", "extensions"))
			result: str | bool = exec_shell_command(extension["command"].replace("%s", ""))
			os.chdir(old_path)
			if not result: return
			options: list[dict] = json.loads(result)
			for option in options:
				option["is_option"] = True
				filtered_apps_list.append(option)

	def exec_condition(self, extension: dict, query: str):
		if extension.get("condition", None):
			condition = extension["condition"]
			old_path = os.getcwd()
			os.chdir(os.path.join(config_location, "envshell", "extensions"))
			result = exec_shell_command(condition.replace("%s", query))
			os.chdir(old_path)
			if str(result).strip() == extension.get("condition-is", None):
				return True

	def arrange_viewport(self, query: str = ""):
		remove_handler(self._arranger_handler) if self._arranger_handler else None
		self.viewport.children = []

		extension_groups: dict[str, dict] = c.get_rule("EnvLight.extensions") # type: ignore
		enabled: list[str] = c.get_rule("EnvLight.enabled") # type: ignore

		filtered_apps_list: list = []
		left_apps: list = self._all_apps.copy()

		for i in extension_groups:
			extension_group = extension_groups[i]
			for j in extension_group:
				extension = extension_group[j]
				if f"{i}.{j}" not in enabled: continue # is enabled
				if query.startswith(extension.get("keyword", "")) and extension.get("keyword", None) is not None:
					if extension.get("type", "command") == "multi-options": self.multi_option_slots(filtered_apps_list, extension)
					else: filtered_apps_list.append(extension)
				elif self.exec_condition(extension, query):
						if extension.get("type", "command") == "multi-options":
							self.multi_option_slots(filtered_apps_list, extension)
						else:
							filtered_apps_list.append(extension)

		filtered_apps_list.extend(list(self.find_apps(query, left_apps)))

		if not filtered_apps_list and query == "": filtered_apps_list = left_apps

		self._arranger_handler = idle_add(
			lambda list: self.add_applications(list, query),
			filtered_apps_list,
			pin=True,
		)

	def entry_changed(self, query: str = ""):
		remove_handler(self._arrange_vp_handler) if self._arranger_handler else None
		self._arrange_vp_handler = idle_add(self.arrange_viewport, query)

	def find_apps(self, query: str = "", left_apps: list[DesktopApp] = []) -> list[DesktopApp]:
		if not query: return []
		fields = ["display_name", "name", "generic_name", "description", "executable", "command_line"]
		query_lower = query.casefold()
		filtered_apps = []
		for field in fields:
			remaining_apps = []
			for app in left_apps:
				value = getattr(app, field, "") or ""
				if query_lower in value.casefold(): filtered_apps.append(app)
				else: remaining_apps.append(app)
			left_apps = remaining_apps
		return filtered_apps

	def add_applications(self, apps_list: list[DesktopApp | dict], query: str = ""):
		for app in apps_list:
			if isinstance(app, dict):
				if app.get("is_option", False):
					idle_add(self.viewport.add, self._add_slot(
						label=app["name"],
						description=app["desc"],
						description_color=colors.white.seven,
						tooltip_text=app["tooltip"],
						command=app["on-click"],
					))
				else:
					idle_add(self.viewport.add, self.bake_extension_slot(app, query))
			else:
				idle_add(self.viewport.add, self.bake_application_slot(app))

	def remove_keyword(self, text: str, keyword: str) -> str:
		if text.startswith(keyword + " "): text = text.removeprefix(keyword + " ")
		elif text.startswith(keyword): text = text.removeprefix(keyword)
		return text

	def wrap_text_by_char(self, text: str) -> str:
		return "\n".join(text[i:i+63] for i in range(0, len(text), 63))

	def wrap_text_by_word(self, text: str) -> str:
			lines = [""]
			words = text.split()
			for word in words:
				if len(word) >= 63:
					lines.extend(self.wrap_text_by_char(word)) # fall back to char
					continue
				if len(lines[-1]) + len(word) >= 63: lines.append("")
				lines[-1] += word + " "
			return "\n".join(lines)

	def update_description(self, extension: dict, value: str, old_query: str, query: str, label_description: Label):
		description = extension.get("description", None) or extension["command"]
		description = description.replace("%c", value)
		description = description.replace("%s", old_query).replace("%S", query) # we use %s and %S for the query, because when using url query, the query will be escaped
		if not extension.get("ignore-char-limit", False): description = description[:c.get_rule("EnvLight.advanced.executable-max-length")]

		if extension.get("wrap-mode", "none") == "none": pass
		elif extension.get("wrap-mode", "none") == "char": description = self.wrap_text_by_char(description)
		elif extension.get("wrap-mode", "none") == "word": description = self.wrap_text_by_word(description)

		idle_add(label_description.set_label, description)

	def bake_extension_slot(self, extension: dict, query: str, **kwargs) -> Button:
		extension = extension.copy() # remove the pointer
		# remove keyword
		query = self.remove_keyword(query, extension["keyword"])
		old_query = f"{query}"

		description = extension.get("description", None) or extension["command"]
		description = description.replace("%c", "...") # default description

		label_description = Label(label=description, style=styler(font_family="monospace", font_size=px(12), color=colors.white.seven), v_align="start", h_align="start")

		# make query be url supportive
		if extension.get("type") == "url":
			query = quote(query)
			if not extension["command"].startswith("xdg-open"): extension["command"] = f"xdg-open {extension['command']}"

		if extension.get("description", None):
			result = extension.get("description-command", "echo ...")
			result = exec_shell_command_async(result.replace("%s", query), lambda value: idle_add(self.update_description, extension, value, old_query, query, label_description))

		return self._add_slot(
			image=None,
			label=f"{extension["name"]}" or "Unknown",
			description_label=label_description if c.get_rule("EnvLight.show-executable") else Label(""),
			description_color=colors.white.seven,
			tooltip_text=f"{extension["tooltip"]}",
			command=f"{extension["command"].replace("%s", query)}",
		)

	def bake_application_slot(self, app: DesktopApp, **kwargs) -> Button:
		return self._add_slot(
			image=app.get_icon_pixbuf(),
			label=app.display_name or "Unknown",
			description=(self.remove_artifacts(
				f"{app.command_line}" if c.get_rule("EnvLight.advanced.full-executable") else app.executable or "Unknown"
			)
			.strip()[:c.get_rule("EnvLight.advanced.executable-max-length")]) if c.get_rule("EnvLight.show-executable") else "",
			description_color=colors.gray.three,
			tooltip_text=f"{app.description}",
			command=f"{app.command_line}",
		)


	def _add_slot(self, image: None = None, label: str="", description: str="", description_label: Widget | None = None, description_color: str=colors.gray.three, tooltip_text: str="", command: str="", **kwargs):
		return Button(
			child=Box(orientation="h", spacing=12, children=[
				Image(pixbuf=image, h_align="start", size=32),
				Box(orientation="v", spacing=2, children=[
					Label( label=label,
						style=styler(font_size=px(14)),
						name="light-suggestion-label",
						v_align="start", h_align="start",
					),
					Label(label=description,
						style=styler(font_size=px(12), color=description_color),
						v_align="start", h_align="start",
					) if description_label is None else description_label,
				]),
			]),
			style=styler({
				"default": style_dict(
					padding=rem(.5) + rem(1),
					margin=rem(.2),
					border_radius=px(5),
				),
				":focus": style_dict(background_color=alpha("#2369ff", 0.5)),
				":hover": style_dict(background_color="#2369ff"),
			}),
			name="light-suggestion",
			tooltip_text=tooltip_text,
			on_clicked=lambda *_: (self.launch_app(command), self._mousecapture_parent.toggle_mousecapture()), # type: ignore
			**kwargs,
		)

	def remove_artifacts(self, text: str) -> str:
		for artifact in ["@@", "%U", "@@u", "%u", "%f", "%F"]: text = text.replace(artifact, "").strip()
		return text

	def launch_app(self, app: str | None):
		if app is None: return
		app = self.remove_artifacts(app)
		command = "nohup bash -c '" + app.replace("'", "\\'") + "' >/dev/null 2>&1"
		logger.info("Launching: " + "nohup " + app)
		threading.Thread(target=lambda: subprocess.run(command, shell=True), name="EnvLightLaunchAppThread", args=(), daemon=True).start()
