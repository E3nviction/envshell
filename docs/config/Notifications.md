# Notifications Configuration

- [Go to Home](./Welcome.md)
- [Go back to Notch Configuration](./Notch.md)

The **Notifications** section allows you to configure the behavior of the notifications.

## Options

Here are the available options for the **Notifications** section:

| Option                     | Description       | Type           | Default               |
|----------------------------|-------------------|----------------|-----------------------|
| `enable`                  | Enable or disable the Notifications          | `Bool`| `true`                |
| `Center.position`                  | The position of the notification Center          | `String["left", "right"]`| `right`                |

## Example

```toml
[Notifications]
enable = true
[Notifications.Center]
position = "right"
```

---

- [Continue with Cache Configuration](./Cache.md)
