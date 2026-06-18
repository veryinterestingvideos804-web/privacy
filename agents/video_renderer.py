import json
import logging
from pathlib import Path
from typing import Dict, Optional

from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)

DEFAULT_RESOLUTION = (1080, 1920)
DEFAULT_FPS = 30
DEFAULT_BG_COLOR = (15, 15, 15)
DEFAULT_TEXT_COLOR = "white"
FONT = "Arial-Bold" if hasattr(TextClip, "font") else None


def load_state(state_path: str) -> Dict:
    path = Path(state_path)
    if not path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku stanu wideo: {state_path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_duration(timeframe: str) -> float:
    if not timeframe:
        return 5.0
    try:
        clean = timeframe.replace("s", "")
        start_str, end_str = clean.split("-")
        return max(0.5, float(end_str) - float(start_str))
    except Exception:
        return 5.0


def find_asset_path(segment_index: int, assets_dir: str) -> Optional[Path]:
    folder = Path(assets_dir)
    if not folder.exists():
        return None

    video_extensions = [".mp4", ".mov", ".avi", ".mkv"]
    image_extensions = [".jpg", ".jpeg", ".png"]

    segment_name = f"segment_{segment_index}"
    for ext in video_extensions + image_extensions:
        candidate = folder / f"{segment_name}{ext}"
        if candidate.exists():
            return candidate

    return None


def find_cta_asset_path(assets_dir: str) -> Optional[Path]:
    folder = Path(assets_dir)
    if not folder.exists():
        return None

    for name in ["cta_asset", "segment_cta"]:
        for ext in [".mp4", ".mov", ".avi", ".mkv", ".jpg", ".jpeg", ".png"]:
            candidate = folder / f"{name}{ext}"
            if candidate.exists():
                return candidate

    return None


def create_text_overlay(text: str, duration: float):
    if not text:
        return None

    try:
        txt_clip = TextClip(
            txt=text,
            fontsize=50,
            color=DEFAULT_TEXT_COLOR,
            font=FONT,
            method="caption",
            size=(DEFAULT_RESOLUTION[0] - 120, None),
        )
        txt_clip = txt_clip.with_duration(duration)
        return txt_clip.with_position(("center", "bottom"))
    except Exception as e:
        return None


def make_base_clip(duration: float) -> ColorClip:
    return ColorClip(size=DEFAULT_RESOLUTION, color=DEFAULT_BG_COLOR, duration=duration)


def load_media_clip(asset_path: Path, duration: float):
    try:
        if asset_path.suffix.lower() in [".mp4", ".mov", ".avi", ".mkv"]:
            source = VideoFileClip(str(asset_path))
            trimmed = source.subclip(0, min(duration, source.duration))
            resized = trimmed.resized(height=DEFAULT_RESOLUTION[1])
            return resized.with_duration(duration)
        elif asset_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            img_clip = ImageClip(str(asset_path))
            resized = img_clip.resized(height=DEFAULT_RESOLUTION[1])
            return resized.with_duration(duration)
        else:
            return make_base_clip(duration)
    except Exception as e:
        return make_base_clip(duration)


class VideoRenderer:
    def __init__(self, state_path: str = "current_video_state.json", assets_dir: str = "assets"):
        self.state_path = state_path
        self.assets_dir = assets_dir
        self.logger = logging.getLogger("VideoRenderer")

    def render(self, output_path: str = "output.mp4", audio_path: Optional[str] = None, force_text_only: bool = False):
        state = load_state(self.state_path)
        timeline = state.get("editing_plan", {}).get("timeline", [])
        cta_asset = state.get("assets", {}).get("cta_asset", {})

        if force_text_only or not timeline:
            return self.render_text_only(output_path)

        clips = []
        for segment in timeline:
            index = int(segment.get("segment_index", len(clips)))
            duration = segment.get("end_time_sec") - segment.get("start_time_sec", 0.0) if segment.get("end_time_sec") is not None else parse_duration(segment.get("timeframe", "0-5s"))
            duration = max(0.5, float(duration))

            asset_path = find_asset_path(index, self.assets_dir)
            if asset_path:
                clip = load_media_clip(asset_path, duration)
            else:
                clip = make_base_clip(duration)

            overlay = create_text_overlay(segment.get("visual", ""), duration)
            if overlay:
                clip = CompositeVideoClip([clip, overlay])

            clips.append(clip)

        if cta_asset:
            cta_clip = self.build_cta_clip(cta_asset)
            clips.append(cta_clip)

        if not clips:
            raise ValueError("Brak segmentów do renderowania. Sprawdź current_video_state.json lub użyj force_text_only.")

        final_clip = concatenate_videoclips(clips, method="compose")
        final_clip = final_clip.with_fps(DEFAULT_FPS)

        if audio_path:
            audio_clip = self._load_audio(audio_path)
            if audio_clip:
                final_clip = final_clip.with_audio(audio_clip)

        self.logger.info(f"Renderowanie wideo do {output_path}")
        final_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac", fps=DEFAULT_FPS)
        return Path(output_path)

    def build_cta_clip(self, cta_asset: Dict):
        duration = 10.0
        asset_path = find_cta_asset_path(self.assets_dir)

        if asset_path:
            clip = load_media_clip(asset_path, duration)
        else:
            clip = make_base_clip(duration)

        overlay_text = cta_asset.get("search_query", "CTA")
        overlay = create_text_overlay(f"CTA: {overlay_text}", duration)
        if overlay:
            clip = CompositeVideoClip([clip, overlay])
        return clip.with_duration(duration)

    def render_text_only(self, output_path: str = "output_text_only.mp4"):
        state = load_state(self.state_path)
        segments = state.get("script", {}).get("segments", [])

        clips = []
        for segment in segments:
            duration = parse_duration(segment.get("timeframe", "0-5s"))
            clip = make_base_clip(duration)
            text = segment.get("narration", "")
            overlay = create_text_overlay(text, duration)
            if overlay:
                clip = CompositeVideoClip([clip, overlay])
            clips.append(clip)

        if not clips:
            raise ValueError("Brak segmentów do renderowania tekstowego.")

        final_clip = concatenate_videoclips(clips, method="compose").with_fps(DEFAULT_FPS)
        self.logger.info(f"Renderowanie tekstowego wideo do {output_path}")
        final_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac", fps=DEFAULT_FPS)
        return Path(output_path)

    def _load_audio(self, audio_path: str):
        audio_file = Path(audio_path)
        if not audio_file.exists():
            self.logger.warning(f"Nie znaleziono pliku audio: {audio_path}. Renderuję bez dźwięku.")
            return None
        return AudioFileClip(str(audio_file))
