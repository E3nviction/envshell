from typing import Any
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.widget import Widget

from gi.repository import GtkLayerShell # type: ignore

from styledwidgets.styled import styler, style_dict
from styledwidgets.agents import margins, paddings, transitions, colors, shadows, borderradius, textsize
from styledwidgets.types import px, rem
from styledwidgets.color import alpha, hex

from utils.roam import envshell_service

class MouseCatcher(Window):
	"""A Window that spans across the entire screen, to essentially catch the mouse"""
	def __init__(self, layer: str, child_window: Window, **kwargs):
		super().__init__(
			layer=layer,
			anchor="top bottom left right",
			exclusivity="auto",
			title="envshell-mousecatch",
			name="MouseCatcher",
			keyboard_mode="exclusive",
			style=styler(
				background_color=alpha(colors.black, 0),
				border_radius=px(0),
			),
			all_visible=False,
			visible=False,
			**kwargs,
		)

		GtkLayerShell.set_exclusive_zone(self, -1)

		self.child_window = child_window

		# when clicking on the mousecatcher, hide the child window
		self.event_box = EventBox(
			events=["enter-notify-event", "leave-notify-event", "button-press-event"],
			all_visible=True,
		)
		self.event_box.connect("button-press-event", self.hide_child_window)

		self.children = [self.event_box]

	def show_child_window(self, widget: Widget, event: Any) -> None:
		self.child_window._set_mousecatcher(True)
		self.set_visible(True)
		self.pass_through = False

	def hide_child_window(self, widget: Widget, event: Any) -> None:
		self.child_window._set_mousecatcher(False)
		envshell_service.current_dropdown = None
		self.set_visible(False)
		self.pass_through = True

	def dropdowns_hide_changed(self, widget: Widget, event: Any) -> None:
		self.child_window._set_mousecatcher(False)
		self.set_visible(False)
		self.pass_through = True

	def toggle_mousecatcher(self, *_) -> None:
		self.set_visible(not self.is_visible())
		self.pass_through = not self.is_visible()
		self.child_window._set_mousecatcher(self.is_visible())


class DropDownMouseCatcher(MouseCatcher):
	"""A Window that spans across the entire screen, to essentially catch the mouse"""
	def __init__(self, *args, **kwargs):
		super().__init__(
			*args,
			**kwargs,
		)
		envshell_service.connect("dropdowns-hide-changed", self.dropdowns_hide_changed)

	def dropdowns_hide_changed(self, widget: Widget, event: Any) -> None:
		if envshell_service.current_dropdown == self.child_window.id: return
		return super().dropdowns_hide_changed(widget, event)