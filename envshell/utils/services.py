from fabric.core.service import Service, Signal, Property

class EnvShellService(Service):
	@Signal
	def current_active_app_name_changed(self, new_current_active_app_name: str) -> None:
		...
	@Signal
	def bluetooth_changed(self, new_bluetooth: str) -> None:
		...
	@Signal
	def volume_changed(self, new_volume: str) -> None:
		...
	@Signal
	def wlan_changed(self, new_wlan: str) -> None:
		...
	@Signal
	def dock_apps_changed(self, new_dock_apps: str) -> None:
		...

	@Property(str, flags="read-write")
	def current_active_app_name(self) -> str:
		return self._current_active_app_name
	@Property(str, flags="read-write")
	def bluetooth(self) -> str:
		return self._bluetooth
	@Property(str, flags="read-write")
	def wlan(self) -> str:
		return self._wlan
	@Property(str, flags="read-write")
	def volume(self) -> str:
		return self._volume
	@Property(str, flags="read-write")
	def dock_apps(self) -> str:
		return self._dock_apps

	@current_active_app_name.setter
	def current_active_app_name(self, value: str):
		if value != self._current_active_app_name:
			self._current_active_app_name = value
			self.current_active_app_name_changed(value)
	@volume.setter
	def volume(self, value: str):
		if value != self._volume:
			self._name = value
			self.volume_changed(value)
	@wlan.setter
	def wlan(self, value: str):
		if value != self._wlan:
			self._wlan = value
			self.wlan_changed(value)
	@bluetooth.setter
	def bluetooth(self, value: str):
		if value != self._bluetooth:
			self._bluetooth = value
			self.bluetooth_changed(value)
	@dock_apps.setter
	def dock_apps(self, value: str):
		if value != self._dock_apps:
			self._dock_apps = value
			self.dock_apps_changed(value)

	def __init__(self, volume: str = "", wlan: str = "", bluetooth: str = "", current_active_app_name: str = "", dock_apps: str = ""):
		super().__init__()
		self._volume = volume or ""
		self._wlan = wlan or ""
		self._bluetooth = bluetooth or ""
		self._current_active_app_name = current_active_app_name or ""
		self._dock_apps = dock_apps or ""

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