from typing import cast

from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.image import Image
from fabric.widgets.button import Button
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.notifications import Notifications, Notification
from fabric.utils import invoke_repeater, get_relative_path

from utils.roam import envshell_service

from widgets.customimage import CustomImage

from gi.repository import GdkPixbuf

NOTIFICATION_WIDTH = 360
NOTIFICATION_IMAGE_SIZE = 64
NOTIFICATION_TIMEOUT = 10 * 1000


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

		envshell_service.cache_notification(self._notification)

		body_container = Box(spacing=4, orientation="h")

		if image_pixbuf := self._notification.image_pixbuf:
			body_container.add(
				CustomImage(
					name="noti-image",
					pixbuf=image_pixbuf.scale_simple(
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
					# a box for holding both the "summary" label and the "close" button
					Box(
						orientation="h",
						children=[
							Label(
								markup=self._notification.summary,
								ellipsization="middle",
								style_classes="summary",
							)
						],
						h_expand=True,
						v_expand=True,
					)
					# add the "close" button
                    .build(
                        lambda box, _: box.pack_end(
                            Button(
                                image=CustomImage(
                                    icon_name="close-symbolic",
                                    icon_size=18,
                                ),
                                v_align="center",
                                h_align="end",
                                on_clicked=lambda *_: self._notification.close(),
                            ),
                            False,
                            False,
                            0,
                        )
                    ),
					Label(
						label=self._notification.body,
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

		# destroy this widget once the notification is closed
		self._notification.connect(
			"closed",
			self.destroy_noti,
		)

		# automatically close the notification after the timeout period
		invoke_repeater(
			NOTIFICATION_TIMEOUT,
			lambda: self._notification.close("expired"),
			initial_call=False,
		)

	def destroy_noti(self, *_):
		envshell_service.remove_notification(self._notification["id"])
		parent.remove(self) if (parent := self.get_parent()) else None,  # type: ignore
		self.destroy(),

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
					on_notification_added=lambda notifs_service, nid: viewport.add(
						NotificationWidget(
							cast(
								Notification,
								notifs_service.get_notification_from_id(nid),
							)
						)
					)
				)
			),
			**kwargs,
		)