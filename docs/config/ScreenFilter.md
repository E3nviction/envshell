# ScreenFilter Configuration

- [Go to Home](./Welcome.md)
- [Go back to Panel Configuration](./Panel.md)

The **ScreenFilter** section allows you to configure screen filters like Nightshift and Redshift.

## Options

Here are the available options for the **ScreenFilter** section:

| Option                     | Description                                                                                        | Type             | Default  |
| ---------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------ | ---------- |
| `enable`                   | Enable or disable envLight                                                                         | `Bool`           | `true`   |
| `advanced.update_interval` | How often it will check if it should activate a filter                                             | `Number`         | `10`     |
| `effect`                   | The default effect, that is applied if no other effect is applied                                  | `String`         | `"none"` |
| `ScreenFilter.???effect`   | Options for the specific effect                                                                    | `Options`        | `...`    |
| `ScreenFilter.rules`       | A list of rules that will get checked and evaluated. If they succeed then it will applie an effect | `Array[Options]` | `none`   |

### ScreenFilter Effect Options

| Option        | Description               | Type                  | Default |
| --------------- | --------------------------- | ----------------------- | --------- |
| `brightness`  | Brightness of the effect  | `Number`              | `1`     |
| `temperature` | The Color Temperature     | `Number[1000->10000]` | `10000` |
| `strength`    | The opacity of the effect | `Float[0.1->1]`       | `0.1`   |

### ScreenFilter Rule Options

| Option | Description                                                    | Type                    | Default |
| -------- | ---------------------------------------------------------------- | ------------------------- | --------- |
| `type` | Can be python, or shell. Which is the type of eval it will use | `String[shell, python]` | `none`  |
| `if`   | The Command or python expression that will get run             | `String`                | `none`  |
| `is`   | The value that the output will get compared to                 | `String`                | `none`  |
| `then` | The effect that will get applied                               | `String`                | `none`  |

## Example

```toml
[ScreenFilter]
enable = true
effect = "none"
advanced.update_interval = 10
[ScreenFilter.redshift]
brightness = 1
temperature = 10000
strength = 0.1
[ScreenFilter.nightshift]
brightness = 1
temperature = 10000
strength = 0.1
[[ScreenFilter.rules]]
type = "shell"
if = '[ $(date +"%H") -gt 17 ] && echo "true" || echo "false"'
is = "true"
then = "nightshift"
```

---

- [Continue with EnvLight Configuration](./EnvLight.md)
