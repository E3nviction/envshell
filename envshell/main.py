from envpanel.envpanel import EnvPanel
from envdock.envdock import EnvDock
#from envnotch.main import EnvNotch
from fabric import Application

if __name__ == "__main__":
	envpanel = EnvPanel()
	envdock = EnvDock()
	app = Application("envshell", envdock)

	def set_css():
		app.set_stylesheet_from_file(
			"./envshell.css",
		)
	app.set_css = set_css
	app.set_css()

	app.run()