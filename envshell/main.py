from modules.envnotch.envnotch import EnvNotch
from modules.envpanel.envpanel import EnvPanel
from modules.envnoti.envnoti import EnvNoti
from modules.envdock.envdock import EnvDock
from modules.envlight.envlight import EnvLight
from fabric import Application
import loguru

if __name__ == "__main__":
	envnotch = EnvNotch()
	envpanel = EnvPanel()
	envnoti = EnvNoti()
	envdock = EnvDock()
	envlight = EnvLight()
	app = Application("envshell", envnoti, envnotch, envdock, envpanel, envlight)

	def set_css():
		app.set_stylesheet_from_file(
			"./envshell.css",
		)
	app.set_css = set_css
	app.set_css()

	app.run()