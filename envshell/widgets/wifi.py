import gi # type: ignore

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, GObject, Gdk # type: ignore

from utils.async_tm import AsyncTaskManager # type: ignore

async_task_manager = AsyncTaskManager()

import asyncio
from utils.wifi_backend import (
    get_wifi_networks,
    get_network_speed,
    connect_network,
    forget_network,
    disconnect_network,
    fetch_currently_connected_ssid,
    get_wifi_status,
    set_wifi_power,
)

from loguru import logger

"""
Thanks to @kaipark for the following code.
"""

class WifiNetworkRow(Gtk.ListBoxRow):
    def __init__(self, network_data, **kwargs):
        super().__init__(**kwargs)
        self.set_margin_top(5)
        self.set_margin_bottom(5)
        self.set_margin_start(10)
        self.set_margin_end(10)

        self.network_data = network_data

        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        container.set_spacing(10)

        try:
            signal_strength = int(self.network_data["signal"])
        except (ValueError, TypeError):
            signal_strength = 0

        if signal_strength >= 80:
            icon_name = "network-wireless-signal-excellent-symbolic"
        elif signal_strength >= 60:
            icon_name = "network-wireless-signal-good-symbolic"
        elif signal_strength >= 40:
            icon_name = "network-wireless-signal-ok-symbolic"
        elif signal_strength > 0:
            icon_name = "network-wireless-signal-weak-symbolic"
        else:
            icon_name = "network-wireless-signal-none-symbolic"
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)

        ssid_label = Gtk.Label()
        if self.network_data["in_use"]:
            ssid_label.set_markup("<b>{}</b>".format(self.network_data["ssid"]))
        else:
            ssid_label.set_text(self.network_data["ssid"])
        ssid_label.set_xalign(0)

        security_signal_label = Gtk.Label(
            label="{} • Signal: {}%".format(
                self.network_data["security"], self.network_data["signal"]
            )
        )
        security_signal_label.set_xalign(0)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info_box.pack_start(ssid_label, False, False, 0)
        info_box.pack_start(security_signal_label, False, False, 0)

        container.pack_start(icon, False, False, 0)
        container.pack_start(info_box, True, True, 0)

        if self.network_data["in_use"]:
            connected_icon = Gtk.Image.new_from_icon_name(
                "checkmark-symbolic", Gtk.IconSize.MENU
            )
            container.pack_end(connected_icon, False, False, 0)

        # Enable button press events (needed in GTK3) and connect the event handler.
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_button_press_event)

        # Add the container box to this row.
        self.add(container)
        self.show_all()

    def on_button_press_event(self, widget, event):
        if event.button == 3:  # Right-click detected
            logger.info("Right-click detected:", self.network_data)
        return False


class WifiMenu(Gtk.Box):
    __gsignals__ = {
        "connected": (GObject.SignalFlags.RUN_FIRST, None, (str, )),
        "enabled-status-changed": (GObject.SignalFlags.RUN_FIRST, None, (bool, ))
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_orientation(Gtk.Orientation.VERTICAL)

        header_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        title_label = Gtk.Label()
        title_label.set_markup("<b>wi-fi</b>")
        title_label.set_xalign(0)
        header_hbox.pack_start(title_label, True, True, 0)

        self.enabled_switch = Gtk.Switch()
        self.enabled_switch.connect("notify::active", self.on_switch_toggled)
        header_hbox.pack_end(self.enabled_switch, False, False, 0)
        self.pack_start(header_hbox, False, False, 0)

        status_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.pack_start(status_hbox, False, False, 0)

        self.status_label = Gtk.Label()
        status_hbox.pack_start(self.status_label, False, False, 0)

        self.refresh_btn = Gtk.Button()
        refresh_image = Gtk.Image.new_from_icon_name(
            "refreshstructure-symbolic", Gtk.IconSize.BUTTON
        )
        self.refresh_btn.set_image(refresh_image)
        self.refresh_btn.connect("clicked", self.refresh_wifi)
        status_hbox.pack_end(self.refresh_btn, False, False, 0)

        speeds_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        download_icon = Gtk.Image.new_from_icon_name(
            "go-down-symbolic", Gtk.IconSize.MENU
        )
        self.download_speed_label = Gtk.Label()
        upload_icon = Gtk.Image.new_from_icon_name("go-up-symbolic", Gtk.IconSize.MENU)
        self.upload_speed_label = Gtk.Label()

        speeds_box.pack_start(download_icon, False, False, 0)
        speeds_box.pack_start(self.download_speed_label, True, True, 0)
        speeds_box.pack_start(upload_icon, False, False, 0)
        speeds_box.pack_start(self.upload_speed_label, True, True, 0)
        self.pack_start(speeds_box, False, False, 0)

        self.listbox = Gtk.ListBox()
        self.listbox.set_activate_on_single_click(False)
        self.listbox.connect("row-activated", self.on_listbox_row_activated)
        self.listbox.connect("button-press-event", self.on_listbox_button_press)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self.listbox)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        self.pack_start(scrolled_window, True, True, 0)

        self.task_manager = async_task_manager

        # Store previous rx_bytes and tx_bytes to calculate Mbps
        self.prev_rx_bytes = 0
        self.prev_tx_bytes = 0

        GLib.timeout_add_seconds(1, self.update_speeds)
        self.update_ssid()
        self.update_status()
        self.refresh_wifi()

        self.connect("destroy", self.on_destroy)
        self.show_all()

    def refresh_wifi(self, button=None):
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        spinner = Gtk.Spinner()
        spinner.start()
        self.listbox.add(spinner)
        self.listbox.show_all()


        self.task_manager.run(self._fetch_wifi_list())

    def on_switch_toggled(self, switch, gparam):
        self.task_manager.run(self._set_wifi_power(switch.get_active()))

    async def _fetch_wifi_list(self):
        if hasattr(self, "_is_refreshing") and self._is_refreshing is True:
            logger.info("Not running it back")
            return
        self._is_refreshing = True
        networks = await asyncio.to_thread(get_wifi_networks)
        GLib.idle_add(self.update_listbox_ui, networks)
        self.update_ssid()
        self._is_refreshing = False

    async def _fetch_current_ssid(self):
        ssid = await asyncio.to_thread(fetch_currently_connected_ssid)
        if ssid:
            GLib.idle_add(self.status_label.set_text, f"connected: {ssid}")
            self.emit("connected", ssid)
        else:
            GLib.idle_add(self.status_label.set_text, "not connected")
            self.emit("connected", "")

    async def _get_wifi_speed(self):
        speed = await asyncio.to_thread(get_network_speed)

        rx_bytes = speed["rx_bytes"]
        tx_bytes = speed["tx_bytes"]

        download_speed = 0.0
        upload_speed = 0.0

        if self.prev_rx_bytes > 0 and self.prev_tx_bytes > 0:
            rx_speed = (rx_bytes - self.prev_rx_bytes) / 1024 / 1024
            tx_speed = (tx_bytes - self.prev_tx_bytes) / 1024 / 1024
            download_speed = rx_speed
            upload_speed = tx_speed

        self.prev_rx_bytes = rx_bytes
        self.prev_tx_bytes = tx_bytes

        GLib.idle_add(
            self.download_speed_label.set_text, "{:.2f} Mbps".format(download_speed)
        )
        GLib.idle_add(
            self.upload_speed_label.set_text, "{:.2f} Mbps".format(upload_speed)
        )

    async def _set_wifi_power(self, state: bool):
        GLib.idle_add(
            self.status_label.set_text,
            "disabling wifi..." if not state else "enabling wifi...",
        )
        success = await asyncio.to_thread(set_wifi_power, enabled=state)
        if success:
            self.update_ssid()
            if not state:
                for child in self.listbox.get_children():
                    GLib.idle_add(self.listbox.remove, child)

        self.update_status()



    async def _update_wifi_status(self):
        enabled = await asyncio.to_thread(get_wifi_status)
        GLib.idle_add(self.enabled_switch.set_active, enabled)
        GLib.idle_add(self.emit, "enabled-status-changed", enabled)


    def update_ssid(self):
        self.task_manager.run(self._fetch_current_ssid())

    def update_status(self):
        self.task_manager.run(self._update_wifi_status())

    def update_speeds(self):
        self.task_manager.run(self._get_wifi_speed())
        return True

    def update_listbox_ui(self, networks):
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        for network_data in networks:
            row = WifiNetworkRow(network_data)
            self.listbox.add(row)
        self.listbox.show_all()
        return False

    def on_listbox_row_activated(self, listbox, row):
        if not hasattr(row, "network_data"):
            return

    def on_listbox_button_press(self, listbox, event):
        if event.button == 3:
            if not self.listbox.get_selected_row():
                return
            self.show_context_menu(event)
            return True
        return False

    def show_context_menu(self, event):
        menu = Gtk.Menu()
        connect_item = Gtk.MenuItem(label="connect")
        connect_item.connect("activate", self.connect_wifi)
        menu.append(connect_item)

        disconnect_item = Gtk.MenuItem(label="disconnect")
        disconnect_item.connect("activate", self.disconnect_wifi)
        menu.append(disconnect_item)

        forget_item = Gtk.MenuItem(label="forget")
        forget_item.connect("activate", self.forget_wifi)
        menu.append(forget_item)

        menu.show_all()
        menu.popup_at_pointer(event)

    def connect_wifi(self, widget=None):
        self.task_manager.run(self._connect_wifi())

    def disconnect_wifi(self, widget=None):
        self.task_manager.run(self._disconnect_wifi())

    def forget_wifi(self, widget=None):
        self.task_manager.run(self._forget_wifi())

    async def _connect_wifi(self,):
        selected = self.listbox.get_selected_row()
        ssid = selected.network_data["ssid"]
        GLib.idle_add(self.status_label.set_text, f"Connecting to {ssid}...")
        result = await asyncio.to_thread(connect_network, ssid)

        if result:
            self.update_ssid()
        else:
            # Might just need a password
            password, remember = self._show_password_dialog(selected.network_data)
            logger.info("hi", password, remember)
            result = await asyncio.to_thread(connect_network, ssid=ssid, password=password, remember=remember)
            if result:
                self.update_ssid()
            else:
                GLib.idle_add(self.status_label.set_text, f"Failed to connect to {ssid}")

        await self._fetch_wifi_list()

    async def _disconnect_wifi(self):
        selected = self.listbox.get_selected_row()
        ssid = selected.network_data["ssid"]

        GLib.idle_add(self.status_label.set_text, f"Disconnecting {ssid}...")
        result = await asyncio.to_thread(disconnect_network, ssid)
        if result:
            self.update_ssid()
        else:
            GLib.idle_add(self.status_label.set_text, "Failed to disconnect from {}".format(ssid))
        await self._fetch_wifi_list()

    async def _forget_wifi(self):
        selected = self.listbox.get_selected_row()
        ssid = selected.network_data["ssid"]

        GLib.idle_add(self.status_label.set_text, "Forgetting {}".format(ssid))

        result = await asyncio.to_thread(forget_network, ssid)
        if result:
            self.update_ssid()

        else:
            GLib.idle_add(self.status_label.set_text, "Failed to forget {}".format(ssid))
        await self._fetch_wifi_list()


    def _show_password_dialog(self, network_data):
        """Show password dialog for secured networks"""
        if network_data and network_data["security"].lower() != "none":
            dialog = Gtk.Dialog(
                title=f"Connect to {network_data['ssid']}",
                parent=self.get_toplevel(),
                flags=0,
                buttons=(
                    Gtk.STOCK_CANCEL,
                    Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK,
                    Gtk.ResponseType.OK,
                ),
            )

            box = dialog.get_content_area()
            box.set_spacing(10)
            box.set_margin_start(10)
            box.set_margin_end(10)
            box.set_margin_top(10)
            box.set_margin_bottom(10)

            password_label = Gtk.Label(label="Password:")
            box.add(password_label)

            password_entry = Gtk.Entry()
            password_entry.set_visibility(False)
            password_entry.set_invisible_char("●")
            box.add(password_entry)

            remember_check = Gtk.CheckButton(label="Remember this network")
            remember_check.set_active(True)
            box.add(remember_check)

            dialog.show_all()
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                ret = (password_entry.get_text(), remember_check.get_active())
            else:
                ret = ("", False)

            dialog.destroy()
            return ret
        return ("", False)


    def on_destroy(self, widget):
        logger.info("Bye!")
        del self.task_manager


class NetworksAppWin(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super(NetworksAppWin, self).__init__(**kwargs)
        self.set_default_size(400, 400)
        self.networks_box = WifiMenu()
        self.networks_box.connect("connected", lambda _, s: logger.info(s))
        self.networks_box.connect("enabled-status-changed", lambda _, s: logger.info("enabled {}".format(s)))
        self.add(self.networks_box)
        self.show_all()


def main():
    app = Gtk.Application(application_id="org.example.WifiViewer")
    app.connect("activate", lambda app: NetworksAppWin(application=app).present())
    app.run(None)


if __name__ == "__main__":
    main()