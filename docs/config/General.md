# General Configuration

- [Go to Home](./Welcome.md)

The **General** section provides global settings for envShell, such as including additional configuration files.

## Options

Here are the available options for the **General** section:

| Option                     | Description       | Type           | Default               |
|----------------------------|-------------------|----------------|-----------------------|
| `transparency`             | Will try to remove transparency from the shell, if possible, to optimize performance.          | `Bool`         | `true`                |
| `include`                  | Include additional configuration files from the specified paths.          | `Array[String]`         | `none`                |

## Example

```toml
[General]
transparency = true
include = ["~/.config/envshell/display.toml"]
```

---

- [Continue with Display Configuration](./Display.md)
