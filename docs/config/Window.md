# Window Configuration

- [Go to Home](./Welcome.md)
- [Go back to Display Configuration](./Display.md)

The **Window** section provides Window management settings, including autohide and title translation.

## Options

Here are the available options for the **Window** section:

| Option                     | Description                                                                 | Type           | Default               |
|----------------------------|-----------------------------------------------------------------------------|----------------|-----------------------|
| `autohide.class`           | This will enable a styling class on the panel if one of these classes is active. This has the purpose of a dynamically changing background color of the panel. | `Array[String]`| `none`       |
| `ignore.class`             | Will ignore a window if one of these classes is active.                      | `Array[String]`| `none`       |
| `translate.force-manual`   | Force manual title translation.                                             | `Bool`         | `false`       |
| `translate.smart-title`    | Enable smart title translation.                                             | `Bool`         | `true`       |
| `translate.class`          | This will translate the displayed name of a window if one of these classes is active. | `Array[String]`| `none`       |

## Example

```toml
[Window]
autohide.class."Hyprland" = true
[Window.translate]
smart-title = true
class."None" = "Hyprland"
```

---

- [Continue with Dock Configuration](./Dock.md)
