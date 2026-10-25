# Configuration reference

Configuration is stored in `%APPDATA%\DeepSeekPet\config.json`.

Portable mode: create an empty `portable.txt` next to `DeepSeekPet.exe` (or in the project
root when running from source). The config then lives in `<app>\data\config.json`.

The file is written atomically. A corrupt file is backed up as `config.json.bak` and the
app starts with defaults.

| Key | Type | Default | Notes |
|---|---|---|---|
| `schema_version` | int | `1` | Internal format version. |
| `language` | string | `auto` | `auto`, `zh`, or `en`. `auto` follows the system locale. |
| `refresh_interval_sec` | int | `60` | Clamped to 30–600 seconds. |
| `pet_size` | int | `360` | Clamped to 240–600 logical pixels. |
| `opacity` | float | `1.0` | Clamped to 0.6–1.0. |
| `always_on_top` | bool | `true` | Keep the pet above normal windows. |
| `show_bubble` | bool | `true` | Master switch for the bubble feature. The bubble itself is hidden until the pet is clicked. |
| `position.x` | int or null | `null` | Restored on startup; reset from Settings. |
| `position.y` | int or null | `null` | Restored on startup; reset from Settings. |
| `startup` | bool | `false` | Adds/removes the `HKCU\...\Run\DeepSeekPet` value. |
| `key_source` | string | `auto` | `auto`, `custom`, `env`, or `local`. |
| `api.base_url` | string | `https://api.deepseek.com` | Advanced; the key is sent to this host. |
| `api.timeout_sec` | int | `10` | Clamped to 3–60 seconds. |
| `api.proxy` | string | `""` | Empty means follow the system proxy. Example: `http://127.0.0.1:7897`. |
| `ui.number_animation` | bool | `true` | Animate balance changes over ~500 ms. |
| `ui.reduce_motion` | bool | `false` | Disable the number animation. |
| `ui.idle_animation` | bool | `true` | Gentle 60 FPS breathing animation. |
| `ui.bubble_autohide_sec` | int | `10` | Auto-hide the bubble after N seconds; `0` means never. Clamped to 0–120. Clicking the pet while the bubble is visible only refreshes and restarts this timer. |
| `ui.peak_style` | string | `mini` | Peak badge text: `default`, `liangwen`, `qiangqiang`, or `mini`. |
| `ui.sound_enabled` | bool | `true` | Play the upstream duck click sound once per click. |
| `update_check` | bool | `true` | Reserved; this release does not contact GitHub. |
| `first_run_done` | bool | `false` | Set after the wizard is completed or skipped. |
| `last_balance` | object or null | `null` | `{currency, total, timestamp}` for offline display. |
| `usage` | object or null | `null` | `{date, spent, last_total}` for today's observed usage. |

## Peak / off-peak

The bubble computes the current DeepSeek pricing window locally; no extra request is
made. The rules match the upstream DSH whale widget:

- Peak: Monday-Friday, 09:00-12:00 and 14:00-18:00 **Beijing time**.
- Off-peak: all other times, including weekends, adjusted working weekends, and Chinese
  statutory holidays.
- Weekend valley applies from 2026-08-23; holiday valley applies from 2026-09-19.
- The 2026 holiday list is in `src/deepseek_pet/peak.py`; update it when the State Council
  publishes the next year's schedule.

The bubble centers a status badge and a rounded time-until-next-switch together: a green
badge with white text for off-peak, or a red badge with white text for peak, followed by
something like `12h55m` (`in 12h55m` in English). It rounds to 5 minutes; under 5 minutes
shows `soon`, over 24 hours shows `in Xd Yh`. No countdown is shown.

`ui.peak_style` selects the badge text; longer text widens the badge automatically:

| Value | Chinese | English |
|---|---|---|
| `default` | 高峰期 / 低谷期 | Peak / Off-peak |
| `liangwen` | 梁文峰 / 梁文谷 | Liangwen Peak / Liangwen Valley |
| `qiangqiang` | !?峰峰?! / !?谷谷?! | !?PEAK?! / !?VALLEY?! |
| `mini` (default) | 峰 / 谷 | P / V |

The character faces the screen center automatically: on the left half it faces right,
on the right half it faces left.

The bubble forms over about 0.75 seconds in three stages: the small circle appears first,
then the medium circle, then the large bubble grows; the text fades in last. Clicking
while it is visible only refreshes it; it does not hide it.

## Today's usage

The bubble bottom shows `Used today ¥x.xx`. A small local ledger (`usage` in the config)
tracks the balance observed on each successful balance request:

- The first observation of a day sets the baseline and starts at `0`.
- A balance decrease adds the difference to today's spend.
- A balance increase (top-up or granted credit) is ignored and only updates the baseline,
  so it does not erase already-recorded usage.
- The day rolls over at Beijing midnight; the next observation starts a fresh total.
- The ledger is persisted, so restarting the app keeps today's total.

This is an observed accumulation, not an official bill; the balance is sampled every
60 seconds (or when the pet is clicked).

## Sound

`Ya1.wav` is the upstream duck press sound. It is played **once immediately on mouse
down**; holding does not loop it. Controlled by `ui.sound_enabled` (settings panel → Click
sound). An eight-channel SDL mixer (pygame) follows the current system output device and
gives each rapid click its own channel, so repeated clicks each play instead of being
swallowed.

Dragging the size or opacity sliders in Settings previews the change live; Cancel
restores the saved values.

## Key sources

1. `custom`: the DPAPI-encrypted key in `secrets.bin`.
2. `env`: `DEEPSEEK_API_KEY` environment variable.
3. `local`: optional user configuration from another local tool (detected automatically).

`auto` tries them in the order above. Selecting `custom`, `env`, or `local` in Settings
restricts the lookup to that source.

## CLI

```text
python -m deepseek_pet --check           # key + balance check, no GUI
python -m deepseek_pet --portable        # force portable config location
python -m deepseek_pet --reset-config    # restore defaults
python -m deepseek_pet --self-test       # verify Qt and bundled assets
python -m deepseek_pet --fake-balance 123.45
python -m deepseek_pet --screenshot out.png --fake-balance 123.45
```

`--check` prints the source, a masked key, the currency, and the amount. It never prints
the full key.
