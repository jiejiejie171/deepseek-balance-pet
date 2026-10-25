# Privacy

DeepSeek Balance Pet is a local desktop app. It does not have a server, an account system,
or telemetry.

## Network requests

- `GET https://api.deepseek.com/user/balance` with the configured API key, to read the
  balance. This is the only request in normal use.
- If you change `api.base_url` in the settings panel → Advanced → Configure…, the key is
  sent to that host instead. Only do this if you trust the endpoint.
- This release does not contact GitHub; there is no update-check request.

## What is stored locally

| File | Content |
|---|---|
| `%APPDATA%\DeepSeekPet\config.json` | Settings, last balance, window position. No key. |
| `%APPDATA%\DeepSeekPet\secrets.bin` | DPAPI-encrypted custom key. |
| `%APPDATA%\DeepSeekPet\pet.log` | Rotated operational log, redacted. |

The app may read a local tool's user configuration only to optionally reuse an existing
DeepSeek key, and only when the key source is `auto` or `local`. If you do not want this,
set the key source to `custom` or `env`, or leave that tool unconfigured.

## Redaction

Before anything is written to a log, messages are passed through a filter that replaces
`sk-...` patterns with `sk-****`. The diagnostics export copies this already-redacted log.

## Deleting your data

Quit the app, delete the program directory and `%APPDATA%\DeepSeekPet`. If startup was
enabled, also remove the `DeepSeekPet` value under
`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.
