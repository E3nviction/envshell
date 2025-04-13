# MusicPlayer Configuration

- [Go to Home](./Welcome.md)
- [Go back to Misc Configuration](./Misc.md)

The **MusicPlayer** section allows you to configure the music player settings.

## Options

Here are the available options for the **MusicPlayer** section:

| Option                | Description                                  | Type   | Default |
| ----------------------- | ---------------------------------------------- | -------- | --------- |
| `ignore.title.regex` | Ignores any players with the title matching the regex | `String` | `none` |

## Example

```toml
[MusicPlayer]
[[MusicPlayer.ignore]]
title.regex = "^spotify$"
```

---

- [Continue with Panel Mods Configuration](./Mods.md)
