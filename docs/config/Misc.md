# Misc Configuration

- [Go to Home](./Welcome.md)
- [Go back to Bluetooth Configuration](./Bluetooth.md)

The **Misc** section allows you to configure miscellaneous settings, and joke features.

## Options

Here are the available options for the **Misc** section:

| Option                | Description                                  | Type   | Default |
| ----------------------- | ---------------------------------------------- | -------- | --------- |
| `activate-linux.enable` | Whether or not to enable the activate-linux overlay, like windows's paywall | `Bool` | `false` |
| `activate-linux.layer` | The layer to use for the activate-linux overlay | `String[background, bottom, top, overlay]` | `overlay` |

## Example

```toml
[Misc]
activate-linux.enable = false
activate-linux.layer = "overlay"
```

---

- [Continue with MusicPlayer Configuration](./MusicPlayer.md)
