import threading
import time
import sys
import os

from fabric import Application
from fabric.widgets.button import Button
from fabric.widgets.svg import Svg
from fabric.widgets.box import Box
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import GLib


from config.c import c, app_list, icon_list, icon_dir

# Get all the icons
for file in os.listdir(icon_dir):
    if file.endswith(".svg"): icon_list.append(file.removesuffix(".svg"))

# Add all the icons to the app_list
for icon in icon_list: app_list[icon] = f"{icon_dir}{icon}.svg"

global instance
global envshell_service
from utils.roam import create_instance, envshell_service
instance = create_instance()


class EnvDock(Window):
    """Hackable dock for envshell."""
    def __init__(self, **kwargs):
        super().__init__(
            layer="top",
            anchor=c.get_shell_rule(rule="dock-position"),
            exclusivity="auto",
            name="env-dock",
            style=f"""
                border-radius: {c.get_shell_rule(rule="dock-rounding")};
            """,
            margin=c.get_shell_rule(rule="dock-margin"),
            size=(400, 46),
            **kwargs,
        )

        envshell_service.connect(
            "dock-apps-changed",
            lambda _, apps: self.dock_apps_changed(apps),
        )

        self.dock_box = Box(
            orientation=c.get_shell_rule(rule="dock-orientation"),
            name="dock-box",
            style=f"""
                border-radius: {c.get_shell_rule(rule="dock-rounding")};
            """,
			children=[],
            h_expand=True,
            v_expand=True,
        )

        self.children = CenterBox(
            start_children=[self.dock_box],
        )

        self.start_update_thread()

    def dock_apps_changed(self, _apps):
        """Update UI safely in the main thread."""
        def focus(b): os.system("hyprctl dispatch focuswindow address:" + b.get_name())
        def launch(b): os.system("hyprctl dispatch exec " + c.dock_pinned[b.get_name()])
        def dock_apps_changed_update():
            self.dock_box.children = []
            apps = _apps
            # We have to eval the string to get the list, because Signals don't work with lists. Atleast I haven't found a way
            if apps[0] == "[" and apps[-1] == "]": apps: list = eval(apps)
            pinned_apps = {}
            apps_new = []
            for i, app in enumerate(apps):
                if app[0] not in c.dock_pinned:
                    apps_new.append(app)
                    continue
                pinned_apps[app[0]] = [app[0], app[1], app[2], app[3], app[4], True]
            apps = apps_new
            for p in c.dock_pinned:
                if p not in pinned_apps:
                    pinned_apps[p] = [p, None, None, None, None, False]
            pinned_apps = dict(sorted(pinned_apps.items(), key=lambda item: list(c.dock_pinned.keys()).index(item[0])))
            for app_ in pinned_apps:
                app, pid, title, address, active, running = pinned_apps[app_]
                svg = Svg(svg_file=app_list["NotFOUND"], size=(32), name="dock-app-icon")
                app_i = app
                app_i = c.get_translation(wmclass=app)
                if str(app_i).lower() in app_list or str(app_i) in app_list:
                    if str(app_i).lower() in app_list:
                        svg = Svg(svg_file=app_list[str(app_i).lower()], size=(32), name="dock-app-icon")
                    else:
                        svg = Svg(svg_file=app_list[str(app_i)], size=(32), name="dock-app-icon")
                app = c.get_title(wmclass=app, title=title)
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
                            Svg(svg_file="./assets/svgs/indicator.svg", size=(6), name="dock-app-indicator", h_align="center", v_align="center"),
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
                app = c.get_translation(wmclass=app)
                svg = Svg(svg_file=app_list["NotFOUND"], size=(32), name="dock-app-icon")
                if str(app).lower() in app_list or str(app) in app_list:
                    if str(app).lower() in app_list:
                        svg = Svg(svg_file=app_list[str(app).lower()], size=(32), name="dock-app-icon")
                    else:
                        svg = Svg(svg_file=app_list[str(app)], size=(32), name="dock-app-icon")
                app = c.get_title(wmclass=app, title=title)
                app_button = Box(
                    orientation="vertical",
                    children=[
                        Button(
                            child=svg,
                            name=f"{address}",
                            style_classes=("active" if active else "", "dock-app-button", address),
                            h_align="center",
                            v_align="center",
                            # we run a function here, because if we would use a lambda _: print(address) function it wouldn't work
                            on_clicked= focus,
                            # add app name and title (constrained to max 25 chars)
                            tooltip_text=f"{app} ({f"{title[:25]}..."})",
                        ),
                        Svg(svg_file="./assets/svgs/indicator.svg", size=(6), name="dock-app-indicator", h_align="center", v_align="center"),
                    ],
                )
                self.dock_box.add(app_button)
            self.dock_box.show_all()

        GLib.idle_add(dock_apps_changed_update)

    def start_update_thread(self):
        """Start a background thread to monitor open applications."""
        def run():
            while True:
                windows = instance.get_windows()
                open_apps = []
                for window in windows:
                    pid = window.pid
                    title = window.title
                    address = window.address
                    app_name = window.wm_class
                    if app_name == "":
                        app_name = window.title
                    if not (c.is_window_ignored(wmclass=str(app_name).lower()) or c.is_window_ignored(wmclass=str(app_name)) or c.is_workspace_ignored(id_=window.workspace_id)):
                        try:
                            iaddress = instance.get_active_window().address
                        except:
                            iaddress = None
                        open_apps.append([app_name, pid, str(title), address, iaddress == address])
                # sort alphabetically
                open_apps = sorted(open_apps, key=lambda x: x[0])
                envshell_service.dock_apps = str(open_apps)
                time.sleep(0.25)

        threading.Thread(target=run, daemon=True).start()