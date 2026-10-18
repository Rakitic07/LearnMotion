"""Prepare compact runtime metadata and CDN-served assets for Vercel."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import subjects  # noqa: E402


def main() -> None:
    manifest = Path(subjects.__file__).with_name("_summary_manifest.json")
    manifest.write_text(json.dumps(subjects._build_summaries(), separators=(",", ":")), encoding="utf-8")

    static_source = ROOT / "app" / "static"
    public_static = ROOT / "public" / "static"
    if public_static.exists():
        shutil.rmtree(public_static)
    shutil.copytree(static_source, public_static)


if __name__ == "__main__":
    main()
