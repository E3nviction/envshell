from fabric.widgets.centerbox import CenterBox
from fabric.widgets.box import Box
from fabric.widgets.wayland import WaylandWindow as Window

from utils.roam import envshell_service

dropdowns = []

def dropdown_divider(comment): return Box(children=[Box(name="dropdown-divider", h_expand=True)], name="dropdown-divider-box", h_align="fill", h_expand=True, v_expand=True,)

class EnvDropdown(Window):
	"""A Dropdown for envshell"""
	def __init__(self, x, y, w=-1, h=-1, dropdown_children=None, parent=None, **kwargs):
		super().__init__(
			layer="top",
			anchor="left top",
			exclusivity="auto",
			name="dropdown-menu",
			visible=False,
			margin=(y, 0, 0, x),
			**kwargs,
		)

		self.id = len(dropdowns)
		dropdowns.append(self)

		self.set_property("width-request", w)
		self.set_property("height-request", h)

		self.x_set = x
		self.y_set = y

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
		self.connect("button-press-event", self.hide_dropdown)
		self.add_keybinding("Escape", self.hide_dropdown)

	def toggle_dropdown(self, button, parent=None):
		# if parent, then set the x, and y to parent alloc
		if parent:
			par_alloc = parent.get_allocation()
			self.margin = (par_alloc.y + self.y_set, 0, 0, par_alloc.x + self.x_set)
		self.set_visible(not self.is_visible())
		if self.is_visible():
			self.pass_through = False
			self.keyboard_mode = "exclusive"
			self.grab_focus()
			envshell_service.current_dropdown = self.id
	def hide_dropdown(self, widget, event):
		x, y = self.get_pointer()
		allocation = self.get_allocation()
		if envshell_service.current_dropdown != self.id:
			self.hide()
