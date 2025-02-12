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


from config.c import c


class Notch(Window):
    def __init__(self, **kwargs):
        super().__init__(
            layer="overlay",
            anchor="top center",
            exclusivity="none",
            name="env-notch",
            margin=(0, 0, 0, 0),
            size=(200, 32),
            **kwargs,
        )

        self.notch_box = Box(
            orientation="horizontal",
            name="notch-box",
			children=[],
			size=(200, 32),
            h_expand=True,
            v_expand=True,
        )

        self.children = CenterBox(
            start_children=[self.notch_box],
        )
