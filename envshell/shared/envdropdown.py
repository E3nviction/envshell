from fabric.widgets.centerbox import CenterBox
from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow as Window

from utils.roam import envshell_service

def dropdown_divider(comment): return Box(children=[Box(name="dropdown-divider", h_expand=True)], name="dropdown-divider-box", h_align="fill", h_expand=True, v_expand=True,)

class EnvDropdown(Window):
	"""A Dropdown for envshell"""
	def __init__(self, x, y, w=-1, h=-1, dropdown_children=None, **kwargs):
		super().__init__(
			layer="top",
			anchor="left top",
			exclusivity="auto",
			name="dropdown-menu",
			visible=False,
			margin=(y, 0, 0, x),
			**kwargs,
		)

		self.id = -1

		self.set_property("width-request", w)
		self.set_property("height-request", h)

		envshell_service.connect("dropdowns-hide-changed", self.hide_dropdown)

		self.dropdown = Box(
			children=dropdown_children or [],
			h_expand=True,
			name="dropdown-options",
			orientation="vertical",
		)

		self.dropdown.set_property("width-request", w)
		self.dropdown.set_property("height-request", h)

		self.child_box = CenterBox(start_children=[self.dropdown])

		self.child_box.set_property("width-request", w)
		self.child_box.set_property("height-request", h)

		self.children = self.child_box
		self.connect("event", self.hide_dropdown)

	def toggle_dropdown(self, button):
		self.set_visible(not self.is_visible())
		if self.is_visible():
			if envshell_service.current_dropdown == 1:
				self.id = 0
				envshell_service.current_dropdown = 0
			else:
				self.id = 1
				envshell_service.current_dropdown = 1
	def hide_dropdown(self, widget, event):
		x, y = self.get_pointer()
		allocation = self.get_allocation()
		if not 0 < x <= allocation.width - 1 and 0 < y <= allocation.height - 1 or envshell_service.current_dropdown != self.id:
			self.hide()
