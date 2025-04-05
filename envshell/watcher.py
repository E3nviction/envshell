import psutil
import subprocess
import setproctitle
import time

from fabric.utils.helpers import get_relative_path

from config.c import c

def is_running(name):
	"""Check if a process with the given name is running."""
	return any(proc.name() == name for proc in psutil.process_iter(attrs=["name"]))

def wait_for_process(name):
	while not is_running(name):
		time.sleep(0.1)  # Check every 100ms

def restart_if_needed(process_name, script_name):
	if not is_running(process_name):
		print(f"{process_name} is not running. Starting {script_name}...")
		subprocess.Popen(f"python {get_relative_path(script_name)} &", shell=True)
		wait_for_process(process_name)
		print(f"{process_name} has started.")

def monitor():
	process_names = {
		"Panel": "panel.py",
		"Dock": "dock.py",
		"ScreenFilter": "screenfilter.py",
	}

	if not c.get_rule("Dock.enable"):          process_names.pop("Dock")
	if not c.get_rule("Panel.enable"):         process_names.pop("Panel")
	if not c.get_rule("ScreenFilter.enable"):  process_names.pop("ScreenFilter")

	existing_pids = {p.pid for p in psutil.process_iter(attrs=["pid"])}

	while True:
		time.sleep(.1)
		current_pids = {p.pid for p in psutil.process_iter(attrs=["pid"])}
		if current_pids != existing_pids:
			for process, script in process_names.items():
				restart_if_needed(process, script)
			existing_pids = current_pids

if __name__ == "__main__":
	setproctitle.setproctitle("envShell")
	monitor()
