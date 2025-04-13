# Dock Configuration

- [Go to Home](./Welcome.md)
- [Go back to Window Configuration](./Window.md)

The **Dock** section allows you to configure the appearance and behavior of the dock.

## Options

Here are the available options for the **Dock** section:

| Option              | Description                                                                              | Type                          | Default              |
| --------------------- | ------------------------------------------------------------------------------------------ | ------------------------------- | ---------------------- |
| `enable`            | Disable or enable the dock                                                               | `Bool`                        | `true`               |
| `legacy`            | Will toggle the Legacy dock system                                                       | `Bool`                        | `true`               |
| `magnification`     | [Not Implemented]                                                                        | `Bool`                        | `true`               |
| `title.limit`       | Lenght of the app title in a dock                                                        | `Number`                      | `25`                 |
| `exclusive`         | Make the dock push away windows                                                          | `Bool`                        | `false`              |
| `lazy-time`         | How long it takes the dock to disappear (not implemented for legacy dock)                | `Number`                      | `1000`               |
| `autohide`          | Makes the dock Hide, when not hovered                                                    | Bool`                         | `true`               |
| `show-on-workspace` | Makes the dock show on an empty workspace                                                | `Bool`                        | `true`               |
| `mode`              | If mode is "full", then it will expand to edges                                          | `String[center, full]`        | `center`             |
| `size`              | Icon size of the dock                                                                    | `Float[0.1->3.0]`             | `1`                  |
| `position`          | The position of the dock, on the screen                                                  | `String[left, right, bottom]` | `bottom`             |
| `debug`             | Shows the Hotspot of the dock (not implemented for legacy dock)                          | `Bool`                        | `false`              |
| `Dock.pinned`       | A dictionary of all pinned apps, first value is the icon name, and second is the command | `Dict[str, str]`              | `nautilus and kitty` |

## Example

```toml
[Dock]
enable = true
legacy = true
magnification = true
title.limit = 25
exclusive = false
lazy-time = 1000
autohide = true
show-on-workspace = true
mode = "center"
size = 1
position = "bottom"
debug = false
[Dock.pinned]
"org.gnome.Nautilus" = "nautilus"
"kitty" = "kitty"

```

---

- [Continue with Panel Configuration](./Panel.md)
