from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import zipfile

API_RELEASES_LATEST = "https://api.github.com/repos/KanjiVG/kanjivg/releases/latest"


class KanjiVGSourceError(Exception):
    """Raised when fetching or preparing KanjiVG data fails."""


@dataclass(slots=True)
class KanjiVGAssetInfo:
    tag_name: str
    asset_name: str
    download_url: str


class KanjiVGRepository:
    """Downloads and caches KanjiVG release assets outside the repo tree."""

    def __init__(self, app_name: str = "untitled_kanji_learner") -> None:
        cache_home = Path.home() / ".cache"
        self.root = cache_home / app_name / "kanjivg"
        self.root.mkdir(parents=True, exist_ok=True)

    def ensure_ready(self, release_kind: str = "main") -> Path:
        """Ensure local cache exists and return the extracted kanji directory path."""

        if release_kind not in {"main", "all"}:
            raise ValueError("release_kind must be 'main' or 'all'")

        info = self._latest_asset(release_kind)
        release_dir = self.root / info.tag_name
        release_dir.mkdir(parents=True, exist_ok=True)

        zip_path = release_dir / info.asset_name
        extract_dir = release_dir / release_kind
        manifest = release_dir / f"{release_kind}.json"

        if not extract_dir.exists():
            self._download(info.download_url, zip_path)
            self._extract(zip_path, extract_dir)
            manifest.write_text(
                json.dumps(
                    {
                        "tag": info.tag_name,
                        "asset": info.asset_name,
                        "source": info.download_url,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

        kanji_dir = extract_dir / "kanji"
        if not kanji_dir.exists():
            raise KanjiVGSourceError(f"Expected kanji folder missing at {kanji_dir}")

        return kanji_dir

    def _latest_asset(self, release_kind: str) -> KanjiVGAssetInfo:
        req = Request(
            API_RELEASES_LATEST,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "UntitledKanjiLearner"},
        )

        try:
            with urlopen(req, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (URLError, HTTPError, TimeoutError) as exc:
            raise KanjiVGSourceError(f"Failed to query latest KanjiVG release: {exc}") from exc

        tag_name = payload.get("tag_name")
        assets = payload.get("assets", [])

        if not tag_name:
            raise KanjiVGSourceError("GitHub response missing tag_name")

        expected_suffix = f"-{release_kind}.zip"
        for asset in assets:
            name = asset.get("name", "")
            if name.endswith(expected_suffix):
                return KanjiVGAssetInfo(
                    tag_name=tag_name,
                    asset_name=name,
                    download_url=asset["browser_download_url"],
                )

        raise KanjiVGSourceError(
            f"Could not find {release_kind} zip in latest release assets for {tag_name}"
        )

    @staticmethod
    def _download(url: str, destination: Path) -> None:
        req = Request(url, headers={"User-Agent": "UntitledKanjiLearner"})
        with urlopen(req, timeout=60) as response, destination.open("wb") as out:
            out.write(response.read())

    @staticmethod
    def _extract(zip_path: Path, destination: Path) -> None:
        destination.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(destination)
