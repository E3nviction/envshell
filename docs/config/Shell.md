# Shell Configuration

- [Go to Home](./Welcome.md)
- [Go back to System Tray Configuration](./Systray.md)

The **Shell** section allows you to configure shell settings/apps.

## Options

Here are the available options for the **Shell** section:

### Shell About window

| Option             | Description                                          | Type     | Default                                  |
| -------------------- | ------------------------------------------------------ | ---------- | ------------------------------------------ |
| `window.width`     | Window width                                         | `Number` | `250`                                    |
| `window.height`    | Window height                                        | `Number` | `355`                                    |
| `window.resizable` | Whether its resizable                                | `Bool`   | `false`                                  |
| `computer-label`   | The Label for the Computer                           | `String` | `Env Shell`                              |
| `computer-caption` | A Caption for the Computer (example: its os version) | `String` | `ESH ?.?.?, 2025`                        |
| `more-info`        | A link to where the button sends you, when pressed   | `String` | `https://github.com/E3nviction/envshell` |

### Shell Menu Options

| Option                      | Description                                                                | Type     | Default                                      |
| ----------------------------- | ---------------------------------------------------------------------------- | ---------- | ---------------------------------------------- |
| `options.settings.on-click` | The command that executes when clicking the settings                       | `String` | `code ~/.config/`                            |
| `options.store.label`       | The Label for the App Store button (example: AUR Store, or Gnome Software) | `String` | `Nix Store...`                               |
| `options.store.on-click`    | The command that executes when pressing the App Store Label                | `String` | `xdg-open https://search.nixos.org/packages` |

## Example

```toml
[Shell]
[Shell.about]
window.width = 250
window.height = 355
window.resizable = false
computer-label = "Env Shell"
computer-caption = "ESH 0.2.0, 2025"
more-info = "https://github.com/E3nviction/envshell"
[Shell.env-menu]
options.settings.on-click = "code ~/.config/"
options.store.label = "Nix Store..."
options.store.on-click = "xdg-open https://search.nixos.org/packages"

```

---

- [Continue with Notch Configuration](./Notch.md)
