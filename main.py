"""Build a DaDb radical archive from the KRADFILE/RADKFILE data.

Downloads the latest ``radkfile`` and ``kradfile`` JSON from
``scriptin/jmdict-simplified`` and repackages them, together with a DaDb
``index.json``, into ``out/krad-radk-dadb.zip`` — the archive DaKanji's
``kradk`` importer reads.

Run locally with ``uv run main.py``; CI runs the same on a schedule and
publishes ``out/krad-radk-dadb.zip`` as ``releases/latest``.
"""

from __future__ import annotations

import io
import json
import urllib.request
import zipfile
from pathlib import Path

GITHUB_USER = "dariyooo"
GITHUB_REPO = "Krad-Radk-DaDb"
UPSTREAM = "scriptin/jmdict-simplified"

OUT_DIR = Path("out")
ARCHIVE_NAME = "krad-radk-dadb.zip"

_BASE = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/latest/download"


def _latest_release() -> dict:
    url = f"https://api.github.com/repos/{UPSTREAM}/releases/latest"
    req = urllib.request.Request(url, headers={"User-Agent": "Krad-Radk-DaDb"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def _asset_url(release: dict, starts_with: str) -> str:
    for asset in release["assets"]:
        name = asset["name"]
        if name.startswith(starts_with) and name.endswith(".json.zip"):
            return asset["browser_download_url"]
    raise SystemExit(f"asset {starts_with}*.json.zip not found in {UPSTREAM} latest release")


def _download_inner_json(url: str) -> bytes:
    """Download a ``*.json.zip`` asset and return the JSON bytes it contains."""
    req = urllib.request.Request(url, headers={"User-Agent": "Krad-Radk-DaDb"})
    with urllib.request.urlopen(req) as resp:
        raw = resp.read()
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        inner = next(n for n in zf.namelist() if n.endswith(".json"))
        return zf.read(inner)


def _index_json(revision: str) -> bytes:
    return json.dumps(
        {
            "title": "Kanji Radicals",
            "revision": revision,
            "isUpdatable": True,
            "indexUrl": f"{_BASE}/index.json",
            "downloadUrl": f"{_BASE}/{ARCHIVE_NAME}",
            "url": f"https://github.com/{UPSTREAM}",
            "author": "EDRDG (KRADFILE/RADKFILE), jmdict-simplified",
            "attribution": "KRADFILE/RADKFILE © EDRDG, CC BY-SA 4.0",
        },
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")


def main() -> None:
    release = _latest_release()
    revision = release["tag_name"]

    radk = _download_inner_json(_asset_url(release, "radkfile"))
    krad = _download_inner_json(_asset_url(release, "kradfile"))

    OUT_DIR.mkdir(exist_ok=True)
    index = _index_json(revision)
    (OUT_DIR / "index.json").write_bytes(index)
    with zipfile.ZipFile(OUT_DIR / ARCHIVE_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.json", index)
        zf.writestr("radkfile.json", radk)
        zf.writestr("kradfile.json", krad)

    print(f"wrote {OUT_DIR / ARCHIVE_NAME} (revision {revision})")


if __name__ == "__main__":
    main()
