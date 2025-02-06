from envpanel.main import EnvPanel
from envdock.main import EnvDock
#from envnotch.main import EnvNotch
from fabric import Application

if __name__ == "__main__":
	envpanel = EnvPanel()
	envdock = EnvDock()
	app = Application("envshell", envdock)
	app.set_stylesheet_from_file("./style.css")
	app.run()