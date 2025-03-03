import subprocess
import threading
import time


from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.label import Label
from fabric.widgets.overlay import Overlay
from fabric.widgets.button import Button
from fabric.widgets.box import Box
from fabric.widgets.image import Image
from fabric.widgets.checkbutton import CheckButton
from fabric.widgets.scale import Scale
from fabric.widgets.svg import Svg
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.utils.helpers import exec_shell_command_async
from fabric.audio import Audio
from fabric.bluetooth import BluetoothClient, BluetoothDevice
from gi.repository import GLib, Gtk

global envshell_service
global audio_service
from utils.roam import envshell_service, audio_service
from utils.exml import exml

from utils.functions import get_from_socket

from config.c import c

class BluetoothDeviceSlot(CenterBox):
    def __init__(self, device: BluetoothDevice, **kwargs):
        super().__init__(**kwargs)
        self.device = device
        self.device.connect("changed", self.on_changed)
        self.device.connect(
            "notify::closed", lambda *_: self.device.closed and self.destroy()
        )

        self.styles = [
            "connected" if self.device.connected else "",
            "paired" if self.device.paired else "",
        ]

        self.dimage = Image(
            icon_name=device.icon_name + "-symbolic",
            size=5,
            name="device-icon",
            style_classes=" ".join(self.styles),
        )

        self.start_children = [
            Button(
                image=self.dimage,
                on_clicked=lambda *_: self.toggle_connecting(),
            ),
            Label(label=device.name),
        ]

        self.device.emit("changed")  # to update display status

    def toggle_connecting(self):
        self.device.emit("changed")
        self.device.set_connecting(not self.device.connected)

    def on_changed(self, *_):
        self.styles = [
            "connected" if self.device.connected else "",
            "paired" if self.device.paired else "",
        ]
        self.dimage.set_property("style-classes", " ".join(self.styles))
        return


class BluetoohConnections(Box):
    def __init__(self, **kwargs):
        super().__init__(
            spacing=4,
            orientation="vertical",
            style="margin: 8px",
            **kwargs,
        )

        self.client = BluetoothClient(on_device_added=self.on_device_added)
        self.title = Label("Bluetooth")
        self.scan_button = Button(
            name="scan-button",
            on_clicked=lambda *_: self.client.toggle_scan()
        )
        self.toggle_button = CheckButton(
            name="toggle-button",
            on_clicked=lambda *_: self.client.toggle_power()
        )

        self.client.connect(
            "notify::enabled",
            lambda *_: self.toggle_button.set_label(
                "Bluetooth " + ("On" if self.client.enabled else "Off")
            ),
        )
        self.client.connect(
            "notify::scanning",
            lambda *_: self.scan_button.set_label(
                "Stop" if self.client.scanning else "Scan"
            ),
        )

        self.not_paired = Box(spacing=2, orientation="vertical")
        self.paired = Box(spacing=2, orientation="vertical")

        self.device_box = Box(spacing=2, orientation="vertical", children=[self.paired, self.not_paired])

        self.children = [
            CenterBox(start_children=self.title, center_children=self.scan_button, end_children=self.toggle_button, name="bluetooth-widget-top"),
            Label("Devices", h_align="start", name="devices-title"),
            ScrolledWindow(min_content_size=(300, 400), max_content_size=(300, 800), child=self.device_box, overlay_scroll=True),
        ]
        self.client.notify("scanning")
        self.client.notify("enabled")

    def on_device_added(self, client: BluetoothClient, address: str):
        if not (device := client.get_device(address)):
            return
        slot = BluetoothDeviceSlot(device, paired=device.paired)

        if device.name in ["", None] and not c.get_rule("Bluetooth.show-hidden-devices"):
            return
        if device.paired:
            return self.paired.add(slot)
        return self.not_paired.add(slot)