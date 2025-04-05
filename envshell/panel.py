from modules.envnotch.envnotch import EnvNotch
from modules.envpanel.envpanel import EnvPanel
from modules.envcorners.envcorners import EnvCorners
from modules.envlight.envlight import EnvLight
from fabric import Application
from fabric.utils import get_relative_path, monitor_file
import loguru
import sys
import setproctitle

from utils.functions import AppName, apply_style
from config.c import c

for disable in [
	"fabric.hyprland.widgets",
	"fabric.widgets.wayland",
	"fabric.audio.service",
	"fabric.bluetooth.service",
	"fabric.core.application",
]:
	loguru.logger.disable(disable)

if __name__ == "__main__":
	envcorners = EnvCorners()
	envnotch = None
	envpanel = None
	if c.get_rule("Notch.enable"):
		envnotch = EnvNotch()
	if c.get_rule("Panel.enable"):
		envpanel = EnvPanel()
	else:
		exit()
	apps = [
		envnotch,
		envpanel,
		envcorners,
	]
	apps = list(filter(lambda x: x is not None, apps))
	app = Application(
		"envshellPanel",
		*apps,
		open_inspector=len(sys.argv) > 1,
	)
	setproctitle.setproctitle("Panel")

	css_file = monitor_file(get_relative_path("styles"))
	css_file.connect("changed", lambda *_: apply_style(app))

	apply_style(app)
	if not c.get_rule("General.transparency"):
		app.set_stylesheet_from_file(get_relative_path("styles/transparency_false.css"), append=True)
	app.run()