import datetime
import os
import shutil
import subprocess
from typing import Dict, List, Literal

import gi
from fabric.utils import exec_shell_command, exec_shell_command_async, get_relative_path
from fabric.widgets.image import Image
from .icons import icons
from gi.repository import Gdk, GLib, Gtk


def parse_markup(text):
	return text

def check_icon_exists(icon_name: str, fallback_icon: str) -> str:
    if Gtk.IconTheme.get_default().has_icon(icon_name):
        return icon_name
    return fallback_icon

def get_icon(app_icon, size=25) -> Image:
    icon_size = size - 5
    try:
        match app_icon:
            case str(x) if "file://" in x:
                return Image(
                    name="app-icon",
                    image_file=app_icon[7:],
                    size=size,
                )
            case str(x) if len(x) > 0 and x[0] == "/":
                return Image(
                    name="app-icon",
                    image_file=app_icon,
                    size=size,
                )
            case _:
                return Image(
                    name="app-icon",
                    icon_name=app_icon
                    if app_icon
                    else icons["fallback"]["notification"],
                    icon_size=icon_size,
                )
    except GLib.GError:
        return Image(
            name="app-icon",
            icon_name=icons["fallback"]["notification"],
            icon_size=icon_size,
        )