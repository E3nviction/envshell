import datetime
import os
import shutil
from typing import Dict, List, Literal

import gi
from fabric.utils import exec_shell_command, exec_shell_command_async, get_relative_path
from fabric.widgets.image import Image
from gi.repository import Gdk, GLib, Gtk

def set_socket(value):
    try:
        with open(f"/tmp/envshell.socket", "w") as f:
            # clear file
            f.truncate(0)
            # write value
            f.write(value)
    except Exception as e:
        print("Failed to create socket:", e)
        sys.exit(1)

def get_from_socket():
    try:
        with open(f"/tmp/envshell.socket", "r") as f:
            lines = []
            for line in f:
                line = line.strip()
                if line == "\n": continue
                if line == "false":
                    lines.append(False)
                    continue
                if line == "true":
                    lines.append(True)
                    continue
                lines.append(line)
            return lines
    except Exception as e:
        print("Failed to read from socket:", e)
        sys.exit(1)