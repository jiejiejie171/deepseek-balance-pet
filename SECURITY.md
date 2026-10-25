# Security

## Credential storage

- A custom API key is encrypted with Windows DPAPI (`CryptProtectData`) and written to
  `%APPDATA%\DeepSeekPet\secrets.bin`.
- DPAPI ciphertext is bound to the current Windows user; copying the file to another
  machine or user account does not reveal the key.
- The key is never written to `config.json`, logs, or diagnostics.
- The UI only shows the first 3 and last 4 characters (for example `sk-****1a2b`).

## Network

- The app only calls `https://api.deepseek.com/user/balance` to read the balance.
- If a custom API base URL is configured, the key is sent to that host. Only change this
  if you trust the endpoint.
- No telemetry, analytics, crash reporting, or account system.
- This release does not contact GitHub and has no update-check UI.

## Logging

`%APPDATA%\DeepSeekPet\pet.log` is rotated (1 MB × 3) and passes through a redaction
filter that replaces `sk-...` values with `sk-****`.

## Reporting a vulnerability

Do not open a public issue with a real API key or personal data. Report privately to the
repository maintainer once the project is published, including:

- affected version;
- reproduction steps;
- impact;
- a sanitized log snippet if needed.

## User responsibilities

- Keep your DeepSeek API key private.
- Do not run the app with an API base URL or proxy you do not trust.
- Delete `%APPDATA%\DeepSeekPet` when you stop using the app if you want to remove the
  encrypted key and local history.
