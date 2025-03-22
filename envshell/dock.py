from modules.envdock.envdock import EnvDock
from modules.envdock.envdock_old import EnvDock as EnvDockLegacy
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
	if c.get_rule("Dock.enable"):
		app = Application(
			"envshellDock",
			EnvDockLegacy() if c.get_rule("Dock.legacy") else EnvDock(),
			open_inspector=len(sys.argv) > 1,
		)
	else:
		exit()
	setproctitle.setproctitle("Dock")

	css_file = monitor_file(get_relative_path("styles"))
	css_file.connect("changed", lambda *_: apply_style(app))

	apply_style(app)
	if not c.get_rule("General.transparency"):
		app.set_stylesheet_from_file(get_relative_path("styles/transparency_false.css"), append=True)
	app.run()