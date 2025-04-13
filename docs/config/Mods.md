# Panel Mods Configuration

- [Go to Home](./Welcome.md)
- [Go back to MusicPlayer Configuration](./MusicPlayer.md)

The **Panel Mods** section allows you to add mods for the top panel.

## Options

Here are the available options for the **Panel Mods** section:

| Option                | Description                                  | Type   | Default |
| ----------------------- | ---------------------------------------------- | -------- | --------- |
| `???.icon` | The icon to use for the mod | `String` | `none` |
| `???.icon` | The icon size | `String` | `none` |
| `???.options` | The options for the mod | `Array[Options]` | `none` |

### Mod Options

| Option                | Description                                  | Type   | Default |
| ----------------------- | ---------------------------------------------- | -------- | --------- |
| `???.options.label`    | The Label for the Dropdown Option | `String` | `none` |
| `???.options.on-clicked`    | The Command to execute when clicking the option | `String` | `none` |
| `???.options.divider`    | Whether or not to have an divider below the option (Tip: only have a divider option and it will only render a divider) | `Bool` | `false` |

## Example

```toml
[Mods]
terminal.icon = "/run/current-system/sw/share/icons/WhiteSur-dark/apps/symbolic/terminal-app-symbolic.svg"
terminal.icon-size = 18
[[Mods.terminal.options]]
label = "Terminal"
on-clicked = "kitty"
[[Mods.terminal.options]]
label = "Terminal but scary"
on-clicked = "ghostty"
divider = true
```

---

- [Go back to Welcome](./Welcome.md)
