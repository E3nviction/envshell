# Panel Configuration

- [Go to Home](./Welcome.md)
- [Go back to Dock Configuration](./Dock.md)

The **Panel** section allows you to configure the top panel, widgets, and date format.

## Options

Here are the available options for the **Panel** section:

| Option                     | Description                                                          | Type                       | Default          |
| ---------------------------- | ---------------------------------------------------------------------- | ---------------------------- | ------------------ |
| `enable`                   | Disable or enable the panel                                          | `Bool`                     | `true`           |
| `height`                   | The Height of the panel                                              | `Number`                   | `24`             |
| `full`                     | Makes the panel have a margin around the edges if false              | `Bool`                     | `true`           |
| `transparent`              | Makes the panel transparent or not                                   | `Bool`                     | `true`           |
| `mode`                     | Determines if the panel expands to the edges or floats in the middle | `String[normal, floating]` | `normal`         |
| `date-format`              | Custom format for the clock on the right side                        | `String`                   | `%a %b %d %H:%M` |
| `icon`                     | A custom nerdfont character as an icon on the left                   | `String`                   | ``             |
| `Panel.Widgets.???.enable` | What widgets of the panel are enabled                                | `Array[Bool]`              | `[true...]`      |

## Example

```toml
enable = true
height = 24
full = true
transparent = true
mode = "normal"
date-format = "%a %b %d %H:%M"
icon = ""
[Panel.Widgets]
left.enable = true
info-menu.enable = true
global-title.enable = true
global-menu.enable = true

right.enable = true
system-tray.enable = true
system-tray.expandable = true
battery.enable = true
wifi.enable = true
bluetooth.enable = true
search.enable = true
control-center.enable = true
date.enable = true

```

---

- [Continue with ScreenFilter Configuration](./ScreenFilter.md)
