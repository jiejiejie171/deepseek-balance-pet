# Build and release

## Requirements

- Windows 10/11 x64
- Python 3.12 (tested); 3.10+ should work
- `D:\PycharmProjects\python312\python.exe` is the reference interpreter for this machine

## Setup

```powershell
cd D:\Projects\deepseek-balance-pet
python -m pip install -e ".[dev]"
```

## Checks

```powershell
python -m ruff check src tests
python -m pytest -q
python -m deepseek_pet --self-test
```

## Portable build

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File packaging/build.ps1
```

With an explicit version:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File packaging/build.ps1 -Version 0.2.0
```

Outputs:

- `dist/DeepSeekPet/` — onedir distribution
- `dist/DeepSeekPet-0.2.0-win-x64.zip` — distributable zip

The build uses `packaging/deepseek-pet.spec` and bundles `src/deepseek_pet/assets` inside
the executable directory.

## Smoke test

```powershell
$p = Start-Process -FilePath "dist\DeepSeekPet\DeepSeekPet.exe" -ArgumentList "--self-test" -Wait -PassThru
$p.ExitCode  # expected 0
```

## Release (prepared, not run)

`.github/workflows/release.yml` runs on a `v*` tag. It builds on `windows-latest`, creates
the zip, writes `SHA256SUMS.txt`, and attaches both to a GitHub Release. It is intentionally
dormant until the repository is published.

Before publishing:

1. Set `PROJECT_URL` in `src/deepseek_pet/__init__.py` to the repository URL.
2. Update the version in `pyproject.toml`, `__init__.py`, `CHANGELOG.md`, and the README.
3. Configure the repository's git identity (the local trial commits use a placeholder
   `DeepSeek Pet Dev <dev@localhost>`).
4. Run the full checks and build once more.

## Notes

- The exe is unsigned. Windows SmartScreen may warn on downloaded builds; verify the
  SHA256 from the release page.
- The exe uses `console=False`; `--check` output is not visible in the packaged build.
  Use the source install for CLI checking.
