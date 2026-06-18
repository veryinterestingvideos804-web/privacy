import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

import requests

PEXELS_VIDEO_SEARCH = "https://api.pexels.com/videos/search"
PEXELS_IMAGE_SEARCH = "https://api.pexels.com/v1/search"
PIXABAY_VIDEO_SEARCH = "https://pixabay.com/api/videos/"
PIXABAY_IMAGE_SEARCH = "https://pixabay.com/api/"

VIDEO_EXTENSIONS = [".mp4", ".mov", ".avi", ".mkv"]
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]


class AssetsDownloader:
    def __init__(
        self,
        pexels_api_key: Optional[str] = None,
        pixabay_api_key: Optional[str] = None,
        assets_dir: str = "assets",
    ):
        self.pexels_api_key = pexels_api_key or os.getenv("PEXELS_API_KEY")
        self.pixabay_api_key = pixabay_api_key or os.getenv("PIXABAY_API_KEY")
        self.assets_dir = Path(assets_dir)
        self.logger = logging.getLogger("AssetsDownloader")
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        if not self.pexels_api_key and not self.pixabay_api_key:
            self.logger.warning(
                "Brak klucza API dla Pexels i Pixabay. Assety nie będą pobierane automatycznie."
            )

    def download_assets(self, asset_plan: Dict) -> Dict:
        assets = asset_plan.get("assets", [])
        cta_asset = asset_plan.get("cta_asset", {})

        for asset in assets:
            index = int(asset.get("segment_index", 0))
            query = asset.get("search_query", "")
            preferred_type = asset.get("asset_type", "video")
            path = self._download_asset(index, query, preferred_type)
            if path:
                asset["local_path"] = str(path)

        if cta_asset:
            query = cta_asset.get("search_query", "")
            preferred_type = cta_asset.get("asset_type", "video")
            path = self._download_asset("cta", query, preferred_type)
            if path:
                cta_asset["local_path"] = str(path)

        return {"assets": assets, "cta_asset": cta_asset}

    def _download_asset(self, index, query: str, preferred_type: str) -> Optional[Path]:
        if not query:
            self.logger.warning(f"Brak zapytania search_query dla assetu {index}. Pomijam.")
            return None

        query = query.strip()
        self.logger.info(f"Pobieram asset {index} dla zapytania: {query}")
        asset_name = "cta_asset" if str(index).lower() == "cta" else f"segment_{index}"
        file_path = self.assets_dir / f"{asset_name}.mp4"

        if "image" in preferred_type.lower() or "animation" in preferred_type.lower():
            file_path = self.assets_dir / f"{asset_name}.jpg"
            url = self._search_image(query)
        else:
            url = self._search_video(query)

        if not url and "image" not in preferred_type.lower():
            url = self._search_image(query)
            file_path = self.assets_dir / f"{asset_name}.jpg"

        if not url:
            self.logger.warning(f"Nie znaleziono assetu dla zapytania: {query}")
            return None

        return self._download_url(url, file_path)

    def _search_video(self, query: str) -> Optional[str]:
        if self.pexels_api_key:
            url = self._search_pexels_video(query)
            if url:
                return url
        if self.pixabay_api_key:
            return self._search_pixabay_video(query)
        return None

    def _search_image(self, query: str) -> Optional[str]:
        if self.pexels_api_key:
            url = self._search_pexels_image(query)
            if url:
                return url
        if self.pixabay_api_key:
            return self._search_pixabay_image(query)
        return None

    def _search_pexels_video(self, query: str) -> Optional[str]:
        headers = {"Authorization": self.pexels_api_key}
        params = {"query": query, "orientation": "portrait", "per_page": 1}
        response = requests.get(PEXELS_VIDEO_SEARCH, headers=headers, params=params, timeout=20)
        if response.status_code != 200:
            self.logger.warning(f"Pexels video search failed: {response.status_code}")
            return None
        data = response.json()
        videos = data.get("videos", [])
        if not videos:
            return None
        files = videos[0].get("video_files", [])
        if not files:
            return None
        files.sort(key=lambda item: item.get("height", 0))
        return files[-1].get("link")

    def _search_pexels_image(self, query: str) -> Optional[str]:
        headers = {"Authorization": self.pexels_api_key}
        params = {"query": query, "orientation": "portrait", "per_page": 1}
        response = requests.get(PEXELS_IMAGE_SEARCH, headers=headers, params=params, timeout=20)
        if response.status_code != 200:
            self.logger.warning(f"Pexels image search failed: {response.status_code}")
            return None
        data = response.json()
        photos = data.get("photos", [])
        if not photos:
            return None
        return photos[0].get("src", {}).get("large")

    def _search_pixabay_video(self, query: str) -> Optional[str]:
        params = {"key": self.pixabay_api_key, "q": query, "orientation": "vertical", "per_page": 3}
        response = requests.get(PIXABAY_VIDEO_SEARCH, params=params, timeout=20)
        if response.status_code != 200:
            self.logger.warning(f"Pixabay video search failed: {response.status_code}")
            return None
        data = response.json()
        hits = data.get("hits", [])
        if not hits:
            return None
        videos = hits[0].get("videos", {})
        for res in ["medium", "large", "small"]:
            if res in videos:
                return videos[res].get("url")
        return None

    def _search_pixabay_image(self, query: str) -> Optional[str]:
        params = {"key": self.pixabay_api_key, "q": query, "image_type": "photo", "orientation": "vertical", "per_page": 3}
        response = requests.get(PIXABAY_IMAGE_SEARCH, params=params, timeout=20)
        if response.status_code != 200:
            self.logger.warning(f"Pixabay image search failed: {response.status_code}")
            return None
        data = response.json()
        hits = data.get("hits", [])
        if not hits:
            return None
        return hits[0].get("largeImageURL")

    def _download_url(self, url: str, dest_path: Path) -> Optional[Path]:
        try:
            self.logger.info(f"Pobieranie pliku z: {url}")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            with dest_path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            self.logger.info(f"Zapisano asset do {dest_path}")
            return dest_path
        except Exception as e:
            self.logger.warning(f"Nie udało się pobrać URL {url}: {e}")
            return None