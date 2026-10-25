# DeepSeek Balance Pet

**No DSH required · Standalone** — no DSH, no Claude Code; Windows plus a DeepSeek API key is all you need.

[中文](README.md) · [Configuration](docs/configuration.md) · [Privacy](docs/privacy.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

> ### ⚠️ Disclaimer
>
> - This is an **unofficial personal project**. It is not affiliated with, endorsed by, or
>   associated with DeepSeek, DeepSeek Harness (DSH), or the original artist **MeteorNOX**.
> - Balance and "used today" are observed/estimated locally from the DeepSeek API. They may
>   differ from the official bill and **must not be used for reconciliation, reimbursement,
>   or legal purposes**.
> - You are responsible for your API key, account permissions, and network environment. Any
>   cost, data loss, or damage caused by using this software is your responsibility.
> - The software is provided "AS IS" under the MIT license, without warranty of any kind.
>   See [DISCLAIMER.md](DISCLAIMER.md) for the full text.

> ### 🐋 Original author and artwork credit
>
> The whale-girl artwork and click sound come from **MeteorNOX**'s
> [DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget),
> under the MIT license. This project is an **independent implementation**, not a DSH plugin,
> and does not represent the original author. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

![screenshot](docs/screenshots/pet.png)

## This is not a DSH plugin

This is a **fully standalone Windows application**:

- It does not install, read, or call DSH (`.dsh`, `dsh plugin`).
- It does not require Claude Code; reusing an existing Claude Code key is optional.
- It only needs Windows 10/11 (x64) and a DeepSeek API key.

## Features

- Transparent, always-on-top, draggable whale-girl; remembers its position.
- **Click the pet and the bubble forms over about 0.75 seconds in three stages**: the
  small circle appears first, then the medium circle, then the large bubble grows, and
  the text fades in last. Clicking again only refreshes; the bubble auto-hides after
  **10 seconds** by default.
- A gear button in the top-right opens the original-style compact settings panel; the pet
  stays usable while the panel is open.
- Balance refreshes every 60 seconds in the background and immediately when clicked;
  amount changes animate.
- Today's usage: the bubble bottom shows `Used today ¥x.xx`, accumulated from observed
  balance decreases (top-ups do not erase it); it resets daily in Beijing time.
- Peak state badge: a green square with white `谷` for off-peak, a red square with white
  `峰` for peak, with a rounded time-until-next-switch next to it.
- Peak text style: Default / Liangwen / !?Strong?! / Minimal (谷/峰, default); longer
  styles widen the badge automatically.
- The upstream duck click sound plays **once immediately on mouse down**; an eight-channel
  SDL mixer lets each rapid click play; holding does not loop it.
- Size / opacity sliders preview live and save immediately.
- The character faces the screen center automatically: right on the left half, left on the
  right half.
- Keeps the last balance when offline; the bottom row still shows today's usage with an
  `offline` marker.
- Change, test, and clear the API key from the settings panel.
- Custom keys are encrypted with Windows DPAPI; logs are redacted.
- Chinese and English UI, following the system language.
- Only contacts `https://api.deepseek.com`; no telemetry.

### Bubble, peak hours, and today's usage

- The bubble is hidden by default; click the pet to grow it in over about 0.75 seconds,
  click again to refresh. It auto-hides after 10 seconds by default (configurable; 0 = never).
- The bubble uses the original hand-drawn skin; all text is centered.
- Peak hours: Monday-Friday, **09:00-12:00 and 14:00-18:00 Beijing time**.
- All other times are off-peak, including weekends, adjusted working weekends, and Chinese
  statutory holidays.
- The bubble bottom shows `Used today ¥1.23`, accumulated from observed balance decreases;
  top-ups do not erase it, and it resets daily in Beijing time.
- The rules match the upstream DSH whale widget; the holiday list lives in
  `src/deepseek_pet/peak.py`.

## Before you start

| Item | Required | Notes |
|---|---|---|
| Windows 10/11 x64 | Yes | Both the portable build and source target Windows |
| DeepSeek API key | Yes | Create one at [DeepSeek Platform](https://platform.deepseek.com) → API Keys; stored locally |
| Python 3.10+ | Source only | The portable exe does not need Python; tested with Python 3.12 |
| Proxy (optional) | No | Configure it under settings → Advanced if needed |
| Accurate system clock | Recommended | Peak/off-peak and the daily usage reset use Beijing time |

> No DSH and no Claude Code are required. A DeepSeek API key is the only essential item.

## Quick start

### Option A: portable build (recommended)

1. Download `DeepSeekPet-0.2.0-win-x64.zip` from [Releases](../../releases/latest).
2. Extract it to a **stable folder** (not a temporary or download folder).
3. Run `DeepSeekPet.exe`.
4. The first-run wizard detects available keys:
   - choose "Use this key", or
   - paste your own DeepSeek API key, or
   - skip and configure it later via the gear → Account & API Key → Manage….

After the wizard, the pet appears in the bottom-right corner. **The bubble is hidden by
default; click the pet once to show the balance.**

> The exe is unsigned. Windows SmartScreen may warn about an unknown publisher on first
> download. Verify the source and SHA256, then choose "More info → Run anyway".

### Option B: run from source

Requires Python 3.10+ (tested with Python 3.12):

```powershell
# Use the Clone URL from this repository's Code button
git clone https://github.com/jiejiejie171/deepseek-balance-pet.git
cd deepseek-balance-pet
python -m pip install -e .
python -m deepseek_pet
```

No console window:

```powershell
pythonw -m deepseek_pet
```

Non-GUI check:

```powershell
python -m deepseek_pet --check
```

## First-time configuration

Key priority:

1. Custom key saved in the app (DPAPI-encrypted);
2. `DEEPSEEK_API_KEY` environment variable;
3. Optional Claude Code user setting `env.ANTHROPIC_AUTH_TOKEN` in `~/.claude/settings.json`.

The custom key is stored in `%APPDATA%\DeepSeekPet\secrets.bin`; configuration is in
`%APPDATA%\DeepSeekPet\config.json`. Put a `portable.txt` next to the executable to use
`<app>\data\` instead.

Steps:

1. Start the app and choose or paste a key in the wizard.
2. Click "Test connection" to verify the balance endpoint.
3. Click the pet to verify the bubble.
4. For a proxy or custom API base URL, open settings → Advanced → Configure….
5. To start with Windows, enable "Start with Windows" in the settings panel.

## Settings

Click the **gear** in the top-right (or right-click the pet / tray icon → Settings) to open
the original-style compact panel; changes apply immediately:

- Size / opacity: live preview while dragging.
- Enable bubble, click sound, idle breathing, number animation, reduce motion.
- Bubble auto-hide seconds, peak text style, refresh interval.
- Startup, always-on-top, language (applies after restart).
- Advanced: timeout / proxy / API base URL via Configure….
- Account & API Key: click Manage… to paste/test/clear a custom key.
- Position: reset; click the small version label at the bottom for About.

The panel is **non-modal**: the pet can still be clicked, dragged, and refreshed while it is
open. Close it with ×, the gear button again, or Esc.

![compact settings panel](docs/screenshots/settings.png)

## FAQ

**"No API key found"**: click the gear → Account & API Key → Manage…, paste a DeepSeek API
key, and click "Test connection".

**"Invalid key or no permission"**: check that the key is from the DeepSeek platform and has
not expired; make sure it is not a key from another provider.

**Network timeout**: configure a proxy under the settings panel → Advanced → Configure….

**Why is the balance old?** When the network or API fails, the last successful balance is
kept; the bottom row still shows today's usage with an `offline` marker.

**Why is today's usage ¥0.00?** It starts accumulating from the first successful balance
reading of the day; it increases only when the balance drops. It is not an official bill
and does not include spending before the app started observing.

**Need DSH?** No. This app never reads `.dsh` and never calls `dsh`.

**Logs**: `%APPDATA%\DeepSeekPet\pet.log`, redacted; the full API key is never written.

**No console output from the exe?** The release build is a GUI app (`console=False`); use
the source install for command-line checks.

## Privacy

- Only `https://api.deepseek.com/user/balance` is contacted for balance.
- No telemetry or analytics.
- Keys are stored as DPAPI ciphertext, or remain in their original location.
- Logs redact `sk-...` secrets.

See [docs/privacy.md](docs/privacy.md).

## Disclaimer (summary)

This is an unofficial project, not affiliated with DeepSeek, DSH, or the original author
MeteorNOX. Balance and today's usage are local estimates, not an official bill. You are
responsible for your API key and use of the software. See [DISCLAIMER.md](DISCLAIMER.md).

## Uninstall

1. Right-click the pet → Quit.
2. Delete the app directory.
3. Delete `%APPDATA%\DeepSeekPet` (or the portable `data` directory).
4. If startup was enabled, disable "Start with Windows" in the settings panel, or remove the
   `DeepSeekPet` value under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.

## Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check src tests
powershell -NoProfile -ExecutionPolicy Bypass -File packaging/build.ps1
```

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/build.md](docs/build.md).

## Credits and license

- **Original author / artwork / click sound**: MeteorNOX,
  [DeepSeek-Balance-Whale-Widget](https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget),
  MIT.
- Project code: MIT, see [LICENSE](LICENSE).
- Full notices: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- This is an independent implementation, not a DSH plugin, and does not represent the
  original author or DeepSeek.
