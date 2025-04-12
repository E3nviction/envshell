from modules.others.misc import ActivateLinux
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
	misc_activatelinux = None
	if c.get_rule("Misc.activate-linux.enable"):
		misc_activatelinux = ActivateLinux()
	apps = [
		misc_activatelinux,
	]
	apps = list(filter(lambda x: x is not None, apps))
	app = Application(
		"envshellMisc",
		*apps,
		open_inspector=len(sys.argv) > 1,
	)
	setproctitle.setproctitle("envShell Misc")

	css_file = monitor_file(get_relative_path("styles"))
	css_file.connect("changed", lambda *_: apply_style(app))

	apply_style(app)
	app.run()