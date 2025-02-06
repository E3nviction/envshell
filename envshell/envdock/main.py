from hmac import new
import subprocess
import threading
import time
import json
import sys

from fabric import Application
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.svg import Svg
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib  # type: ignore

import os

app_list = {
    "NotFOUND": "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/abrt.svg",
}
app_name_translation_list = {
    "code": "vscode"
}
pinned = {
    "org.gnome.Nautilus": "nautilus",
    "gnome-disks": "gnome-disks",
    "org.gnome.baobab": "baobab",
    "kitty": "kitty",
    "brave-browser": "brave",
    "code": "code",
    "org.gnome.Calculator": "gnome-calculator",
    "org.gnome.TextEditor": "gnome-text-editor",
    "org.gnome.Loupe": "Image Viewer",
    "org.gnome.clocks": "gnome-clocks",
    "krita": "krita",
    "spotify": "spotify",
    "vesktop": "vesktop",
    "org.keepassxc.KeePassXC": "keepassxc",
    "com.github.rafostar.Clapper": "clapper",
    "blender": "blender",
    "obsidian": "obsidian",
}
app_names = json.load(open("./envpanel/app_names.json"))
exclude_list = [
    "kitty-dropterm",
    "albert",
    "main.py"
]
ignored_workspace_list = [
    9
]
icon_list = []
icon_dir = "/run/current-system/sw/share/icons/WhiteSur-dark/apps/scalable/"

# Get all the icons
for file in os.listdir(icon_dir):
    if file.endswith(".svg"):
        icon_list.append(file.removesuffix(".svg"))

# Add all the icons to the app_list
for icon in icon_list:
    app_list[icon] = f"{icon_dir}{icon}.svg"

from .services import AppService

from hyprpy import Hyprland

global instance
from utils.roam import instance


class EnvDock(Window):
    def __init__(self, **kwargs):
        super().__init__(
            layer="bottom",
            anchor="bottom center",
            exclusivity="auto",
            name="env-dock",
            margin=(0, 0, 5, 0),
            size=(400, 46),
            **kwargs,
        )

        self.app_service = AppService()
        self.app_service.connect(
            "apps-changed",
            lambda _, apps: self.update_ui_thread_safe(apps),
        )

        self.dock_box = Box(
            orientation="horizontal",
            name="dock-box",
			children=[],
            h_expand=True,
            v_expand=True,
        )

        self.children = CenterBox(
            start_children=[self.dock_box],
        )

        self.start_app_monitor_thread()

    def update_ui_thread_safe(self, _apps):
        """Update UI safely in the main thread."""
        def focus(b):
            try:
                print("Focus app: " + b.get_name())
                os.system("hyprctl dispatch focuswindow address:" + b.get_name())
            except:
                print("Failed to focus app")
        def launch(b):
            try:
                print("Launch app: " + b.get_name())
                os.system("hyprctl dispatch exec " + pinned[b.get_name()])
            except:
                print("Failed to launch app")
        def update_ui():
            self.dock_box.children = []
            apps = _apps
            # We have to eval the string to get the list, because Signals don't work with lists. Atleast I haven't found a way
            if apps[0] == "[" and apps[-1] == "]":
                apps: list = eval(apps)
            pinned_apps = {}
            apps_new = []
            for i, app in enumerate(apps):
                # Here we check if the app is in the pinned list
                if app[0] in pinned:
                    # If so we add it to the pinned_apps list and remove it from the apps list
                    pinned_apps[app[0]] = [app[0], app[1], app[2], app[3], app[4], True]
                else:
                    apps_new.append(app)
            apps = apps_new
            # Here we check if the pinned app has been overwritten, so if not, we can again add it to the pinned_apps list
            for p in pinned:
                if p not in pinned_apps:
                    pinned_apps[p] = [p, None, None, None, None, False]
            # We sort the pinned_apps by Alphabetical order
            #pinned_apps = dict(sorted(pinned_apps.items(), key=lambda item: item[0].lower()))
            # Actually its better to sort it by the pinned list, so its in the order that was set by the user
            pinned_apps = dict(sorted(pinned_apps.items(), key=lambda item: list(pinned.keys()).index(item[0])))
            for app_ in pinned_apps:
                app, pid, title, address, active, running = pinned_apps[app_]
                svg = Svg(svg_file=app_list["NotFOUND"], size=(32), name="dock-app-icon")
                app_i = app
                if app in app_name_translation_list:
                    app_i = app_name_translation_list[app]
                if str(app_i).lower() in app_list or str(app_i) in app_list:
                    if str(app_i).lower() in app_list:
                        svg = Svg(svg_file=app_list[str(app_i).lower()], size=(32), name="dock-app-icon")
                    else:
                        svg = Svg(svg_file=app_list[str(app_i)], size=(32), name="dock-app-icon")
                if app in app_names:
                    app = app_names[app]
                if running:
                    app_button = Box(
                        orientation="vertical",
                        children=[
                            Button(
                                child=svg,
                                name=f"{address}",
                                style_classes=("active" if active else "", "dock-app-button", "running"),
                                h_align="center",
                                v_align="center",
                                on_clicked=focus,
                                tooltip_text=f"{app}",
                            ),
                            Svg(svg_file="./envpanel/svgs/indicator.svg", size=(6), name="dock-app-indicator", h_align="center", v_align="center"),
                        ],
                    )
                else:
                    app_button = Box(
                        orientation="vertical",
                        children=[
                            Button(
                                child=svg,
                                name=f"{pinned_apps[app_][0]}",
                                style_classes=("active" if active else "", "dock-app-button"),
                                h_align="center",
                                v_align="center",
                                on_clicked=launch,
                                tooltip_text=f"{app}",
                            ),
                        ],
                    )
                self.dock_box.add(app_button)
            if not len(apps) == 0:
                self.dock_box.add(Box(orientation="horizontal", name="dock-seperator", h_expand=True, v_expand=True))
            for app, pid, title, address, active in apps:
                if app in app_name_translation_list:
                    app = app_name_translation_list[app]
                svg = Svg(svg_file=app_list["NotFOUND"], size=(32), name="dock-app-icon")
                if str(app).lower() in app_list or str(app) in app_list:
                    if str(app).lower() in app_list:
                        svg = Svg(svg_file=app_list[str(app).lower()], size=(32), name="dock-app-icon")
                    else:
                        svg = Svg(svg_file=app_list[str(app)], size=(32), name="dock-app-icon")
                if app in app_names:
                    app = app_names[app]
                app_button = Button(
                    child=svg,
                    name=f"{address}",
                    style_classes=("active" if active else "", "dock-app-button", address),
                    h_align="center",
                    v_align="center",
                    # we run a function here, because if we would use a lambda _: print(address) function it wouldn't work
                    on_clicked= focus,
                    # add app name and title (constrained to max 25 chars)
                    tooltip_text=f"{app} ({f"{title[:25]}..."})",
                )
                self.dock_box.add(app_button)
            self.dock_box.show_all()

        GLib.idle_add(update_ui)

    def start_app_monitor_thread(self):
        """Start a background thread to monitor open applications."""
        def fetch_open_apps(sender, **kwargs):
            print("Signal:", sender)
            global instance
            while True:
                try:
                    windows = instance.get_windows()
                    open_apps = []
                    for window in windows:
                        pid = window.pid
                        title = window.title
                        address = window.address
                        app_name = window.wm_class
                        if app_name == "":
                            app_name = window.title
                        if str(app_name).lower() not in exclude_list and str(app_name) not in exclude_list and window.workspace_id not in ignored_workspace_list:
                            try:
                                iaddress = instance.get_active_window().address
                            except:
                                iaddress = None
                            open_apps.append([app_name, pid, str(title), address, iaddress == address])
                    # sort alphabetically
                    open_apps = sorted(open_apps, key=lambda x: x[0])
                    self.app_service.apps = str(open_apps)
                except Exception as e:
                    print("Error fetching open apps:", e)
                    print("Exiting because of Error...")
                    sys.exit(1)
                time.sleep(0.25)

        instance.signal_active_window_changed.connect(fetch_open_apps)
        instance.signal_active_workspace_changed.connect(fetch_open_apps)
        instance.signal_window_created.connect(fetch_open_apps)
        instance.signal_window_destroyed.connect(fetch_open_apps)


if __name__ == "__main__":
    envdock = EnvDock()
    app = Application("envdock", envdock)
    app.set_stylesheet_from_file("./envdock/styles/style.css")
    app.run()