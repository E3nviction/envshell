from modules.envnotch.envnotch import EnvNotch
from modules.envpanel.envpanel import EnvPanel
from modules.envnoti.envnoti import EnvNoti
from modules.envdock.envdock import EnvDock
from modules.envcorners.envcorners import EnvCorners
from modules.envlight.envlight import EnvLight
from fabric import Application
import loguru

from utils.functions import AppName
from config.c import c

loguru.logger.disable("fabric.hyprland.widgets")
loguru.logger.disable("fabric.widgets.wayland")
loguru.logger.disable("fabric.audio.service")
loguru.logger.disable("fabric.bluetooth.service")

if __name__ == "__main__":
	envnoti = EnvNoti()
	#envcorners = EnvCorners() # FIXME: Fix the issue where they are just not correctly positioned
	envnotch = EnvNotch()
	envdock = None
	envpanel = None
	if c.get_rule("Widgets.panel.enable"):
		envpanel = EnvPanel()
	if c.get_rule("Widgets.dock.enable"):
		envdock = EnvDock()
	apps = [
		envnoti,
		envnotch,
		envdock,
		envpanel,
	]
	apps = list(filter(lambda x: x is not None, apps))
	app = Application(
		"envshell",
		*apps,
	)

	def set_css():
		app.set_stylesheet_from_file(
			"./envshell.css",
		)
	app.set_css = set_css
	app.set_css()

	app.run()