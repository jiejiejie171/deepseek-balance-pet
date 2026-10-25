import argparse
import os
import sys
from decimal import Decimal
from pathlib import Path

from . import __version__
from .balance_client import BalanceError, fetch_balance
from .config import Config
from .key_source import resolve_key
from .secrets_store import SecretStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="deepseek-pet", description="DeepSeek Balance Pet")
    parser.add_argument("--check", action="store_true", help="check key and balance without GUI")
    parser.add_argument(
        "--fake-balance", type=Decimal, default=None, help="run GUI with a fake balance"
    )
    parser.add_argument(
        "--screenshot", type=Path, default=None, help="save a screenshot and exit"
    )
    parser.add_argument("--portable", action="store_true", help="force portable config directory")
    parser.add_argument(
        "--reset-config", action="store_true", help="reset configuration to defaults"
    )
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
        suffix = f" (HTTP {exc.status})" if exc.status else ""
        print(f"Balance check failed: {exc.kind}{suffix}")
        return 1
    print(
        f"source={info.source} key={info.masked} currency={balance.currency} "
        f"amount={balance.total:.2f}"
    )
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

    if args.self_test:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from .app import run_app

    return run_app(args, config, store)


if __name__ == "__main__":
    sys.exit(main())
