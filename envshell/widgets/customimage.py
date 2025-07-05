import math
import cairo
from typing import cast
from fabric.widgets.image import Image
from fabric import Service
from .animator import Animator
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject, GLib # type: ignore

class CustomImage(Image):
    def do_render_rectangle(
        self, cr: cairo.Context, width: int, height: int, radius: int = 0
    ):
        cr.move_to(radius, 0)
        cr.line_to(width - radius, 0)
        cr.arc(width - radius, radius, radius, -(math.pi / 2), 0)
        cr.line_to(width, height - radius)
        cr.arc(width - radius, height - radius, radius, 0, (math.pi / 2))
        cr.line_to(radius, height)
        cr.arc(radius, height - radius, radius, (math.pi / 2), math.pi)
        cr.line_to(0, radius)
        cr.arc(radius, radius, radius, math.pi, (3 * (math.pi / 2)))
        cr.close_path()

    def do_draw(self, cr: cairo.Context):
        context = self.get_style_context()
        width, height = self.get_allocated_width(), self.get_allocated_height()
        cr.save()

        self.do_render_rectangle(
            cr,
            width,
            height,
            cast(int, context.get_property("border-radius", Gtk.StateFlags.NORMAL)),
        )
        cr.clip()
        Image.do_draw(self, cr)

        cr.restore()



class HoverSVG(Gtk.EventBox):
    def __init__(self, svg_path=None, pixbuf=None, size=64, hover_size=96, duration=0.3, bezier=(0.34, 1.56, 0.64, 1.0), name=None):
        super().__init__()
        self.image = Gtk.Image()
        self.add(self.image)

        self.svg_path = svg_path
        self.pixbuf = pixbuf
        self.default_size = size
        self.hover_size = hover_size
        self.size = size

        if name:
            self.set_name(name)

        self.set_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)

        self.animator = Animator(
            bezier_curve=bezier,
            duration=duration,
            min_value=size,
            max_value=hover_size,
            tick_widget=self,
            notify_value=lambda p, *_: self.set_size(p.value),
        ).build().unwrap()

        self.connect("enter-notify-event", self.on_hover)
        self.connect("leave-notify-event", self.on_leave)

    def set_size(self, size):
        self.size = size
        if not self.pixbuf:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.svg_path, size, size)
        else:
            pixbuf = self.pixbuf.scale_simple(size, size, GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(pixbuf)

    def animate_value(self, value: float):
        self.animator.pause()
        self.animator.min_value = self.size
        self.animator.max_value = value
        self.animator.play()
        return

    def on_hover(self, *args):
        self.animate_value(self.hover_size)

    def on_leave(self, *args):
        self.animate_value(self.default_size)

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Animated SVG Hover")
        self.set_default_size(300, 300)

        box = Gtk.Box(spacing=10)
        svg = HoverSVG("./assets/svgs/imac.svg", size=64, hover_size=100, duration=0.15)
        box.pack_start(svg, False, False, 0)

        self.add(box)
        self.show_all()


if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()