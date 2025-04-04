from typing import cast

from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.image import Image
from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.notifications import NotificationAction, Notifications, Notification
from fabric.utils import invoke_repeater, get_relative_path

from utils.roam import envshell_service

from widgets.customimage import CustomImage

from gi.repository import GdkPixbuf # type: ignore

NOTIFICATION_WIDTH = 360
NOTIFICATION_IMAGE_SIZE = 64
NOTIFICATION_TIMEOUT = 10 * 1000

from styledwidgets.styled import styler, style_dict, on_hover
from styledwidgets.agents import colors, borderradius, transitions, margins, paddings
from styledwidgets.types import rem, px

from styles.styles import button_style, button_style_hover


class NotificationWidget(Box):
	def __init__(self, notification: Notification, **kwargs):
		super().__init__(
			size=(NOTIFICATION_WIDTH, -1),
			name="notification",
			spacing=8,
			orientation="v",
			**kwargs,
		)

		self._notification = notification

		body_container = Box(spacing=4, orientation="h")

		if image_pixbuf := self._notification.image_pixbuf:
			body_container.add(
				CustomImage(
					name="noti-image",
					pixbuf=image_pixbuf.scale_simple( # type: ignore
						NOTIFICATION_IMAGE_SIZE,
						NOTIFICATION_IMAGE_SIZE,
						GdkPixbuf.InterpType.BILINEAR,
					)
				)
			)

		body_container.add(
			Box(
				spacing=4,
				orientation="v",
				children=[
					Box(
						orientation="h",
						children=[
							Label(
								markup=self._notification.summary, # type: ignore
								ellipsization="middle",
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
                                on_clicked=self.close_noti,
                            ),
                            False,
                            False,
                            0,
                        )
                    ),
					Label(
						label=self._notification.body, # type: ignore
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

		self.add(body_container)

		if actions := self._notification.actions:
			actions = cast(list[NotificationAction], actions)  # type: ignore
			self.add(
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
								on_hover: button_style_hover,
							}),
							on_clicked=lambda *_, action=action: action.invoke(),
						)
						for action in actions # type: ignore
					],
				)
			)

		self._notification.connect(
			"closed",
			self.destroy_noti,
		)

		invoke_repeater(
			NOTIFICATION_TIMEOUT,
			lambda: self._notification.close("expired"),
			initial_call=False,
		)

	def close_noti(self, *_):
		envshell_service.remove_notification(self._notification["id"])
		self._notification.close()
		self.destroy()

	def destroy_noti(self, *_):
		parent.remove(self) if (parent := self.get_parent()) else None,  # type: ignore
		self.destroy()

class EnvNoti(Window):
	def __init__(self, **kwargs):
		super().__init__(
			margin="8px 8px 8px 8px",
			name="notification-window",
			layer="overlay",
			anchor="top right",
			child=Box(
				size=2,
				spacing=4,
				orientation="v",
			).build(
				lambda viewport, _: Notifications(
					on_notification_added=self.on_notification_added
				)
			),
			**kwargs,
		)

	def on_notification_added(self, notifs_service, nid):
		envshell_service.cache_notification(notifs_service.get_notification_from_id(nid))
		self.get_child().add(NotificationWidget(cast(Notification, notifs_service.get_notification_from_id(nid))))