import copy
import json
import os
import sys
from pathlib import Path

APP_NAME = "DeepSeekPet"
CONFIG_VERSION = 1
DEFAULTS: dict = {
    "schema_version": CONFIG_VERSION,
    "language": "auto",
    "refresh_interval_sec": 60,
    "pet_size": 360,
    "opacity": 1.0,
    "always_on_top": True,
    "show_bubble": True,
    "position": {"x": None, "y": None},
    "startup": False,
    "key_source": "auto",
    "api": {"base_url": "https://api.deepseek.com", "timeout_sec": 10, "proxy": ""},
    "ui": {
        "number_animation": True,
        "reduce_motion": False,
        "idle_animation": True,
        "bubble_autohide_sec": 10,
        "peak_style": "mini",
        "sound_enabled": True,
    },
    "update_check": True,
    "first_run_done": False,
    "last_balance": None,
    "usage": None,
}


def _clamp_int(value, lo: int, hi: int, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, number))


def _clamp_float(value, lo: float, hi: float, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, number))


def normalize(data: dict | None) -> dict:
    out = copy.deepcopy(data) if isinstance(data, dict) else {}
    for key, value in DEFAULTS.items():
        if key not in out:
            out[key] = copy.deepcopy(value)
    out["schema_version"] = CONFIG_VERSION
    out["language"] = (
        out.get("language") if out.get("language") in ("auto", "zh", "en") else "auto"
    )
    out["refresh_interval_sec"] = _clamp_int(out.get("refresh_interval_sec"), 30, 600, 60)
    out["pet_size"] = _clamp_int(out.get("pet_size"), 240, 600, 360)
    out["opacity"] = _clamp_float(out.get("opacity"), 0.6, 1.0, 1.0)
    out["key_source"] = (
        out.get("key_source")
        if out.get("key_source") in ("auto", "custom", "env", "claude")
        else "auto"
    )
    for flag in ("always_on_top", "show_bubble", "startup", "update_check", "first_run_done"):
        out[flag] = bool(out.get(flag, DEFAULTS[flag]))

    pos = out.get("position") if isinstance(out.get("position"), dict) else {}
    out["position"] = {
        "x": pos.get("x") if isinstance(pos.get("x"), int) else None,
        "y": pos.get("y") if isinstance(pos.get("y"), int) else None,
    }

    api = out.get("api") if isinstance(out.get("api"), dict) else {}
    base_url = str(api.get("base_url") or DEFAULTS["api"]["base_url"]).rstrip("/")
    out["api"] = {
        **api,
        "base_url": base_url,
        "timeout_sec": _clamp_int(api.get("timeout_sec"), 3, 60, 10),
        "proxy": str(api.get("proxy") or ""),
    }

    ui = out.get("ui") if isinstance(out.get("ui"), dict) else {}
    peak_style = ui.get("peak_style")
    out["ui"] = {
        **ui,
        "number_animation": bool(ui.get("number_animation", True)),
        "reduce_motion": bool(ui.get("reduce_motion", False)),
        "idle_animation": bool(ui.get("idle_animation", True)),
        "bubble_autohide_sec": _clamp_int(ui.get("bubble_autohide_sec"), 0, 120, 10),
        "peak_style": (
            peak_style
            if peak_style in ("default", "liangwen", "qiangqiang", "mini")
            else "mini"
        ),
        "sound_enabled": bool(ui.get("sound_enabled", True)),
    }
    out["last_balance"] = (
        out.get("last_balance") if isinstance(out.get("last_balance"), dict) else None
    )
    out["usage"] = out.get("usage") if isinstance(out.get("usage"), dict) else None
    return out


def executable_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def is_portable(exe_dir: Path | None = None) -> bool:
    return ((exe_dir or executable_dir()) / "portable.txt").exists()


def config_dir(
    portable: bool | None = None,
    appdata: Path | None = None,
    exe_dir: Path | None = None,
) -> Path:
    if portable is None:
        portable = is_portable(exe_dir)
    if portable:
        return (exe_dir or executable_dir()) / "data"
    base = appdata or Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
    return base / APP_NAME


class Config:
    def __init__(self, data: dict, path: Path):
        self.data = data
        self.path = path

    @classmethod
    def load(
        cls,
        path: Path | None = None,
        portable: bool | None = None,
        appdata: Path | None = None,
        exe_dir: Path | None = None,
    ) -> "Config":
        resolved = Path(path) if path else config_dir(portable, appdata, exe_dir) / "config.json"
        raw: dict = {}
        if resolved.exists():
            try:
                raw = json.loads(resolved.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                try:
                    resolved.replace(resolved.with_suffix(".json.bak"))
                except OSError:
                    pass
                raw = {}
        config = cls(normalize(raw), resolved)
        if not resolved.exists():
            config.save()
        return config

    def get(self, dotted: str, default=None):
        current = self.data
        for part in dotted.split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def set(self, dotted: str, value) -> None:
        parts = dotted.split(".")
        current = self.data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self.path)

    def reset_to_defaults(self) -> None:
        self.data = normalize(copy.deepcopy(DEFAULTS))
        self.save()
