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
from widgets.customimage import CustomImage

from gi.repository.GLib import idle_add

global envshell_service
from utils.roam import envshell_service, audio_service
from utils.functions import app_name_class

from styledwidgets.styled import styler, style_dict
from styledwidgets.agents import margins, paddings, transitions, colors, shadows, borderradius, textsize
from styledwidgets.types import px, rem
from styledwidgets.color import alpha, hex

from config.c import c

from .envnoti import NOTIFICATION_IMAGE_SIZE, NOTIFICATION_TIMEOUT, NOTIFICATION_WIDTH

class EnvNotiCenter(Window):
	"""Notification Center for envshell"""
	def __init__(self, **kwargs):
		super().__init__(
			layer="overlay",
			anchor="bottom right",
			exclusivity="auto",
			margin=(0,0,0,0),
			name="env-panel",
			size=(250, -1),
			**kwargs,
		)

		self.main_box = Box(
			orientation="v",
			spacing=4,
			name="notification-center",
			children=[
				Label(
					label="Notifications",
				)
			],
			**kwargs,
		)

		self.children = [self.main_box]

		envshell_service.connect(
			"notification-count-changed",
			self.on_notification_changed,
		)

		envshell_service.connect(
			"clear-all-changed",
			self.on_notification_changed,
		)

	def on_notification_changed(self, *_):
		self.main_box.children = []
		for i in (envshell_service._notifications):
			notification = i["summary"]
			print(i)
			self.main_box.add(
				self.create_notification(i),
			)

	def create_notification(self, notification_data):
		main = Box(spacing=8, orientation="v")
		body = Box(spacing=4, orientation="h")
		if image_pixbuf := notification_data.get("image_pixbuf"):
			body.add(
				CustomImage(
					name="noti-image",
					pixbuf=image_pixbuf.scale_simple(
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
                            ),
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
		if actions := notification_data["actions"]:
			self.add(
				Box(
					spacing=4,
					orientation="h",
					children=[
						Button(
							h_expand=True,
							v_expand=True,
							label=action.label,
							on_clicked=lambda *_, action=action: action.invoke(),
						)
						for action in actions
					],
				)
			)
		return main