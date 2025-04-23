import threading
import time
import math
import subprocess
from widgets.popup_window import PopupWindow
import gi # type: ignore

from fabric.utils import invoke_repeater
from fabric.core.service import Service, Signal, Property
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale
from fabric.widgets.scale import ScaleMark
from fabric.widgets.revealer import Revealer
from fabric.widgets.svg import Svg
from widgets.systrayv2 import SystemTray
from fabric.hyprland.widgets import ActiveWindow
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import FormattedString, truncate
from fabric.utils.helpers import exec_shell_command_async, get_relative_path, monitor_file
from gi.repository import GLib, Gtk, GdkPixbuf # type: ignore
from widgets.customimage import CustomImage

from fabric.notifications import Notification

from gi.repository.GLib import idle_add # type: ignore

global envshell_service
from utils.roam import envshell_service, audio_service
from utils.functions import app_name_class, get_socket_signal

from styledwidgets.styled import styler, style_dict, on_hover
from styledwidgets.agents import margins, paddings, transitions, colors, shadows, borderradius, textsize
from styledwidgets.types import px, rem
from styledwidgets.color import alpha, hex

from styles.styles import button_style, button_style_hover

from config.c import c

from .envnoti import NOTIFICATION_IMAGE_SIZE, NOTIFICATION_TIMEOUT, NOTIFICATION_WIDTH

class EnvNotiCenter(Window):
	"""Notification Center for envshell"""
	def __init__(
		self,
		transition_type="crossfade",
		transition_duration: int = 400,
		revealer_name: str | None = None,
		**kwargs
	):
		super().__init__(
			layer="overlay",
			anchor="top bottom right",
			title="envshell",
			exclusivity="none",
			margin=(0,0,0,0),
			name="env-noti-center",
			pass_through=True,
			size=(NOTIFICATION_WIDTH, -1),
			**kwargs,
		)

		self.set_size_request(NOTIFICATION_WIDTH, -1)

		self.main_box = Box(
			orientation="v",
			spacing=4,
			name="notification-center",
			children=[
				Label(
					label="Notifications",
				)
			],
		)

		self.revealer = Revealer(
			child=self.main_box,
			transition_type="slide-right",
			transition_duration=transition_duration,
			name=revealer_name,
		)

		envshell_service.connect("notification-count-changed", self.on_notification_changed)
		envshell_service.connect("clear-all-changed", self.on_notification_changed)

		self.show()
		self.add(self.revealer)

	def _set_mousecapture(self, visible: bool):
		self.pass_through = not visible
		if visible: self.revealer.reveal()
		else: self.revealer.unreveal()

	def on_notification_changed(self, *_):
		self.main_box.children = [
			Label("Notifications")
		]
		for i in (envshell_service._notifications):
			self.main_box.add(
				self.create_notification(i),
			)

	def create_notification(self, notification_data: Notification):
		main = Box(spacing=8, name="notification", orientation="v")
		body = Box(spacing=4, orientation="h")
		if notification_data.get("image-pixmap"):
			body.add(
				CustomImage(
					name="noti-image",
					pixbuf=Notification.deserialize(notification_data).image_pixbuf.scale_simple( # type: ignore
						NOTIFICATION_IMAGE_SIZE,
						NOTIFICATION_IMAGE_SIZE,
						GdkPixbuf.InterpType.BILINEAR,
					)
				)
			)
		body.add(
			Box(
				spacing=4,
				orientation="v",
				children=[
					Box(
						orientation="h",
						children=[
							Label(
								markup=notification_data["summary"],
								style_classes="summary",
							)
						],
						h_expand=True,
						v_expand=True,
					)
					.build(
						lambda box, _: box.pack_end(
							Button(
								image=CustomImage(
									icon_name="close-symbolic",
									icon_size=18,
								),
								v_align="center",
								h_align="end",
							).build(
								lambda button, _: button.connect(
									"clicked",
									lambda *_, notification_data=notification_data: envshell_service.remove_notification(notification_data["id"]),
								)),
							False,
							False,
							0,
						)
					),
					Label(
						label=notification_data["body"],
						line_wrap="word-char",
						v_align="start",
						h_align="start",
						style_classes="body",
					)
				],
				h_expand=True,
				v_expand=True,
			)
		)

		main.add(body)
		if actions := Notification.deserialize(notification_data).actions:
			main.add(
				Box(
					spacing=4,
					orientation="h",
					children=[
						Button(
							h_expand=True,
							v_expand=True,
							label=action.label,
							style=styler({
								"default": button_style,
							}),
							on_clicked=lambda *_, action=action: action.invoke(),
						)
						for action in actions # type: ignore
					],
				)
			)
		return main