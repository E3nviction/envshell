from fabric.widgets.centerbox import CenterBox
from fabric.widgets.box import Box
from fabric.widgets.eventbox import EventBox
from fabric.widgets.wayland import WaylandWindow as Window

from widgets.popup_window_custom import PopupWindow

from utils.roam import envshell_service

dropdowns = []

def dropdown_divider(comment): return Box(children=[Box(name="dropdown-divider", h_expand=True)], name="dropdown-divider-box", h_align="fill", h_expand=True, v_expand=True,)

class EnvDropdown(PopupWindow):
	"""A Dropdown for envshell"""
	def __init__(self, dropdown_children=None, dropdown_id=None, **kwargs):
		super().__init__(
			layer="top",
			exclusivity="auto",
			name="dropdown-menu",
			keyboard_mode="none",
			visible=False,
			**kwargs,
		)

		self.id = dropdown_id or str(len(dropdowns))
		dropdowns.append(self)

		envshell_service.connect("dropdowns-hide-changed", self.hide_dropdown)

		self.dropdown = Box(
			children=dropdown_children or [],
			h_expand=True,
			name="dropdown-options",
			orientation="vertical",
		)

		self.child_box = CenterBox(start_children=[self.dropdown])

		self.event_box = EventBox(
			events=["enter-notify-event", "leave-notify-event"],
			child=self.child_box,
			all_visible=True,
		)

		self.children = [self.event_box]
		self.event_box.connect("enter-notify-event", self.on_cursor_enter)
		self.event_box.connect("leave-notify-event", self.on_cursor_leave)
		self.connect("button-press-event", self.hide_dropdown)
		self.add_keybinding("Escape", self.hide_dropdown)

	def toggle_dropdown(self, button, parent=None):
		self.set_visible(not self.is_visible())
		if self.is_visible():
			self.keyboard_mode = "exclusive"
			self.steal_input()
			envshell_service.current_dropdown = self.id
		else:
			self.keyboard_mode = "none"
			self.return_input()
			envshell_service.current_dropdown = None
	def hide_dropdown(self, widget, event):
		if envshell_service.current_dropdown != self.id:
			self.hide()

	def on_cursor_enter(self, *_):
		self.set_visible(True)

	def on_cursor_leave(self, *_):
		if self.is_hovered():
			return
		self.set_visible(False)
		envshell_service.dropdowns_hide = not envshell_service.dropdowns_hide
