# DeepSeek 余额桌宠 v0.1.0 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 做一个本地可运行的 Windows 桌宠：小鲸鱼娘气泡里实时显示 DeepSeek 余额，不需要 DSH、不需要 Claude Code，只需一个 DeepSeek API Key。

**Architecture:** PySide6 单进程桌面应用；配置与 Key 存储独立于任何宿主；余额请求在后台线程完成；先用源码运行，再用 PyInstaller 打成免安装目录供试用。

**Tech Stack:** Python 3.12（`D:\PycharmProjects\python312\python.exe`）、PySide6、requests、pytest、ruff、PyInstaller、Pillow（仅生成图标）。

## Global Constraints

- 本版只在 Windows 10/11 上验证；不发布、不推送 GitHub、不创建 Release。
- **不需要 DSH**：不读取 `.dsh`，不调用 `dsh`，不依赖 Claude Code；复用 Claude Code 的 Key 只是可选来源。
- Key 优先级固定为：自定义 Key（DPAPI） > `DEEPSEEK_API_KEY` > `~/.claude/settings.json` 的 `env.ANTHROPIC_AUTH_TOKEN`。
- 任何日志、异常、诊断输出都不得包含完整 Key；界面只显示尾 4 位。
- 配置目录：`%APPDATA%\DeepSeekPet`；存在 `portable.txt` 时改用 `<程序目录>\data`。
- 角色素材来自 `MeteorNOX/DeepSeek-Balance-Whale-Widget`（MIT），必须保留 `THIRD_PARTY_NOTICES.md`。
- 版本号 `0.1.0`，产品名 `DeepSeek Balance Pet` / `DeepSeek 余额桌宠`。
- 默认刷新 60 秒；点击立即刷新；断网保留上次余额。
- 界面中英双语；中文系统默认中文，其余默认英文。

---

### Task 1: 项目脚手架、素材与依赖

**Files:**
- Create: `pyproject.toml`, `.gitignore`, `LICENSE`, `THIRD_PARTY_NOTICES.md`, `CHANGELOG.md`
- Create: `src/deepseek_pet/__init__.py`
- Create: `src/deepseek_pet/assets/DSniang02.png`, `DSniang1.png`
- Create: `scripts/make_icon.py`, `src/deepseek_pet/assets/icon.ico`
- Create: `tests/.gitkeep`

**Interfaces:**
- Produces: `deepseek_pet.__version__ == "0.1.0"`；`src/deepseek_pet/assets/` 下有三张资源图。

- [ ] **Step 1: 建目录并写项目元数据**

```bash
cd /d/Projects/deepseek-balance-pet
mkdir -p src/deepseek_pet/assets scripts tests docs/superpowers/plans
```

`pyproject.toml`：

```toml
[build-system]
requires = ["setuptools>=69"]
build-backend = "setuptools.build_meta"

[project]
name = "deepseek-balance-pet"
version = "0.1.0"
description = "Standalone Windows desktop pet showing DeepSeek API balance (no DSH required)"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
dependencies = ["PySide6>=6.7,<7", "requests>=2.31"]

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.6", "pyinstaller>=6.6", "pillow>=10"]

[project.scripts]
deepseek-pet = "deepseek_pet.__main__:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
deepseek_pet = ["assets/*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"

[tool.ruff]
line-length = 100
target-version = "py310"
```

`.gitignore`：

```gitignore
__pycache__/
*.py[cod]
.venv/
build/
dist/
*.egg-info/
.pytest_cache/
.ruff_cache/
data/
config.json
secrets.bin
*.log
.idea/
.vscode/
```

`LICENSE`：MIT 全文，版权行写 `Copyright (c) 2026 DeepSeek Balance Pet contributors`。

`THIRD_PARTY_NOTICES.md`：写明角色素材来自 `https://github.com/MeteorNOX/DeepSeek-Balance-Whale-Widget`，MIT 许可，并附上原仓库 MIT 全文。

`CHANGELOG.md`：

```markdown
# Changelog

## 0.1.0 - 2026-10-25

- 首个本地试用版：独立 Windows 桌宠，无需 DSH。
- 实时显示 DeepSeek 余额，60 秒刷新，点击立即刷新。
- 支持自定义 Key（DPAPI 加密）、环境变量、可选复用 Claude Code Key。
- 中英双语设置窗口与首次启动向导。
```

`src/deepseek_pet/__init__.py`：

```python
"""DeepSeek Balance Pet - a standalone Windows desktop pet."""

__version__ = "0.1.0"
APP_NAME = "DeepSeekPet"
PROJECT_URL = ""  # 发布后填入 GitHub 仓库地址；为空时界面隐藏链接
```

- [ ] **Step 2: 放入角色素材**

把已下载的三张图复制进 `src/deepseek_pet/assets/`：

```bash
cp "/c/Users/jiejiejie/AppData/Local/Temp/whale-assets/DSniang1.png" src/deepseek_pet/assets/
cp "/c/Users/jiejiejie/AppData/Local/Temp/whale-assets/DSniang02.png" src/deepseek_pet/assets/
```

验证：

```bash
python -I -c "import struct; b=open('src/deepseek_pet/assets/DSniang02.png','rb').read(24); print(struct.unpack('>II', b[16:24]))"
```

Expected: `(1026, 1026)`。

- [ ] **Step 3: 生成 exe/托盘图标**

`scripts/make_icon.py`：

```python
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "deepseek_pet" / "assets" / "DSniang1.png"
DST = ROOT / "src" / "deepseek_pet" / "assets" / "icon.ico"

image = Image.open(SRC).convert("RGBA")
image.save(DST, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print(DST)
```

运行：

```bash
"D:/PycharmProjects/python312/python.exe" scripts/make_icon.py
```

- [ ] **Step 4: 安装依赖并验证导入**

```bash
"D:/PycharmProjects/python312/python.exe" -m pip install -e ".[dev]"
"D:/PycharmProjects/python312/python.exe" -c "import deepseek_pet; print(deepseek_pet.__version__)"
```

Expected: `0.1.0`（会安装 PySide6，首次约 1–3 分钟）。

- [ ] **Step 5: 初始化 git 并提交**

```bash
git init
git config user.name "DeepSeek Pet Dev"
git config user.email "dev@localhost"
git add .
git commit -m "chore: scaffold project, assets, and dependencies"
```

> 发布前改成你自己的 GitHub 用户名/邮箱：`git config user.name/user.email`。

---

### Task 2: 国际化与日志脱敏

**Files:**
- Create: `src/deepseek_pet/i18n.py`
- Create: `src/deepseek_pet/logging_setup.py`
- Test: `tests/test_i18n.py`, `tests/test_redaction.py`

**Interfaces:**
- Produces: `detect_language(locale_name: str | None) -> str`、`Translator(lang).t(key, **kwargs) -> str`。
- Produces: `redact(text: str) -> str`、`setup_logging(log_dir: Path) -> logging.Logger`。

- [ ] **Step 1: 写失败测试**

`tests/test_i18n.py`：

```python
from deepseek_pet.i18n import STRINGS, Translator, detect_language


def test_translation_keys_match():
    assert set(STRINGS["zh"]) == set(STRINGS["en"])


def test_detect_language():
    assert detect_language("zh_CN") == "zh"
    assert detect_language("zh-TW") == "zh"
    assert detect_language("en_US") == "en"
    assert detect_language("ja_JP") == "en"


def test_translator_formats_and_falls_back():
    tr = Translator("zh")
    assert tr.t("status.minutes_ago", n=3) == "3 分钟前更新"
    assert Translator("en").t("app.no_dsh") == "No DSH required · Standalone"
    assert Translator("en").t("missing.key") == "missing.key"
```

`tests/test_redaction.py`：

```python
import logging

from deepseek_pet.logging_setup import RedactingFilter, redact


def test_redact_removes_secret():
    text = "request failed key=sk-abcdefghijklmnop1234"
    cleaned = redact(text)
    assert "abcdefghijklmnop1234" not in cleaned
    assert "sk-" in cleaned


def test_filter_rewrites_record():
    record = logging.LogRecord("x", logging.ERROR, __file__, 1, "bad %s", ("sk-1234567890abcd",), None)
    RedactingFilter().filter(record)
    assert "1234567890abcd" not in record.getMessage()
```

- [ ] **Step 2: 运行确认失败**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_i18n.py tests/test_redaction.py -v
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 i18n**

`src/deepseek_pet/i18n.py`：完整字典（中英 key 必须完全一致）。

```python
import locale
import os

STRINGS: dict[str, dict[str, str]] = {
    "zh": {
        "app.title": "DeepSeek 余额桌宠",
        "app.no_dsh": "无需 DSH · 独立运行",
        "bubble.title": "DeepSeek 余额",
        "bubble.unknown": "—",
        "status.just_now": "刚刚更新",
        "status.seconds_ago": "{n} 秒前更新",
        "status.minutes_ago": "{n} 分钟前更新",
        "status.offline": "离线 · 上次 {time}",
        "status.no_key": "未找到 API Key",
        "status.invalid_key": "Key 无效或无权限",
        "status.rate_limited": "请求过于频繁",
        "status.server_error": "服务异常（HTTP {status}）",
        "status.error": "刷新失败",
        "menu.refresh": "立即刷新",
        "menu.settings": "设置…",
        "menu.size": "大小",
        "menu.size.small": "小",
        "menu.size.medium": "中",
        "menu.size.large": "大",
        "menu.bubble": "显示气泡",
        "menu.startup": "开机自启",
        "menu.hide": "隐藏 1 小时",
        "menu.about": "关于",
        "menu.quit": "退出",
        "tray.show": "显示桌宠",
        "tray.hide": "隐藏桌宠",
        "tab.account": "账户",
        "tab.appearance": "外观",
        "tab.behavior": "行为",
        "tab.about": "关于",
        "key.source": "Key 来源",
        "key.source.auto": "自动（按优先级）",
        "key.source.custom": "自定义 Key",
        "key.source.env": "环境变量 DEEPSEEK_API_KEY",
        "key.source.claude": "Claude Code 配置",
        "key.source.none": "未找到",
        "key.current": "当前使用：{source}（{masked}）",
        "key.placeholder": "粘贴 DeepSeek API Key",
        "key.show": "显示",
        "key.hide": "隐藏",
        "key.test": "测试连接",
        "key.testing": "测试中…",
        "key.test_ok": "连接成功 · 余额 {amount}",
        "key.test_fail": "测试失败：{reason}",
        "key.save": "保存",
        "key.cancel": "取消",
        "key.clear": "清除自定义 Key",
        "key.saved": "已保存",
        "key.cleared": "已清除自定义 Key",
        "appearance.size": "大小",
        "appearance.opacity": "透明度",
        "appearance.bubble": "显示气泡",
        "appearance.animation": "数字滚动动画",
        "appearance.reduce_motion": "减少动态效果",
        "appearance.reset_position": "重置位置",
        "behavior.interval": "刷新间隔（秒）",
        "behavior.startup": "开机自启",
        "behavior.top": "始终置顶",
        "behavior.language": "语言",
        "behavior.language.auto": "自动",
        "behavior.update_check": "检查更新",
        "behavior.advanced": "高级",
        "behavior.timeout": "超时（秒）",
        "behavior.proxy": "代理（留空跟随系统）",
        "behavior.base_url": "API 地址",
        "about.version": "版本 {version}",
        "about.no_dsh": "本程序不需要 DSH，也不读取 .dsh 目录。",
        "about.github": "GitHub 项目页",
        "about.check_update": "检查更新",
        "about.export_log": "导出诊断日志",
        "about.license": "MIT 许可 · 素材来自 MeteorNOX（MIT）",
        "update.available": "发现新版本 {version}：{url}",
        "update.latest": "已是最新版本",
        "update.failed": "检查更新失败",
        "first.title": "欢迎使用 DeepSeek 余额桌宠",
        "first.no_dsh": "无需 DSH，也不需要 Claude Code。只要一个 DeepSeek API Key 就能运行。",
        "first.detected": "检测到可用 Key：{source}（{masked}）",
        "first.use_detected": "使用这个 Key",
        "first.enter_key": "自己填写 Key",
        "first.skip": "先跳过",
        "first.done": "完成",
        "common.on": "开",
        "common.off": "关",
        "common.save": "保存",
        "common.cancel": "取消",
        "common.close": "关闭",
        "common.ok": "确定",
        "common.seconds": "秒",
        "common.minutes": "分钟",
        "error.no_key": "未找到 DeepSeek API Key，请在设置中填写。",
        "error.unauthorized": "Key 无效或没有余额权限。",
        "error.rate_limited": "请求过于频繁，请稍后再试。",
        "error.timeout": "网络超时。",
        "error.network": "网络连接失败。",
        "error.server": "服务异常（HTTP {status}）。",
        "error.invalid_response": "余额接口返回了无法识别的数据。",
        "error.unknown": "未知错误。",
    },
    "en": {
        "app.title": "DeepSeek Balance Pet",
        "app.no_dsh": "No DSH required · Standalone",
        "bubble.title": "DeepSeek Balance",
        "bubble.unknown": "—",
        "status.just_now": "Updated just now",
        "status.seconds_ago": "Updated {n}s ago",
        "status.minutes_ago": "Updated {n}m ago",
        "status.offline": "Offline · last {time}",
        "status.no_key": "No API key found",
        "status.invalid_key": "Invalid key or no permission",
        "status.rate_limited": "Rate limited",
        "status.server_error": "Server error (HTTP {status})",
        "status.error": "Refresh failed",
        "menu.refresh": "Refresh now",
        "menu.settings": "Settings…",
        "menu.size": "Size",
        "menu.size.small": "Small",
        "menu.size.medium": "Medium",
        "menu.size.large": "Large",
        "menu.bubble": "Show bubble",
        "menu.startup": "Start with Windows",
        "menu.hide": "Hide for 1 hour",
        "menu.about": "About",
        "menu.quit": "Quit",
        "tray.show": "Show pet",
        "tray.hide": "Hide pet",
        "tab.account": "Account",
        "tab.appearance": "Appearance",
        "tab.behavior": "Behavior",
        "tab.about": "About",
        "key.source": "Key source",
        "key.source.auto": "Automatic (by priority)",
        "key.source.custom": "Custom key",
        "key.source.env": "Environment variable DEEPSEEK_API_KEY",
        "key.source.claude": "Claude Code settings",
        "key.source.none": "Not found",
        "key.current": "Using: {source} ({masked})",
        "key.placeholder": "Paste a DeepSeek API key",
        "key.show": "Show",
        "key.hide": "Hide",
        "key.test": "Test connection",
        "key.testing": "Testing…",
        "key.test_ok": "Connected · balance {amount}",
        "key.test_fail": "Test failed: {reason}",
        "key.save": "Save",
        "key.cancel": "Cancel",
        "key.clear": "Clear custom key",
        "key.saved": "Saved",
        "key.cleared": "Custom key cleared",
        "appearance.size": "Size",
        "appearance.opacity": "Opacity",
        "appearance.bubble": "Show bubble",
        "appearance.animation": "Number roll animation",
        "appearance.reduce_motion": "Reduce motion",
        "appearance.reset_position": "Reset position",
        "behavior.interval": "Refresh interval (seconds)",
        "behavior.startup": "Start with Windows",
        "behavior.top": "Always on top",
        "behavior.language": "Language",
        "behavior.language.auto": "Automatic",
        "behavior.update_check": "Check for updates",
        "behavior.advanced": "Advanced",
        "behavior.timeout": "Timeout (seconds)",
        "behavior.proxy": "Proxy (empty = system)",
        "behavior.base_url": "API base URL",
        "about.version": "Version {version}",
        "about.no_dsh": "This app does not require DSH and never reads the .dsh directory.",
        "about.github": "GitHub project",
        "about.check_update": "Check for updates",
        "about.export_log": "Export diagnostic log",
        "about.license": "MIT license · artwork by MeteorNOX (MIT)",
        "update.available": "New version {version}: {url}",
        "update.latest": "You are up to date",
        "update.failed": "Update check failed",
        "first.title": "Welcome to DeepSeek Balance Pet",
        "first.no_dsh": "No DSH and no Claude Code required. All you need is a DeepSeek API key.",
        "first.detected": "Detected key: {source} ({masked})",
        "first.use_detected": "Use this key",
        "first.enter_key": "Enter a key",
        "first.skip": "Skip for now",
        "first.done": "Done",
        "common.on": "On",
        "common.off": "Off",
        "common.save": "Save",
        "common.cancel": "Cancel",
        "common.close": "Close",
        "common.ok": "OK",
        "common.seconds": "seconds",
        "common.minutes": "minutes",
        "error.no_key": "No DeepSeek API key found. Please add one in Settings.",
        "error.unauthorized": "The key is invalid or lacks balance permission.",
        "error.rate_limited": "Too many requests. Please try again later.",
        "error.timeout": "Network timeout.",
        "error.network": "Network connection failed.",
        "error.server": "Server error (HTTP {status}).",
        "error.invalid_response": "The balance endpoint returned unexpected data.",
        "error.unknown": "Unknown error.",
    },
}


def detect_language(locale_name: str | None = None) -> str:
    if locale_name is None:
        locale_name = (
            os.environ.get("LANG")
            or locale.getlocale()[0]
            or locale.getdefaultlocale()[0]
            or "en"
        )
    return "zh" if str(locale_name).lower().replace("-", "_").startswith("zh") else "en"


class Translator:
    def __init__(self, lang: str):
        self.lang = lang if lang in STRINGS else "en"

    def t(self, key: str, **kwargs) -> str:
        text = STRINGS.get(self.lang, {}).get(key) or STRINGS["en"].get(key, key)
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
```

- [ ] **Step 4: 实现日志脱敏**

`src/deepseek_pet/logging_setup.py`：

```python
import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

KEY_PATTERN = re.compile(r"sk-[A-Za-z0-9_\-]{8,}")


def redact(text: str) -> str:
    return KEY_PATTERN.sub("sk-••••", str(text))


class RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = ()
        return True


def setup_logging(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("deepseek_pet")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = RotatingFileHandler(
            log_dir / "pet.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        handler.addFilter(RedactingFilter())
        logger.addHandler(handler)
    return logger
```

- [ ] **Step 5: 运行测试并提交**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_i18n.py tests/test_redaction.py -v
git add src/deepseek_pet/i18n.py src/deepseek_pet/logging_setup.py tests/
git commit -m "feat: add bilingual strings and secret redaction"
```

Expected: 全部 PASS。

---

### Task 3: 配置系统

**Files:**
- Create: `src/deepseek_pet/config.py`
- Test: `tests/test_config.py`

**Interfaces:**
- Produces: `Config.load(path=None, portable=None, appdata=None, exe_dir=None) -> Config`
- Produces: `Config.data: dict`、`Config.path: Path`、`Config.get(dotted, default=None)`、`Config.set(dotted, value)`、`Config.save()`、`Config.reset_to_defaults()`
- Produces: `config_dir(portable=None, appdata=None, exe_dir=None) -> Path`、`normalize(data) -> dict`

- [ ] **Step 1: 写失败测试**

`tests/test_config.py`：

```python
import json

from deepseek_pet.config import Config, DEFAULTS, config_dir, normalize


def test_defaults(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    assert cfg.get("refresh_interval_sec") == 60
    assert cfg.get("pet_size") == 360
    assert cfg.get("key_source") == "auto"
    assert cfg.path.exists()


def test_normalize_clamps_and_keeps_unknown():
    data = normalize(
        {
            "refresh_interval_sec": 9999,
            "pet_size": 10,
            "opacity": 9,
            "language": "xx",
            "key_source": "weird",
            "api": {"timeout_sec": 0, "unknown": 1},
            "custom_future_key": "keep-me",
        }
    )
    assert data["refresh_interval_sec"] == 600
    assert data["pet_size"] == 240
    assert data["opacity"] == 1.0
    assert data["language"] == "auto"
    assert data["key_source"] == "auto"
    assert data["api"]["timeout_sec"] == 3
    assert data["api"]["unknown"] == 1
    assert data["custom_future_key"] == "keep-me"


def test_corrupt_file_backed_up(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{not json", encoding="utf-8")
    cfg = Config.load(path=path)
    assert cfg.get("refresh_interval_sec") == 60
    assert (tmp_path / "config.json.bak").exists()


def test_dotted_get_set_and_save(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    cfg.set("position.x", 123)
    cfg.set("api.proxy", "http://127.0.0.1:7897")
    cfg.save()
    again = Config.load(path=tmp_path / "config.json")
    assert again.get("position.x") == 123
    assert again.get("api.proxy") == "http://127.0.0.1:7897"


def test_portable_dir(tmp_path):
    (tmp_path / "portable.txt").write_text("", encoding="utf-8")
    d = config_dir(portable=None, appdata=tmp_path / "appdata", exe_dir=tmp_path)
    assert d == tmp_path / "data"


def test_reset_to_defaults(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    cfg.set("refresh_interval_sec", 30)
    cfg.reset_to_defaults()
    assert cfg.get("refresh_interval_sec") == DEFAULTS["refresh_interval_sec"]
```

- [ ] **Step 2: 运行确认失败**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_config.py -v
```

Expected: FAIL（`deepseek_pet.config` 不存在）。

- [ ] **Step 3: 实现 config.py**

```python
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
    "ui": {"number_animation": True, "reduce_motion": False},
    "update_check": True,
    "first_run_done": False,
    "last_balance": None,
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
    out["language"] = out.get("language") if out.get("language") in ("auto", "zh", "en") else "auto"
    out["refresh_interval_sec"] = _clamp_int(out.get("refresh_interval_sec"), 30, 600, 60)
    out["pet_size"] = _clamp_int(out.get("pet_size"), 240, 600, 360)
    out["opacity"] = _clamp_float(out.get("opacity"), 0.6, 1.0, 1.0)
    out["key_source"] = (
        out.get("key_source") if out.get("key_source") in ("auto", "custom", "env", "claude") else "auto"
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
    out["ui"] = {
        **ui,
        "number_animation": bool(ui.get("number_animation", True)),
        "reduce_motion": bool(ui.get("reduce_motion", False)),
    }
    out["last_balance"] = out.get("last_balance") if isinstance(out.get("last_balance"), dict) else None
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
```

- [ ] **Step 4: 运行测试并提交**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_config.py -v
git add src/deepseek_pet/config.py tests/test_config.py
git commit -m "feat: add validated, portable configuration store"
```

Expected: 6 passed。

---

### Task 4: DPAPI Key 存储与 Key 来源

**Files:**
- Create: `src/deepseek_pet/secrets_store.py`
- Create: `src/deepseek_pet/key_source.py`
- Test: `tests/test_secrets_store.py`, `tests/test_key_source.py`

**Interfaces:**
- Produces: `SecretStore(path).set_api_key(key)`, `.get_api_key() -> str | None`, `.clear()`
- Produces: `KeyInfo(key: str, source: str)`，`KeyInfo.masked` 属性
- Produces: `mask_key(key) -> str`、`read_claude_code_key(path=None) -> str | None`、`resolve_key(config, store, env=None, claude_settings=None) -> KeyInfo | None`

- [ ] **Step 1: 写失败测试**

`tests/test_secrets_store.py`：

```python
import sys

import pytest

from deepseek_pet.secrets_store import SecretStore


@pytest.mark.skipif(sys.platform != "win32", reason="DPAPI is Windows-only")
def test_roundtrip(tmp_path):
    store = SecretStore(tmp_path / "secrets.bin")
    store.set_api_key("sk-test-1234567890")
    assert store.get_api_key() == "sk-test-1234567890"
    assert b"sk-test-1234567890" not in (tmp_path / "secrets.bin").read_bytes()


@pytest.mark.skipif(sys.platform != "win32", reason="DPAPI is Windows-only")
def test_clear(tmp_path):
    store = SecretStore(tmp_path / "secrets.bin")
    store.set_api_key("sk-test-1234567890")
    store.clear()
    assert store.get_api_key() is None


def test_missing_returns_none(tmp_path):
    assert SecretStore(tmp_path / "none.bin").get_api_key() is None
```

`tests/test_key_source.py`：

```python
import json

from deepseek_pet.config import Config
from deepseek_pet.key_source import KeyInfo, mask_key, read_claude_code_key, resolve_key
from deepseek_pet.secrets_store import SecretStore


class FakeStore:
    def __init__(self, key=None):
        self.key = key

    def get_api_key(self):
        return self.key


def make_config(tmp_path, mode="auto"):
    cfg = Config.load(path=tmp_path / "config.json")
    cfg.set("key_source", mode)
    return cfg


def test_mask_key():
    assert mask_key("sk-1234567890abcdef") == "sk-••••cdef"
    assert mask_key("short") == "••••"


def test_read_claude_code_key(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": "sk-claude-1234"}}), encoding="utf-8")
    assert read_claude_code_key(p) == "sk-claude-1234"


def test_priority_custom_over_env_over_claude(tmp_path):
    cfg = make_config(tmp_path)
    env = {"DEEPSEEK_API_KEY": "sk-env-0000"}
    claude = tmp_path / "claude.json"
    claude.write_text(json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": "sk-claude-0000"}}), encoding="utf-8")

    info = resolve_key(cfg, FakeStore("sk-custom-0000"), env=env, claude_settings=claude)
    assert info == KeyInfo("sk-custom-0000", "custom")

    info = resolve_key(cfg, FakeStore(None), env=env, claude_settings=claude)
    assert info.source == "env"

    info = resolve_key(cfg, FakeStore(None), env={}, claude_settings=claude)
    assert info.source == "claude"


def test_forced_source(tmp_path):
    cfg = make_config(tmp_path, "claude")
    env = {"DEEPSEEK_API_KEY": "sk-env-0000"}
    claude = tmp_path / "claude.json"
    claude.write_text(json.dumps({"env": {"ANTHROPIC_AUTH_TOKEN": "sk-claude-0000"}}), encoding="utf-8")
    info = resolve_key(cfg, FakeStore("sk-custom-0000"), env=env, claude_settings=claude)
    assert info.source == "claude"


def test_no_key(tmp_path):
    cfg = make_config(tmp_path)
    assert resolve_key(cfg, FakeStore(None), env={}, claude_settings=tmp_path / "nope.json") is None
```

- [ ] **Step 2: 运行确认失败**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_secrets_store.py tests/test_key_source.py -v
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 secrets_store.py**

```python
import base64
import ctypes
import json
import os
import sys
from ctypes import wintypes
from pathlib import Path

CRYPTPROTECT_UI_FORBIDDEN = 0x01


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def _make_blob(data: bytes):
    buffer = ctypes.create_string_buffer(data, len(data))
    blob = DATA_BLOB(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    return blob, buffer


def _load_libs():
    if sys.platform != "win32":
        raise OSError("Windows DPAPI is required")
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    return crypt32, kernel32


def protect(data: bytes) -> bytes:
    crypt32, kernel32 = _load_libs()
    crypt32.CryptProtectData.argtypes = [
        ctypes.POINTER(DATA_BLOB),
        wintypes.LPCWSTR,
        ctypes.POINTER(DATA_BLOB),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(DATA_BLOB),
    ]
    crypt32.CryptProtectData.restype = wintypes.BOOL
    in_blob, in_buffer = _make_blob(data)
    out_blob = DATA_BLOB()
    ok = crypt32.CryptProtectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(out_blob),
    )
    if not ok:
        raise OSError(ctypes.get_last_error(), "CryptProtectData failed")
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)


def unprotect(data: bytes) -> bytes:
    crypt32, kernel32 = _load_libs()
    crypt32.CryptUnprotectData.argtypes = [
        ctypes.POINTER(DATA_BLOB),
        ctypes.POINTER(wintypes.LPWSTR),
        ctypes.POINTER(DATA_BLOB),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(DATA_BLOB),
    ]
    crypt32.CryptUnprotectData.restype = wintypes.BOOL
    in_blob, in_buffer = _make_blob(data)
    out_blob = DATA_BLOB()
    description = wintypes.LPWSTR()
    ok = crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        ctypes.byref(description),
        None,
        None,
        None,
        CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(out_blob),
    )
    if not ok:
        raise OSError(ctypes.get_last_error(), "CryptUnprotectData failed")
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)
        if description:
            kernel32.LocalFree(description)


class SecretStore:
    def __init__(self, path: Path):
        self.path = Path(path)

    def set_api_key(self, key: str) -> None:
        key = key.strip()
        if not key:
            self.clear()
            return
        payload = {
            "v": 1,
            "blob": base64.b64encode(protect(key.encode("utf-8"))).decode("ascii"),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(payload), encoding="utf-8")
        os.replace(tmp, self.path)

    def get_api_key(self) -> str | None:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return unprotect(base64.b64decode(payload["blob"])).decode("utf-8")
        except Exception:
            return None

    def clear(self) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
```

- [ ] **Step 4: 实现 key_source.py**

```python
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .config import Config
from .secrets_store import SecretStore


@dataclass(frozen=True)
class KeyInfo:
    key: str
    source: str  # custom | env | claude

    @property
    def masked(self) -> str:
        return mask_key(self.key)


def mask_key(key: str) -> str:
    key = (key or "").strip()
    if len(key) <= 8:
        return "••••"
    return f"{key[:3]}••••{key[-4:]}"


def read_claude_code_key(path: Path | None = None) -> str | None:
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
    claude_settings: Path | None = None,
) -> KeyInfo | None:
    env = os.environ if env is None else env
    mode = config.get("key_source", "auto")
    custom = store.get_api_key()
    if mode in ("auto", "custom") and custom:
        return KeyInfo(custom, "custom")
    if mode in ("auto", "env"):
        env_key = (env.get("DEEPSEEK_API_KEY") or "").strip()
        if env_key:
            return KeyInfo(env_key, "env")
    if mode in ("auto", "claude"):
        claude_key = read_claude_code_key(claude_settings)
        if claude_key:
            return KeyInfo(claude_key, "claude")
    return None
```

- [ ] **Step 5: 运行测试并提交**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_secrets_store.py tests/test_key_source.py -v
git add src/deepseek_pet/secrets_store.py src/deepseek_pet/key_source.py tests/
git commit -m "feat: add DPAPI key storage and key source resolution"
```

Expected: DPAPI 测试在本机 PASS；其他平台 skip。

---

### Task 5: 余额客户端与 CLI 自检

**Files:**
- Create: `src/deepseek_pet/balance_client.py`
- Create: `src/deepseek_pet/cli.py`
- Create: `src/deepseek_pet/__main__.py`
- Test: `tests/test_balance_client.py`, `tests/test_cli.py`

**Interfaces:**
- Produces: `Balance(currency, total, granted, topped_up, is_available, infos)`；`format_amount(currency, amount) -> str`
- Produces: `parse_balance(payload) -> Balance`；`fetch_balance(api_key, base_url, timeout, proxy, session=None) -> Balance`
- Produces: `BalanceError(kind, status)`；`run_check(config, store) -> int`；`main(argv=None) -> int`

- [ ] **Step 1: 写失败测试**

`tests/test_balance_client.py`：

```python
from decimal import Decimal

import pytest
import requests

from deepseek_pet.balance_client import (
    BalanceError,
    fetch_balance,
    format_amount,
    parse_balance,
)


def test_parse_prefers_cny():
    payload = {
        "is_available": True,
        "balance_infos": [
            {"currency": "USD", "total_balance": "1.00", "granted_balance": "0", "topped_up_balance": "1.00"},
            {"currency": "CNY", "total_balance": "12.34", "granted_balance": "2.00", "topped_up_balance": "10.34"},
        ],
    }
    balance = parse_balance(payload)
    assert balance.currency == "CNY"
    assert balance.total == Decimal("12.34")
    assert format_amount(balance.currency, balance.total) == "¥12.34"


def test_parse_falls_back_to_first():
    balance = parse_balance({"balance_infos": [{"currency": "USD", "total_balance": "5.5"}]})
    assert balance.currency == "USD"
    assert format_amount("USD", balance.total) == "$5.50"


def test_parse_empty_raises():
    with pytest.raises(BalanceError) as exc:
        parse_balance({"balance_infos": []})
    assert exc.value.kind == "invalid_response"


class FakeResponse:
    def __init__(self, status_code, payload=None, json_error=False):
        self.status_code = status_code
        self.payload = payload
        self.json_error = json_error

    def json(self):
        if self.json_error:
            raise ValueError("not json")
        return self.payload


class FakeSession:
    def __init__(self, response=None, exc=None):
        self.response = response
        self.exc = exc
        self.last_kwargs = None

    def get(self, url, **kwargs):
        self.last_kwargs = kwargs
        if self.exc:
            raise self.exc
        return self.response


def test_fetch_success_and_proxy():
    session = FakeSession(FakeResponse(200, {"balance_infos": [{"currency": "CNY", "total_balance": "8.88"}]}))
    balance = fetch_balance("sk-x", proxy="http://127.0.0.1:7897", session=session)
    assert balance.total == Decimal("8.88")
    assert session.last_kwargs["proxies"]["https"] == "http://127.0.0.1:7897"


@pytest.mark.parametrize(
    ("response", "kind"),
    [
        (FakeResponse(401), "unauthorized"),
        (FakeResponse(429), "rate_limited"),
        (FakeResponse(500), "server"),
    ],
)
def test_fetch_status_errors(response, kind):
    with pytest.raises(BalanceError) as exc:
        fetch_balance("sk-x", session=FakeSession(response))
    assert exc.value.kind == kind


def test_fetch_timeout():
    with pytest.raises(BalanceError) as exc:
        fetch_balance("sk-x", session=FakeSession(exc=requests.Timeout()))
    assert exc.value.kind == "timeout"


def test_fetch_network():
    with pytest.raises(BalanceError) as exc:
        fetch_balance("sk-x", session=FakeSession(exc=requests.ConnectionError()))
    assert exc.value.kind == "network"
```

`tests/test_cli.py`：

```python
from deepseek_pet import cli
from deepseek_pet.balance_client import Balance
from deepseek_pet.config import Config
from deepseek_pet.secrets_store import SecretStore


def test_check_no_key(tmp_path, monkeypatch, capsys):
    cfg = Config.load(path=tmp_path / "config.json")
    store = SecretStore(tmp_path / "secrets.bin")
    monkeypatch.setattr(cli, "resolve_key", lambda *a, **k: None)
    assert cli.run_check(cfg, store) == 2
    assert "API" in capsys.readouterr().out


def test_check_success(tmp_path, monkeypatch, capsys):
    cfg = Config.load(path=tmp_path / "config.json")
    store = SecretStore(tmp_path / "secrets.bin")
    info = type("Info", (), {"key": "sk-test", "source": "custom", "masked": "sk-••••test"})()
    monkeypatch.setattr(cli, "resolve_key", lambda *a, **k: info)
    monkeypatch.setattr(
        cli,
        "fetch_balance",
        lambda *a, **k: Balance("CNY", __import__("decimal").Decimal("1.23"), None, None, True),
    )
    assert cli.run_check(cfg, store) == 0
    assert "CNY" in capsys.readouterr().out
```

- [ ] **Step 2: 运行确认失败**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_balance_client.py tests/test_cli.py -v
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 balance_client.py**

```python
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import requests

SYMBOLS = {"CNY": "¥", "USD": "$"}


@dataclass(frozen=True)
class Balance:
    currency: str
    total: Decimal
    granted: Decimal | None = None
    topped_up: Decimal | None = None
    is_available: bool = True
    infos: tuple[dict, ...] = ()


class BalanceError(Exception):
    def __init__(self, kind: str, status: int | None = None):
        super().__init__(kind)
        self.kind = kind
        self.status = status


def _decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def parse_balance(payload: dict) -> Balance:
    infos = payload.get("balance_infos") if isinstance(payload, dict) else None
    if not isinstance(infos, list) or not infos:
        raise BalanceError("invalid_response")
    chosen = next(
        (item for item in infos if str(item.get("currency", "")).upper() == "CNY"),
        infos[0],
    )
    total = _decimal(chosen.get("total_balance"))
    if total is None:
        raise BalanceError("invalid_response")
    return Balance(
        currency=str(chosen.get("currency") or "CNY").upper(),
        total=total,
        granted=_decimal(chosen.get("granted_balance")),
        topped_up=_decimal(chosen.get("topped_up_balance")),
        is_available=bool(payload.get("is_available", True)),
        infos=tuple(infos),
    )


def format_amount(currency: str, amount: Decimal) -> str:
    symbol = SYMBOLS.get(currency.upper())
    if symbol:
        return f"{symbol}{amount:.2f}"
    return f"{currency.upper()} {amount:.2f}"


def fetch_balance(
    api_key: str,
    base_url: str = "https://api.deepseek.com",
    timeout: int = 10,
    proxy: str | None = None,
    session=None,
) -> Balance:
    client = session or requests.Session()
    url = base_url.rstrip("/") + "/user/balance"
    proxies = {"http": proxy, "https": proxy} if proxy else None
    try:
        response = client.get(
            url,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            timeout=timeout,
            proxies=proxies,
        )
    except requests.Timeout as exc:
        raise BalanceError("timeout") from exc
    except requests.RequestException as exc:
        raise BalanceError("network") from exc

    if response.status_code in (401, 403):
        raise BalanceError("unauthorized", response.status_code)
    if response.status_code == 429:
        raise BalanceError("rate_limited", 429)
    if response.status_code >= 500:
        raise BalanceError("server", response.status_code)
    if response.status_code != 200:
        raise BalanceError("unknown", response.status_code)
    try:
        payload = response.json()
    except ValueError as exc:
        raise BalanceError("invalid_response") from exc
    return parse_balance(payload)
```

- [ ] **Step 4: 实现 cli.py 与 __main__.py**

`cli.py`：

```python
import argparse
import sys
from decimal import Decimal
from pathlib import Path

from . import __version__
from .balance_client import BalanceError, fetch_balance, format_amount
from .config import Config
from .key_source import resolve_key
from .secrets_store import SecretStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deepseek-pet", description="DeepSeek Balance Pet")
    parser.add_argument("--check", action="store_true", help="check key and balance without GUI")
    parser.add_argument("--fake-balance", type=Decimal, default=None, help="run GUI with a fake balance")
    parser.add_argument("--screenshot", type=Path, default=None, help="save a screenshot and exit")
    parser.add_argument("--portable", action="store_true", help="force portable config directory")
    parser.add_argument("--reset-config", action="store_true", help="reset configuration to defaults")
    parser.add_argument("--self-test", action="store_true", help="verify Qt and assets, then exit")
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def run_check(config: Config, store: SecretStore) -> int:
    info = resolve_key(config, store)
    if info is None:
        print("No DeepSeek API key found. Configure one in Settings or set DEEPSEEK_API_KEY.")
        return 2
    api = config.get("api", {})
    try:
        balance = fetch_balance(
            info.key,
            base_url=api.get("base_url", "https://api.deepseek.com"),
            timeout=int(api.get("timeout_sec", 10)),
            proxy=api.get("proxy") or None,
        )
    except BalanceError as exc:
        print(f"Balance check failed: {exc.kind}" + (f" (HTTP {exc.status})" if exc.status else ""))
        return 1
    print(f"source={info.source} key={info.masked} currency={balance.currency} amount={format_amount(balance.currency, balance.total)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = Config.load(portable=True if args.portable else None)
    store = SecretStore(config.path.parent / "secrets.bin")

    if args.reset_config:
        config.reset_to_defaults()
        print(f"Configuration reset: {config.path}")
        return 0

    if args.check:
        return run_check(config, store)

    from .app import run_app

    return run_app(args, config, store)


if __name__ == "__main__":
    sys.exit(main())
```

`__main__.py`：

```python
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

> `app.py` 在 Task 8 实现；在此之前 `--check`、`--self-test` 可独立工作，GUI 相关命令会暂时 ImportError。

- [ ] **Step 5: 运行测试并提交**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_balance_client.py tests/test_cli.py -v
git add src/deepseek_pet/balance_client.py src/deepseek_pet/cli.py src/deepseek_pet/__main__.py tests/
git commit -m "feat: add balance API client and non-GUI check command"
```

Expected: 全部 PASS。

---

### Task 6: 余额后台服务与桌宠窗口

**Files:**
- Create: `src/deepseek_pet/balance_service.py`
- Create: `src/deepseek_pet/ui/__init__.py`
- Create: `src/deepseek_pet/ui/pet_window.py`
- Test: `tests/test_pet_render.py`（纯函数）、`tests/test_pet_window_smoke.py`（offscreen）

**Interfaces:**
- `BalanceService(config, store)`：`refresh()`、信号 `updated(Balance)`、`failed(kind, detail)`。
- `PetWindow(config, translator, service)`：`apply_config()`、`refresh_now()`、`set_pet_size(size)`、`show_menu()`；信号 `settings_requested`、`startup_toggled(bool)`、`hide_requested`、`about_requested`、`quit_requested`。

- [ ] **Step 1: 写失败测试**

`tests/test_pet_render.py`：

```python
from decimal import Decimal

from deepseek_pet.balance_client import Balance, format_amount


def test_amount_format():
    assert format_amount("CNY", Decimal("100.5")) == "¥100.50"
    assert format_amount("USD", Decimal("0")) == "$0.00"
```

`tests/test_pet_window_smoke.py`：

```python
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from deepseek_pet.config import Config
from deepseek_pet.i18n import Translator
from deepseek_pet.ui.pet_window import PetWindow


class FakeService:
    def refresh(self):
        pass


def test_window_builds(tmp_path):
    app = QApplication.instance() or QApplication([])
    cfg = Config.load(path=tmp_path / "config.json")
    window = PetWindow(cfg, Translator("zh"), FakeService())
    assert window.width() == cfg.get("pet_size")
    window.close()
    app.quit()
```

- [ ] **Step 2: 运行确认失败**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_pet_render.py tests/test_pet_window_smoke.py -v
```

Expected: FAIL（`pet_window` 不存在）。

- [ ] **Step 3: 实现 balance_service.py**

```python
import logging

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from .balance_client import Balance, BalanceError, fetch_balance
from .config import Config
from .key_source import resolve_key
from .logging_setup import redact
from .secrets_store import SecretStore

log = logging.getLogger("deepseek_pet")


class _Signals(QObject):
    ok = Signal(object)
    err = Signal(str, str)


class _Worker(QRunnable):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.signals = _Signals()

    def run(self):
        try:
            self.signals.ok.emit(self.func())
        except BalanceError as exc:
            self.signals.err.emit(exc.kind, str(exc.status or ""))
        except Exception as exc:  # noqa: BLE001
            log.exception("unexpected balance error")
            self.signals.err.emit("unknown", redact(str(exc)))


class BalanceService(QObject):
    updated = Signal(object)
    failed = Signal(str, str)

    def __init__(self, config: Config, store: SecretStore, parent=None):
        super().__init__(parent)
        self.config = config
        self.store = store
        self._busy = False

    def refresh(self, fake: Balance | None = None) -> None:
        if fake is not None:
            self.updated.emit(fake)
            return
        if self._busy:
            return
        info = resolve_key(self.config, self.store)
        if info is None:
            self.failed.emit("no_key", "")
            return
        api = self.config.get("api", {})
        self._busy = True
        worker = _Worker(
            lambda: fetch_balance(
                info.key,
                base_url=api.get("base_url", "https://api.deepseek.com"),
                timeout=int(api.get("timeout_sec", 10)),
                proxy=api.get("proxy") or None,
            )
        )
        worker.signals.ok.connect(self._on_ok)
        worker.signals.err.connect(self._on_err)
        QThreadPool.globalInstance().start(worker)

    def _on_ok(self, balance) -> None:
        self._busy = False
        self.updated.emit(balance)

    def _on_err(self, kind: str, detail: str) -> None:
        self._busy = False
        self.failed.emit(kind, detail)
```

- [ ] **Step 4: 实现 pet_window.py**

要点（完整实现按下列行为写）：

- 窗口：`Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool`，`WA_TranslucentBackground`，`WA_ShowWithoutActivating`。
- 读取 `assets/DSniang02.png`；`paintEvent` 按窗口尺寸缩放绘制，`self._bounce` 缩放系数围绕底部中心。
- 气泡矩形：`QRectF(w*0.09, h*0.045, w*0.82, h*0.43)`；三行文字居中：
  - 标题：`bubble.title`
  - 金额：`format_amount(currency, display_total)`；无余额时 `—`
  - 状态：`_status_text()`
- 字体：`Microsoft YaHei UI`；标题约 `w*0.030`、金额约 `w*0.058` 加粗、状态约 `w*0.026`，最小 8–14pt。
- 透明区域：`self.setMask(self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation).mask())`，每次 resize 调用。
- 位置恢复：读 `position.x/y`，若与任一屏幕可用区域相交则恢复，否则主屏右下角 `(right - w - 40, bottom - h - 60)`。
- 拖拽：按下记录全局坐标与窗口偏移；移动超过 4px 视为拖动；释放且未拖动则 `refresh_now()`。
- 右键菜单：刷新、设置…、大小（240/360/500）、显示气泡、开机自启、隐藏 1 小时、关于、退出。
- 定时器：刷新间隔 `refresh_interval_sec`；状态每秒重绘；位置保存 500ms 防抖。
- 余额更新：保存 `last_balance`（含 `currency`、`total`、`timestamp`）；数字用 `QVariantAnimation` 500ms 滚动；`ui.number_animation` 或 `ui.reduce_motion` 关闭时直接切换。
- 错误映射：

```python
STATUS_KEYS = {
    "no_key": "status.no_key",
    "unauthorized": "status.invalid_key",
    "rate_limited": "status.rate_limited",
    "server": "status.server_error",
    "timeout": "status.offline",
    "network": "status.offline",
    "invalid_response": "status.error",
    "unknown": "status.error",
}
```

- `timeout/network` 时状态行参数 `time` = 上次成功时间的 `%H:%M`；没有则 `—`。
- `status.server_error` 参数 `status` 用 `BalanceError.status`。
- `apply_config()`：重新设置大小、透明度、置顶、刷新间隔、气泡开关、位置。
- `closeEvent`：`event.ignore(); self.hide()`（真正退出走菜单/托盘）。

骨架代码：

```python
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from PySide6.QtCore import (
    QAbstractAnimation, QEasingCurve, QPointF, QPropertyAnimation, QRectF, Qt, QTimer,
    QVariantAnimation, Property, Signal,
)
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QWidget

from ..balance_client import Balance, format_amount
from ..config import Config
from ..i18n import Translator

ASSETS = Path(__file__).resolve().parents[1] / "assets"
STATUS_KEYS = { ... }


class PetWindow(QWidget):
    settings_requested = Signal()
    startup_toggled = Signal(bool)
    hide_requested = Signal()
    about_requested = Signal()
    quit_requested = Signal()

    def __init__(self, config: Config, tr: Translator, service, parent=None):
        super().__init__(parent)
        self.config = config
        self.tr = tr
        self.service = service
        self._pixmap = QPixmap(str(ASSETS / "DSniang02.png"))
        self._balance: Balance | None = None
        self._display_total: Decimal | None = None
        self._status_key = "status.no_key"
        self._status_args: dict = {}
        self._last_success_time: datetime | None = None
        self._bounce = 1.0
        self._drag_offset = None
        self._press_pos = None
        self._moved = False

        flags = Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.resize(self.config.get("pet_size", 360), self.config.get("pet_size", 360))
        self.setWindowOpacity(self.config.get("opacity", 1.0))
        self._restore_position()
        self._restore_last_balance()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.service.refresh)
        self._timer.start(int(self.config.get("refresh_interval_sec", 60)) * 1000)
        self._tick = QTimer(self)
        self._tick.timeout.connect(self.update)
        self._tick.start(1000)
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_position)
        self.service.updated.connect(self._on_balance)
        self.service.failed.connect(self._on_error)

    # getter/setter for Property(float) bounceScale, paintEvent, mouse events, menu, etc.
```

实现时补全 `_restore_position`、`_restore_last_balance`、`_save_position`、`paintEvent`、`mousePressEvent`、`mouseMoveEvent`、`mouseReleaseEvent`、`contextMenuEvent`、`_show_menu`、`_on_balance`、`_on_error`、`_animate_to`、`_status_text`、`refresh_now`、`set_pet_size`、`apply_config`、`closeEvent`、`resizeEvent`（更新 mask）。

`refresh_now()` 同时触发一次 Q 弹：

```python
def refresh_now(self) -> None:
    self.service.refresh()
    anim = QPropertyAnimation(self, b"bounceScale", self)
    anim.setDuration(220)
    anim.setStartValue(1.04)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutBack)
    anim.start(QAbstractAnimation.DeleteWhenStopped)
```

- [ ] **Step 5: 运行测试并提交**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_pet_render.py tests/test_pet_window_smoke.py -v
git add src/deepseek_pet/balance_service.py src/deepseek_pet/ui tests/
git commit -m "feat: add background balance service and transparent pet window"
```

Expected: 2 passed（offscreen 下窗口可创建）。

---

### Task 7: 设置窗口

**Files:**
- Create: `src/deepseek_pet/ui/settings_dialog.py`
- Test: `tests/test_settings_logic.py`

**Interfaces:**
- `apply_account(config, store, mode: str, key_text: str) -> None`：保存来源与自定义 Key。
- `SettingsDialog(config, translator, store, on_saved=None)`：`exec()`；保存后发出 `saved` 信号。
- `KeyTestWorker(key, api)`：信号 `ok(Balance)`、`fail(kind, detail)`。

- [ ] **Step 1: 写失败测试**

`tests/test_settings_logic.py`：

```python
from deepseek_pet.config import Config
from deepseek_pet.secrets_store import SecretStore
from deepseek_pet.ui.settings_dialog import apply_account


def test_apply_custom_key(tmp_path, monkeypatch):
    cfg = Config.load(path=tmp_path / "config.json")
    store = SecretStore(tmp_path / "secrets.bin")
    monkeypatch.setattr(store, "set_api_key", lambda key: setattr(store, "key", key))
    monkeypatch.setattr(store, "get_api_key", lambda: getattr(store, "key", None))
    apply_account(cfg, store, "custom", "sk-test-123456")
    assert cfg.get("key_source") == "custom"
    assert store.get_api_key() == "sk-test-123456"


def test_apply_clear_custom_key(tmp_path, monkeypatch):
    cfg = Config.load(path=tmp_path / "config.json")
    cfg.set("key_source", "custom")
    store = SecretStore(tmp_path / "secrets.bin")
    cleared = {"value": False}
    monkeypatch.setattr(store, "clear", lambda: cleared.update(value=True))
    apply_account(cfg, store, "custom", "")
    assert cleared["value"] is True
    assert cfg.get("key_source") == "auto"
```

- [ ] **Step 2: 运行确认失败**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_settings_logic.py -v
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 apply_account 与设置窗口**

`apply_account` 规则：

```python
def apply_account(config, store, mode: str, key_text: str) -> None:
    mode = mode if mode in ("auto", "custom", "env", "claude") else "auto"
    key_text = (key_text or "").strip()
    if mode == "custom":
        if key_text:
            store.set_api_key(key_text)
        if store.get_api_key() is None:
            config.set("key_source", "auto")
        else:
            config.set("key_source", "custom")
    else:
        config.set("key_source", mode)
```

设置窗口结构：

- `QDialog` + `QTabWidget` + 底部 `QDialogButtonBox(Save | Cancel)`。
- 账户页：
  - 只读标签显示 `key.current`（用 `resolve_key` 得到的 source/masked）。
  - `QComboBox`：auto/custom/env/claude。
  - `QLineEdit(Password)` + 显示/隐藏按钮。
  - 「测试连接」按钮；按下后禁用，启动 `KeyTestWorker`；成功/失败更新结果标签。
  - 「清除自定义 Key」按钮：`store.clear()`，结果标签 `key.cleared`。
- 外观页：大小 `QSlider(240..600)`、透明度 `QSlider(60..100)`、显示气泡、数字动画、减少动态、重置位置按钮。
- 行为页：刷新间隔 `QSpinBox(30..600)`、开机自启、始终置顶、语言 `QComboBox(auto/zh/en)`、检查更新；「高级」`QGroupBox` 内放超时、代理、API 地址。
- 关于页：`app.no_dsh`、版本、GitHub 链接（`PROJECT_URL` 为空时隐藏）、检查更新按钮、导出诊断日志、许可证说明。
- 保存时：`apply_account`，把其余控件写回 config，`config.save()`，发出 `saved` 信号，`accept()`。
- 取消：不改动 config（所有改动只在保存时写回）。
- 检查更新：`requests.get("https://api.github.com/repos/<owner>/<repo>/releases/latest")`；`PROJECT_URL` 为空时按钮禁用并显示「未发布」。为了不引入占位符，v0.1.0 直接把该按钮禁用。

- [ ] **Step 4: 运行测试并提交**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_settings_logic.py -v
git add src/deepseek_pet/ui/settings_dialog.py tests/test_settings_logic.py
git commit -m "feat: add settings dialog with key management"
```

Expected: 2 passed。

---

### Task 8: 首次启动向导、托盘与应用装配

**Files:**
- Create: `src/deepseek_pet/ui/first_run.py`
- Create: `src/deepseek_pet/ui/tray.py`
- Create: `src/deepseek_pet/startup.py`
- Create: `src/deepseek_pet/app.py`
- Test: `tests/test_first_run_logic.py`, `tests/test_startup.py`

**Interfaces:**
- `complete_first_run(config, store, mode, key_text) -> None`
- `FirstRunDialog(config, tr, store).exec()`，`accepted` 后配置已保存。
- `make_tray(window, tr, app) -> QSystemTrayIcon`
- `set_startup(enabled: bool) -> None`、`startup_command() -> str`
- `run_app(args, config, store) -> int`

- [ ] **Step 1: 写失败测试**

`tests/test_first_run_logic.py`：

```python
from deepseek_pet.config import Config
from deepseek_pet.secrets_store import SecretStore
from deepseek_pet.ui.first_run import complete_first_run


def test_complete_with_custom_key(tmp_path, monkeypatch):
    cfg = Config.load(path=tmp_path / "config.json")
    store = SecretStore(tmp_path / "secrets.bin")
    monkeypatch.setattr(store, "set_api_key", lambda key: setattr(store, "key", key))
    complete_first_run(cfg, store, "custom", "sk-1234567890")
    assert cfg.get("first_run_done") is True
    assert cfg.get("key_source") == "custom"


def test_complete_skip(tmp_path):
    cfg = Config.load(path=tmp_path / "config.json")
    store = SecretStore(tmp_path / "secrets.bin")
    complete_first_run(cfg, store, "skip", "")
    assert cfg.get("first_run_done") is True
```

`tests/test_startup.py`：

```python
import sys

from deepseek_pet import startup


def test_startup_command_frozen(monkeypatch):
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", r"C:\Apps\DeepSeekPet\DeepSeekPet.exe")
    assert startup.startup_command() == r'"C:\Apps\DeepSeekPet\DeepSeekPet.exe"'


def test_startup_command_source(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "executable", r"D:\Python\python.exe")
    assert startup.startup_command().endswith('-m deepseek_pet"')
```

- [ ] **Step 2: 运行确认失败**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_first_run_logic.py tests/test_startup.py -v
```

Expected: FAIL（模块不存在）。

- [ ] **Step 3: 实现 first_run.py**

规则：

- 第一行大标题 `first.title`，下面醒目标注 `app.no_dsh`。
- 用 `resolve_key` 检测现有 Key，显示 `first.detected`（source 用翻译后的 `key.source.*`，masked 用 `mask_key`）。
- 三个按钮：
  - `first.use_detected`：若检测到来源，`complete_first_run(config, store, source, "")`；这里 source 为 `custom/env/claude`，仅设置 config 的来源，不重复写 Key。
  - `first.enter_key`：校验输入非空，调用 `complete_first_run(config, store, "custom", key_text)`。
  - `first.skip`：`complete_first_run(config, store, "skip", "")`。
- 「测试连接」复用 `KeyTestWorker`，成功显示余额，失败显示脱敏原因。
- `complete_first_run`：

```python
def complete_first_run(config, store, mode: str, key_text: str) -> None:
    if mode == "custom" and key_text.strip():
        store.set_api_key(key_text.strip())
        config.set("key_source", "custom")
    elif mode in ("custom", "env", "claude"):
        config.set("key_source", mode)
    else:
        config.set("key_source", "auto")
    config.set("first_run_done", True)
    config.save()
```

- [ ] **Step 4: 实现 startup.py**

```python
import sys
from pathlib import Path

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "DeepSeekPet"


def startup_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    return f'"{pythonw}" -m deepseek_pet'


def set_startup(enabled: bool) -> None:
    import winreg

    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
        if enabled:
            winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, startup_command())
        else:
            try:
                winreg.DeleteValue(key, VALUE_NAME)
            except FileNotFoundError:
                pass
```

- [ ] **Step 5: 实现 tray.py 与 app.py**

托盘：

- `QSystemTrayIcon(QIcon(DSniang1.png))`。
- 菜单项：显示/隐藏、立即刷新、设置…、退出。
- 左键点击切换显示；双击打开设置。
- 系统不支持托盘时不阻塞启动。

应用装配 `app.py`：

```python
def run_app(args, config: Config, store: SecretStore) -> int:
    app = QApplication(sys.argv[:1])
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("DeepSeekPet")
    logger = setup_logging(config.path.parent)
    lang = config.get("language", "auto")
    if lang == "auto":
        from PySide6.QtCore import QLocale
        lang = detect_language(QLocale.system().name())
    tr = Translator(lang)

    if args.self_test:
        assert (ASSETS / "DSniang02.png").exists()
        return 0

    if not config.get("first_run_done") and args.fake_balance is None and args.screenshot is None:
        FirstRunDialog(config, tr, store).exec()

    service = BalanceService(config, store)
    window = PetWindow(config, tr, service)
    tray = make_tray(window, tr, app)
    tray.show()
    window.settings_requested.connect(lambda: open_settings(config, tr, store, window))
    window.startup_toggled.connect(lambda checked: (set_startup(checked), config.set("startup", checked), config.save()))
    window.hide_requested.connect(lambda: (window.hide(), QTimer.singleShot(3600_000, window.show)))
    window.about_requested.connect(lambda: show_about(tr))
    window.quit_requested.connect(app.quit)

    if args.fake_balance is not None:
        service.refresh(fake=Balance("CNY", args.fake_balance))
    else:
        service.refresh()

    window.show()
    if args.screenshot is not None:
        args.screenshot.parent.mkdir(parents=True, exist_ok=True)
        QTimer.singleShot(800, lambda: (window.grab().save(str(args.screenshot)), app.quit()))
    return app.exec()
```

补充函数：

- `open_settings`：构造 `SettingsDialog`，连接 `saved` 到 `window.apply_config()` 和 `service.refresh`。
- `show_about`：`QMessageBox.about`，内容包含 `app.no_dsh`、版本、`about.license`。
- 单实例：在 `run_app` 开头用 `QLocalServer`；已有实例则发 `show` 并返回 0。名字 `f"DeepSeekPet-{getpass.getuser()}"`。
- `args.screenshot` 时强制 `QT_QPA_PLATFORM=offscreen`（在创建 QApplication 前设置）。

- [ ] **Step 6: 运行测试并提交**

```bash
"D:/PycharmProjects/python312/python.exe" -m pytest tests/test_first_run_logic.py tests/test_startup.py -v
D:/PycharmProjects/python312/python.exe -m deepseek_pet --self-test
git add src/deepseek_pet/ui/first_run.py src/deepseek_pet/ui/tray.py src/deepseek_pet/startup.py src/deepseek_pet/app.py tests/
git commit -m "feat: wire first-run wizard, tray, and desktop app"
```

Expected: 测试 PASS；`--self-test` 退出码 0。

---

### Task 9: 本地打包（PyInstaller）

**Files:**
- Create: `packaging/entry.py`, `packaging/deepseek-pet.spec`, `packaging/build.ps1`
- Create local: `dist/DeepSeekPet/`、`dist/DeepSeekPet-0.1.0-win-x64.zip`

- [ ] **Step 1: 写入口与 spec**

`packaging/entry.py`：

```python
from deepseek_pet.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
```

`packaging/deepseek-pet.spec`：

```python
# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

ROOT = Path(SPECPATH).parent

a = Analysis(
    [str(ROOT / "packaging" / "entry.py")],
    pathex=[str(ROOT / "src")],
    datas=[(str(ROOT / "src" / "deepseek_pet" / "assets"), "deepseek_pet/assets")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DeepSeekPet",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(ROOT / "src" / "deepseek_pet" / "assets" / "icon.ico"),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="DeepSeekPet",
)
```

`packaging/build.ps1`：

```powershell
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Push-Location $root
try {
    & "D:\PycharmProjects\python312\python.exe" -m PyInstaller --noconfirm --clean (Join-Path $PSScriptRoot "deepseek-pet.spec")
    $ver = "0.1.0"
    $dist = Join-Path $root "dist\DeepSeekPet"
    $zip = Join-Path $root "dist\DeepSeekPet-$ver-win-x64.zip"
    if (Test-Path $zip) { Remove-Item $zip }
    Compress-Archive -Path (Join-Path $dist "*") -DestinationPath $zip
    Write-Host "Built: $zip"
} finally {
    Pop-Location
}
```

- [ ] **Step 2: 打包并自检**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File packaging/build.ps1
& "dist\DeepSeekPet\DeepSeekPet.exe" --self-test
```

Expected: `--self-test` 退出码 0；`dist\DeepSeekPet-0.1.0-win-x64.zip` 存在。

- [ ] **Step 3: 生成本地截图**

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
& "dist\DeepSeekPet\DeepSeekPet.exe" --screenshot "docs\screenshots\pet.png" --fake-balance 123.45
Remove-Item Env:\QT_QPA_PLATFORM
```

Expected: `docs/screenshots/pet.png` 存在，能看清鲸鱼与余额。

- [ ] **Step 4: 提交**

```bash
git add packaging/ docs/screenshots/pet.png
git commit -m "build: add PyInstaller packaging for local trial"
```

---

### Task 10: 文档、CI 预置与最终验收

**Files:**
- Create: `README.md`, `README.en.md`, `CONTRIBUTING.md`, `SECURITY.md`
- Create: `docs/configuration.md`, `docs/privacy.md`, `docs/build.md`
- Create: `.github/workflows/ci.yml`, `.github/workflows/release.yml`

- [ ] **Step 1: 写 README（第一屏必须标注无需 DSH）**

`README.md` 开头：

```markdown
# DeepSeek 余额桌宠（DeepSeek Balance Pet）

**无需 DSH · 独立运行** —— 不需要 DSH，不需要 Claude Code，只要一个 DeepSeek API Key。

把一只小鲸鱼娘放到 Windows 桌面右下角，气泡里实时显示你的 DeepSeek 剩余余额。
```

后面包含：截图、功能、安装（本地 exe / 源码）、首次启动、设置、常见问题（401、代理、找不到 Key、SmartScreen）、隐私、致谢、许可证、非官方声明。

`README.en.md` 用同样结构，第一行写 **No DSH required · Standalone**。

- [ ] **Step 2: 写配置/隐私/构建文档**

- `docs/configuration.md`：逐项解释 `config.json` 的字段、默认值、范围、便携模式。
- `docs/privacy.md`：只访问 `api.deepseek.com`；GitHub 更新检查可选；无遥测；Key 用 DPAPI 存储；日志脱敏。
- `docs/build.md`：Python 3.12 + `pip install -e ".[dev]"`、`pytest`、`packaging/build.ps1`。

- [ ] **Step 3: 写 CI 与预置 Release 工作流**

`.github/workflows/ci.yml`：

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -e ".[dev]"
      - run: python -m ruff check src tests
      - run: python -m pytest -q
      - run: python -m deepseek_pet --self-test
```

`.github/workflows/release.yml`（预置，不触发）：

```yaml
name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -e ".[dev]"
      - run: python -m pytest -q
      - run: powershell -NoProfile -ExecutionPolicy Bypass -File packaging/build.ps1
      - run: |
          cd dist
          Get-FileHash DeepSeekPet-0.1.0-win-x64.zip -Algorithm SHA256 |
            ForEach-Object { "$($_.Hash)  DeepSeekPet-0.1.0-win-x64.zip" } |
            Out-File SHA256SUMS.txt -Encoding ascii
        shell: pwsh
      - uses: softprops/action-gh-release@v2
        with:
          files: |
            dist/DeepSeekPet-0.1.0-win-x64.zip
            dist/SHA256SUMS.txt
          body: |
            **No DSH required · Standalone**
            DeepSeek Balance Pet v0.1.0 for Windows x64.
```

> 本版**不推送、不打 tag**，此工作流保持未触发状态。

- [ ] **Step 4: 跑完整验收**

```bash
"D:/PycharmProjects/python312/python.exe" -m ruff check src tests
"D:/PycharmProjects/python312/python.exe" -m pytest -q
"D:/PycharmProjects/python312/python.exe" -m deepseek_pet --self-test
```

Expected: ruff 无错误；pytest 全绿；self-test 退出码 0。

真实 Key 连通性（不会打印完整 Key）：

```bash
"D:/PycharmProjects/python312/python.exe" -m deepseek_pet --check
```

Expected: `source=... key=sk-••••xxxx currency=CNY amount=...`，退出码 0。

- [ ] **Step 5: 启动本地试用版**

```powershell
Start-Process "D:\Projects\deepseek-balance-pet\dist\DeepSeekPet\DeepSeekPet.exe"
```

检查：右下角出现鲸鱼；气泡显示余额；点击刷新；右键设置可改 Key；托盘可退出。

- [ ] **Step 6: 提交**

```bash
git add README.md README.en.md CONTRIBUTING.md SECURITY.md docs/ .github/
git commit -m "docs: add bilingual docs, CI, and prepared release workflow"
```

---

## 自检记录

- 规格覆盖：独立运行/no-DSH（Task 1、8、10）、配置与便携（Task 3）、Key 与 DPAPI（Task 4、7）、余额与错误（Task 5、6）、首次向导/托盘（Task 8）、打包（Task 9）、文档/CI（Task 10）。
- 本版明确不发布：无 `git push`、无 tag、不运行 Release 工作流。
- 类型一致性：`Config.get/set`、`Balance`、`KeyInfo.masked`、`BalanceService.updated/failed`、`PetWindow` 信号在各任务中保持一致。
