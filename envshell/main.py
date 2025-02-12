from envnotch.envnotch import EnvNotch
from envpanel.envpanel import EnvPanel
from envdock.envdock import EnvDock
from fabric import Application

if __name__ == "__main__":
	envnotch = EnvNotch()
	envpanel = EnvPanel()
	envdock = EnvDock()
	app = Application("envshell", envnotch, envdock, envpanel)

	def set_css():
		app.set_stylesheet_from_file(
			"./envshell.css",
		)
	app.set_css = set_css
	app.set_css()

	app.run()