from modules.envnotch.envnotch import EnvNotch
from modules.envpanel.envpanel import EnvPanel
from modules.envnoti.envnoti import EnvNoti
from modules.envdock.envdock import EnvDock
from modules.envdock.envdock_old import EnvDock as EnvDockLegacy
from modules.envcorners.envcorners import EnvCorners
from modules.envlight.envlight import EnvLight
from fabric import Application
from fabric.utils import get_relative_path, monitor_file
import loguru
import setproctitle

from utils.functions import AppName
from config.c import c

loguru.logger.disable("fabric.hyprland.widgets")
loguru.logger.disable("fabric.widgets.wayland")
loguru.logger.disable("fabric.audio.service")
loguru.logger.disable("fabric.bluetooth.service")

def apply_style(app):
	loguru.logger.info("[Main] Applying CSS")
	app.set_stylesheet_from_file(get_relative_path("envshell.css"))

if __name__ == "__main__":
	envnoti = EnvNoti()
	#envcorners = EnvCorners() # FIXME: Fix the issue where they are just not correctly positioned
	envnotch = EnvNotch()
	envdock = None
	envpanel = None
	if c.get_rule("Widgets.panel.enable"):
		envpanel = EnvPanel()
	if c.get_rule("Widgets.dock.enable"):
		if c.get_rule("Dock.legacy"):
			envdock = EnvDockLegacy()
		else:
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
	setproctitle.setproctitle("envShell")

	css_file = monitor_file(get_relative_path("styles"))
	css_file.connect("changed", lambda *_: apply_style(app))

	apply_style(app)
	app.run()