from fabric.core.service import Service, Signal, Property
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.scale import Scale
from fabric.widgets.svg import Svg
from fabric.widgets.wayland import WaylandWindow as Window

class AppNameService(Service):
	@Signal
	def name_changed(self, new_name: str) -> None:
		...

	@Property(str, flags="read-write")
	def name(self) -> str: # type: ignore
		return self._name

	@name.setter # type: ignore
	def name(self, value: str):
		if value != self._name:
			self._name = value
			self.name_changed(value)

	def __init__(self, name: str = ""):
		super().__init__()
		self._name = name or ""

class ControlCenterService(Service):
	@Signal
	def volume_changed(self, new_volume: str) -> None:
		...

	@Property(str, flags="read-write")
	def volume(self) -> str: # type: ignore
		return self._volume

	@volume.setter # type: ignore
	def volume(self, value: str):
		if value != self._volume:
			self._name = value
			self.volume_changed(value)

	@Signal
	def wlan_changed(self, new_wlan: str) -> None:
		...

	@Property(str, flags="read-write")
	def wlan(self) -> str: # type: ignore
		return self._wlan

	@wlan.setter # type: ignore
	def wlan(self, value: str):
		if value != self._wlan:
			self._wlan = value
			self.wlan_changed(value)

	@Signal
	def bluetooth_changed(self, new_bluetooth: str) -> None:
		...

	@Property(str, flags="read-write")
	def bluetooth(self) -> str: # type: ignore
		return self._bluetooth

	@bluetooth.setter # type: ignore
	def bluetooth(self, value: str):
		if value != self._bluetooth:
			self._bluetooth = value
			self.bluetooth_changed(value)

	def __init__(self, volume: str = "", wlan: str = "", bluetooth: str = ""):
		super().__init__()
		self._volume = volume or ""
		self._wlan = wlan or ""
		self._bluetooth = bluetooth or ""