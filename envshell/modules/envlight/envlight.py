import operator
from collections.abc import Iterator
from fabric import Application
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.button import Button
from fabric.widgets.image import Image
from fabric.widgets.entry import Entry
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.utils import DesktopApp, get_desktop_applications, idle_add, remove_handler


class EnvLight(Window):
	def __init__(self, **kwargs):
		super().__init__(
			layer="top",
			anchor="center",
			exclusivity="none",
			keyboard_mode="on-demand",
			name="env-light",
			visible=False,
			all_visible=False,
			**kwargs,
		)
		self.add_keybinding("Escape", self.toggle)
		self.set_property("width-request", 400)
		self._arranger_handler: int = 0
		self._all_apps = get_desktop_applications()

		self.viewport = Box(spacing=2, orientation="v")
		self.search_entry = Entry(
			placeholder="Search Applications...",
			h_expand=True,
			notify_text=lambda entry, *_: self.arrange_viewport(entry.get_text()),
		)
		self.scrolled_window = ScrolledWindow(
			min_content_size=(280, 320),
			max_content_size=(280 * 2, 320),
			child=self.viewport,
		)

		self.add(
			Box(
				spacing=2,
				orientation="v",
				style="margin: 2px",
				children=[
					Box(
						spacing=2,
						orientation="h",
						children=[
							self.search_entry,
						],
					),
					self.scrolled_window,
				],
			)
		)
	def toggle(self, b, *_):
		if self.get_visible():
			self.hide()
		else:
			self.show_all()

	def arrange_viewport(self, query: str = ""):
		remove_handler(self._arranger_handler) if self._arranger_handler else None

		self.viewport.children = []

		filtered_apps_iter = iter(
			[
				app
				for app in self._all_apps
				if query.casefold()
				in (
					(app.display_name or "")
					+ (" " + app.name + " ")
					+ (app.generic_name or "")
				).casefold()
			]
		)
		should_resize = operator.length_hint(filtered_apps_iter) == len(self._all_apps)
		self._arranger_handler = idle_add(
			lambda *args: self.add_next_application(*args)
			or (self.resize_viewport() if should_resize else False),
			filtered_apps_iter,
			pin=True,
		)

		return False

	def add_next_application(self, apps_iter: Iterator[DesktopApp]):
		if not (app := next(apps_iter, None)):
			return False

		self.viewport.add(self.bake_application_slot(app))
		return True

	def resize_viewport(self):
		self.scrolled_window.set_min_content_width(
			self.viewport.get_allocation().width  # type: ignore
		)
		return False

	def bake_application_slot(self, app: DesktopApp, **kwargs) -> Button:
		return Button(
			child=Box(
				orientation="h",
				spacing=12,
				name="light-suggestion",
				children=[
					Image(pixbuf=app.get_icon_pixbuf(), h_align="start", size=32),
					Label(
						label=app.display_name or "Unknown",
						v_align="center",
						h_align="center",
					),
				],
			),
			tooltip_text=app.description,
			on_clicked=lambda *_: (app.launch(), self.toggle(None)),
			**kwargs,
		)