import psutil
import subprocess
import setproctitle
import time

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
		subprocess.Popen(f"python {script_name} &", shell=True)
		wait_for_process(process_name)
		print(f"{process_name} has started.")

def monitor():
	process_names = {
		"Shell": "shell.py",
		"Dock": "dock.py"
	}

	if not c.get_rule("Dock.enable"):
		process_names.pop("Dock")

	existing_pids = {p.pid for p in psutil.process_iter(attrs=["pid"])}

	while True:
		current_pids = {p.pid for p in psutil.process_iter(attrs=["pid"])}
		if current_pids != existing_pids:
			for process, script in process_names.items():
				restart_if_needed(process, script)
			existing_pids = current_pids

if __name__ == "__main__":
	setproctitle.setproctitle("envShell")
	monitor()
