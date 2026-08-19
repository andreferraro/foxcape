"""Run graphify label with .env loaded and OpenAI backend forced."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    _load_dotenv(root / ".env")

    # Gemini wins auto-detect over OpenAI; drop Google keys for this command.
    os.environ.pop("GOOGLE_API_KEY", None)
    os.environ.pop("GEMINI_API_KEY", None)

    cmd = [
        sys.executable,
        "-m",
        "graphify",
        "label",
        ".",
        "--backend=openai",
    ]
    model = os.environ.get("OPENAI_MODEL")
    if model:
        cmd.append(f"--model={model}")

    return subprocess.call(cmd, cwd=root)


if __name__ == "__main__":
    raise SystemExit(main())
