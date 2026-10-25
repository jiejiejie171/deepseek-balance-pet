import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from .config import Config
from .secrets_store import SecretStore


@dataclass(frozen=True)
class KeyInfo:
    key: str
    source: str  # custom | env | local

    @property
    def masked(self) -> str:
        return mask_key(self.key)


def mask_key(key: str) -> str:
    key = (key or "").strip()
    if len(key) <= 8:
        return "****"
    return f"{key[:3]}****{key[-4:]}"


def read_local_tool_key(path: Path | None = None) -> str | None:
    settings = Path(path) if path else Path.home() / ".claude" / "settings.json"
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    key = (data.get("env") or {}).get("ANTHROPIC_AUTH_TOKEN")
    return key.strip() if isinstance(key, str) and key.strip() else None


def resolve_key(
    config: Config,
    store: SecretStore,
    env: Mapping[str, str] | None = None,
    local_settings: Path | None = None,
) -> KeyInfo | None:
    env = os.environ if env is None else env
    mode = config.get("key_source", "auto")
    if mode == "claude":
        mode = "local"
    custom = store.get_api_key()
    if mode in ("auto", "custom") and custom:
        return KeyInfo(custom, "custom")
    if mode in ("auto", "env"):
        env_key = (env.get("DEEPSEEK_API_KEY") or "").strip()
        if env_key:
            return KeyInfo(env_key, "env")
    if mode in ("auto", "local"):
        local_key = read_local_tool_key(local_settings)
        if local_key:
            return KeyInfo(local_key, "local")
    return None
