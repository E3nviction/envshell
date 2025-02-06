from fabric.core.service import Service, Signal, Property
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale
from fabric.widgets.svg import Svg
from fabric.widgets.wayland import WaylandWindow as Window

class AppService(Service):
	@Signal
	def apps_changed(self, new_apps: str) -> None:
		...

	@Property(str, flags="read-write")
	def apps(self) -> str:
		return self._apps

	@apps.setter
	def apps(self, value: str):
		if value != self._apps:
			self._apps = value
			self.apps_changed(value)

	def __init__(self, apps: str = []):
		super().__init__()
		self._apps = apps or []
