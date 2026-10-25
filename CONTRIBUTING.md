# Contributing

Thanks for helping improve DeepSeek Balance Pet.

## Ground rules

- This project is **standalone**: it must never require DSH, read `.dsh`, or call `dsh`.
  Reusing a DeepSeek key from another local tool is optional and must keep working when that tool is absent.
- Never log, display in full, or commit an API key. Use `mask_key()` for UI and `redact()`
  for logs.
- Keep the app working on a machine with no DSH, no additional client, and no pre-existing config.

## Development setup

```powershell
cd D:\Projects\deepseek-balance-pet
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check src tests
```

Run from source:

```powershell
python -m deepseek_pet
```

No-console launch:

```powershell
pythonw -m deepseek_pet
```

## Tests

- Unit tests live in `tests/` and use `tmp_path`; they must not call the real balance API.
- DPAPI tests are skipped automatically on non-Windows platforms.
- GUI smoke tests use `QT_QPA_PLATFORM=offscreen`; the real app uses the Windows platform.
- Before opening a PR, run both `pytest` and `ruff check`.

## Building the portable zip

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File packaging/build.ps1
```

The output is `dist/DeepSeekPet-0.2.0-win-x64.zip`.

## Translations

All UI strings live in `src/deepseek_pet/i18n.py`. When adding a string:

1. Add the key to both `zh` and `en`.
2. Run `pytest tests/test_i18n.py`; it asserts the key sets match.
3. Use `Translator.t(key, **kwargs)` from UI code; never hard-code user-facing text.

## Commit style

- Small, focused commits.
- Suggest Conventional Commit prefixes: `feat:`, `fix:`, `docs:`, `test:`, `build:`,
  `chore:`.
- Do not commit `config.json`, `secrets.bin`, logs, `dist/`, or `build/`.

## Reporting bugs

Include:

- Windows version, app version, and whether you ran the exe or source;
- the exact steps to reproduce;
- the sanitized log from `%APPDATA%\DeepSeekPet\pet.log` (remove keys and personal paths);
- whether a proxy or custom API base URL was configured.

Never attach a real API key or an unredacted settings file.
