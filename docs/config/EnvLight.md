# envLight Configuration

- [Go to Home](./Welcome.md)
- [Go back to ScreenFilter Configuration](./ScreenFilter.md)

The **envLight** section allows you to configure the search behavior and manage extensions.

## Options

Here are the available options for the **envLight** section:

| Option                           | Description                                                                                           | Type            | Default                           |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------- | ----------------------------------- |
| `show-executable`                | If it shows you what is used to launch the app with. (example: flatpak, or nautilus)                  | `Bool`          | `true`                            |
| `clear-search-on-toggle`         | Clears the Input if toggled                                                                           | `Bool`          | `true`                            |
| `advanced.executable-max-length` | Max character limit for the executable text                                                           | `Number`        | `50`                              |
| `advanced.full-executable`       | If you want to show the entire command to launch the app with. (example: nautilus --new-window)       | `Bool`          | `true`                            |
| `enabled`                        | All extensions that are enabled                                                                       | `Array[String]` | `none`                            |
| `load-extensions`                | Extension paths that you want to load. This is only useful if you have your extensions in other files | `Array[String]` | `["extension-folder://builtins"]` |

### EnvLight Extension Options

| Option                | Description                                                                                                                                                       | Type                       | Default  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ---------- |
| `name`                | The name of your extension                                                                                                                                        | `String`                   | `none`   |
| `tooltip`             | Text that displays when hovering                                                                                                                                  | `String`                   | `none`   |
| `keyword`             | The text that has to be put in, so the extension can run                                                                                                          | `String`                   | `none`   |
| `type`                | Can be url or command, and it is the type of what to run, so url would open up a browser tab and command is a shell script                                        | `String[url, command]`     | `none`   |
| `description`         | The text that displays below the Title. This can have wildcards like %s and %S to display the user input. and %S will show the url formatted input (url-friendly) | `Array[String]`            | `none`   |
| `command`             | The actual command or url that will be run when clicked                                                                                                           | `String`                   | `none`   |
| `ignore-char-limit`   | This will remove any character limit set by the user                                                                                                              | `Bool`                     | `false`  |
| `wrap-mode`           | What wrap-mode to use for the description. Can be word, char or none                                                                                              | `String[word, char, none]` | `"none"` |
| `description-command` | A command ran everytime the input changes. This can be then accessed inside the description using %c                                                              | `String`                   | `none`   |

## Example

```toml
[EnvLight]
show-executable = true
clear-search-on-toggle = true
advanced.executable-max-length = 50
advanced.full-executable = true
enabled = []
load-extensions = [
  "extension://builtins/wikipedia", # Extensions in your config folder
  "extension://builtins/calculator",
  "extension:///path/to/your/extension", # Absolute path
  "extension-folder://builtins", # to load a folder in the Extensions config folder
]
[EnvLight.extensions.builtins.calculator]
name = "Calculate"
tooltip = "Calculate and Copy to Clipboard."
keyword = "="
type = "command"
ignore-char-limit = true
wrap-mode = "char"
description-command = "python -c 'print(eval(\"%s\"))'"
description = "Copy to clipboard %c"
command = "python -c 'print(eval(\"%s\"))' | wl-copy"
```

---

- [Continue with Workspace Configuration](./Workspace.md)
