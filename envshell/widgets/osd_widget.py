import time
from typing import Literal
from fabric import Fabricator
from fabric.widgets.box import Box
from fabric.widgets.revealer import Revealer
from fabric.widgets.scale import Scale
from fabric.widgets.label import Label
from fabric.widgets.eventbox import EventBox
from fabric.widgets.wayland import WaylandWindow as Window
from gi.repository import Gtk  # type: ignore


def get_current_time_ms():
    return round(time.time() * 1000)


class OsdWindow(Window):
    def __init__(
        self,
        _children: list,
        transition_type: (
            Literal[
                "none",
                "crossfade",
                "slide-right",
                "slide-left",
                "slide-up",
                "slide-down",
            ]
            | Gtk.RevealerTransitionType
        ) = "crossfade",
        transition_duration: int = 400,
        revealer_name: str | None = None,
        hide_timeout: int = 2000,
        fabricator_interval: int = 1000,
        **kwargs,
    ):
        super().__init__(
            pass_through=True,
            **kwargs
        )

        self.box = Box(name="envshell-osd", orientation="vertical", children=_children)
        self.event_box = EventBox(child=self.box, all_visible=True)
        self.revealer = Revealer(
            name=revealer_name,
            transition_type=transition_type,
            transition_duration=transition_duration,
            reveal_child=True,
            child=self.event_box,
        )
        self.hide_timeout = hide_timeout
        self.alive = get_current_time_ms()
        self.fabricator = Fabricator(
            poll_from=lambda x: self.osd_should_hide(),
            interval=1000,
            on_changed=self.hide,
            initial_poll=False,
        )

        self.children = Box(style="padding: 1px;", children=self.revealer)
        super().show()

    def osd_should_hide(self) -> bool:
        if get_current_time_ms() > self.hide_timeout + self.alive:
            return True
        return False

    def hide(self, _, should_hide: bool):
        if should_hide and self.is_visible() and self.revealer.child_revealed:
            self.revealer.unreveal()
            self.fabricator.stop()

    def show(self):
        self.revealer.reveal()
        self.fabricator.start()
        self.alive = get_current_time_ms()