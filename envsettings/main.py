import gi # type: ignore

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk # type: ignore

class SettingsApp(Gtk.Window):
	def __init__(self):
		super().__init__(title="Settings")
		self.set_default_size(800, 600)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_name("settings-window")

		# Main layout
		main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
		self.add(main_box)

		# Sidebar (categories)
		sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		sidebar.set_size_request(250, -1)
		sidebar.set_name("sidebar")

		# Sidebar buttons
		self.current_tab = 0
		general_button = Gtk.Button(label="General", halign=Gtk.Align.START)
		general_button.connect("clicked", self.show_general_settings)
		display_button = Gtk.Button(label="Display", halign=Gtk.Align.START)
		display_button.connect("clicked", self.show_display_settings)
		about_button = Gtk.Button(label="About", halign=Gtk.Align.START)
		about_button.connect("clicked", self.show_about_settings)

		for button in [general_button, display_button, about_button]:
			button.set_name("sidebar-button")
			sidebar.pack_start(button, False, False, 0)

		# Main content area
		self.content_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		self.content_area.set_name("content-area")

		# Add sidebar and content area to main box
		main_box.pack_start(sidebar, False, False, 0)
		main_box.pack_start(self.content_area, True, True, 0)

		# Load General settings by default
		self.show_general_settings()

	def clear_content_area(self):
		for child in self.content_area.get_children():
			self.content_area.remove(child)

	def show_general_settings(self, button=None):
		self.clear_content_area()
		self.current_tab = 0

		general_label = Gtk.Label(label="General", halign=Gtk.Align.START)
		general_label.set_name("content-title")

		dummy_switch = Gtk.Switch()
		dummy_switch.set_active(True)
		switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		switch_box.pack_start(Gtk.Label(label="Enable Feature X:"), False, False, 0)
		switch_box.pack_start(dummy_switch, False, False, 0)

		self.content_area.pack_start(general_label, False, False, 0)
		self.content_area.pack_start(switch_box, False, False, 0)
		self.content_area.show_all()

	def show_display_settings(self, button=None):
		self.clear_content_area()
		self.current_tab = 1

		display_label = Gtk.Label(label="Display", halign=Gtk.Align.START)
		display_label.set_name("content-title")

		resolution_combo = Gtk.ComboBoxText()
		resolution_combo.append_text("1920x1080")
		resolution_combo.append_text("2560x1440")
		resolution_combo.append_text("3840x2160")
		resolution_combo.set_active(0)
		resolution_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
		resolution_box.pack_start(Gtk.Label(label="Resolution:"), False, False, 0)
		resolution_box.pack_start(resolution_combo, False, False, 0)

		self.content_area.pack_start(display_label, False, False, 0)
		self.content_area.pack_start(resolution_box, False, False, 0)
		self.content_area.show_all()

	def show_about_settings(self, button=None):
		self.clear_content_area()
		self.current_tab = 2

		about_label = Gtk.Label(label="About", halign=Gtk.Align.START)
		about_label.set_name("content-title")

		about_text = Gtk.Label(
			label="""
EnvSettings App v1.0\n
Developed by Enviction\n
This is a settings app for Env Shell
			"""
		)
		about_text.set_justify(Gtk.Justification.LEFT)

		self.content_area.pack_start(about_label, False, False, 0)
		self.content_area.pack_start(about_text, False, False, 0)
		self.content_area.show_all()

# Run the app
def main():
	win = SettingsApp()
	win.connect("destroy", Gtk.main_quit)
	win.show_all()

	# Load CSS
	css_provider = Gtk.CssProvider()
	css_provider.load_from_path("style.css")
	Gtk.StyleContext.add_provider_for_screen(
		Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)

	Gtk.main()

if __name__ == "__main__":
	main()
