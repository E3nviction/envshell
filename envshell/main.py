from modules.envnotch.envnotch import EnvNotch
from modules.envpanel.envpanel import EnvPanel
from modules.envnoti.envnoti import EnvNoti
from modules.envdock.envdock import EnvDock
from modules.envlight.envlight import EnvLight
from fabric import Application
import loguru

from utils.functions import AppName
from config.c import c

if __name__ == "__main__":
	if c.get_rule("Widgets.notch.enable"):
		envnotch = EnvNotch()
	if c.get_rule("Widgets.panel.enable"):
		envpanel = EnvPanel()
	if c.get_rule("Widgets.noti.enable"):
		envnoti = EnvNoti()
	if c.get_rule("Widgets.dock.enable"):
		envdock = EnvDock()
	if c.get_rule("Widgets.light.enable"):
		envlight = EnvLight()
	app = Application(
		"envshell",
		envnoti if c.get_rule("Widgets.noti.enable") else None,
		envnotch if c.get_rule("Widgets.notch.enable") else None,
		envdock if c.get_rule("Widgets.dock.enable") else None,
		envpanel if c.get_rule("Widgets.panel.enable") else None,
		envlight if c.get_rule("Widgets.dock.enable") else None
	)

	def set_css():
		app.set_stylesheet_from_file(
			"./envshell.css",
		)
	app.set_css = set_css
	app.set_css()

	app.run()