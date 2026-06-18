import json
from pathlib import Path
from typing import Dict, Optional

from moviepy.editor import (
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


def load_video_state(state_path: str = "current_video_state.json") -> Dict:
    path = Path(state_path)
    if not path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku stanu wideo: {state_path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_asset_path(segment_index: int, assets_dir: str = "assets") -> Optional[Path]:
    folder = Path(assets_dir)
    if not folder.exists():
        return None

    pattern = f"segment_{segment_index}.*"
    candidates = [p for p in folder.glob(pattern) if p.suffix.lower() in [".mp4", ".mov", ".avi", ".mkv", ".jpg", ".jpeg", ".png"]]
    return candidates[0] if candidates else None


def find_cta_asset_path(assets_dir: str = "assets") -> Optional[Path]:
    folder = Path(assets_dir)
    if not folder.exists():
        return None

    pattern = "cta_asset.*"
    candidates = [p for p in folder.glob(pattern) if p.suffix.lower() in [".mp4", ".mov", ".avi", ".mkv", ".jpg", ".jpeg", ".png"]]
    return candidates[0] if candidates else None


def build_segment_clip(segment: Dict, index: int, assets_dir: str = "assets"):
    start = segment.get("start_time_sec", 0.0)
    end = segment.get("end_time_sec", start + 5.0)
    duration = max(0.5, end - start)
    asset_path = find_asset_path(index, assets_dir)

    if asset_path and asset_path.suffix.lower() in [".mp4", ".mov", ".avi", ".mkv"]:
        clip = VideoFileClip(str(asset_path)).subclip(0, min(duration, VideoFileClip(str(asset_path)).duration))
        clip = clip.resize(height=DEFAULT_RESOLUTION[1]).set_duration(duration)
    elif asset_path and asset_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        clip = ImageClip(str(asset_path)).set_duration(duration).resize(height=DEFAULT_RESOLUTION[1])
    else:
        clip = ColorClip(size=DEFAULT_RESOLUTION, color=DEFAULT_BG_COLOR, duration=duration)

    text = segment.get("visual", "")
    if text:
        txt_clip = TextClip(
            txt=text,
            fontsize=48,
            color=DEFAULT_TEXT_COLOR,
            font=FONT,
            method="caption",
            size=(DEFAULT_RESOLUTION[0] - 120, None),
        ).set_duration(duration)
        txt_clip = txt_clip.set_position(("center", "bottom")).margin(bottom=80, opacity=0)
        clip = CompositeVideoClip([clip, txt_clip])

    return clip.set_duration(duration)


def build_cta_clip(cta_asset: Dict, assets_dir: str = "assets"):
    duration = 10.0
    asset_path = find_cta_asset_path(assets_dir)

    if asset_path and asset_path.suffix.lower() in [".mp4", ".mov", ".avi", ".mkv"]:
        clip = VideoFileClip(str(asset_path)).subclip(0, min(duration, VideoFileClip(str(asset_path)).duration))
        clip = clip.resize(height=DEFAULT_RESOLUTION[1]).set_duration(duration)
    elif asset_path and asset_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
        clip = ImageClip(str(asset_path)).set_duration(duration).resize(height=DEFAULT_RESOLUTION[1])
    else:
        clip = ColorClip(size=DEFAULT_RESOLUTION, color=DEFAULT_BG_COLOR, duration=duration)

    text = cta_asset.get("search_query", "CTA")
    txt_clip = TextClip(
        txt=f"CTA: {text}",
        fontsize=52,
        color=DEFAULT_TEXT_COLOR,
        font=FONT,
        method="caption",
        size=(DEFAULT_RESOLUTION[0] - 120, None),
    ).set_duration(duration)
    txt_clip = txt_clip.set_position(("center", "center")).margin(bottom=80, opacity=0)
    return CompositeVideoClip([clip, txt_clip]).set_duration(duration)


def build_audio_clip(audio_path: Optional[str] = None):
    if not audio_path:
        return None

    audio_file = Path(audio_path)
    if not audio_file.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku audio: {audio_path}")

    return AudioFileClip(str(audio_file))


def render_video_from_state(
    state_path: str = "current_video_state.json",
    output_path: str = "output.mp4",
    assets_dir: str = "assets",
    audio_path: Optional[str] = None,
    fps: int = DEFAULT_FPS,
):
    state = load_video_state(state_path)
    timeline = state.get("editing_plan", {}).get("timeline", [])
    cta_asset = state.get("assets", {}).get("cta_asset", {})

    clips = []
    for segment in timeline:
        segment_index = int(segment.get("segment_index", len(clips)))
        clip = build_segment_clip(segment, segment_index, assets_dir=assets_dir)
        clips.append(clip)

    if cta_asset:
        clips.append(build_cta_clip(cta_asset, assets_dir=assets_dir))

    if not clips:
        raise ValueError("Brak segmentów w planie montażowym. Sprawdź current_video_state.json")

    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip = final_clip.set_fps(fps)

    if audio_path:
        audio_clip = build_audio_clip(audio_path)
        if audio_clip:
            final_clip = final_clip.set_audio(audio_clip)

    final_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac", fps=fps)
    return Path(output_path)


def render_text_only_video(
    state_path: str = "current_video_state.json",
    output_path: str = "output_text_only.mp4",
    fps: int = DEFAULT_FPS,
):
    state = load_video_state(state_path)
    script = state.get("script", {})
    segments = script.get("segments", [])

    clips = []
    for idx, segment in enumerate(segments):
        duration = max(0.5, float(segment.get("timeframe", "0-5s").split("-")[1].replace("s", "")))
        clip = ColorClip(size=DEFAULT_RESOLUTION, color=DEFAULT_BG_COLOR, duration=duration)
        text = segment.get("narration", "")
        txt_clip = TextClip(
            txt=text,
            fontsize=48,
            color=DEFAULT_TEXT_COLOR,
            font=FONT,
            method="caption",
            size=(DEFAULT_RESOLUTION[0] - 120, None),
        ).set_duration(duration)
        txt_clip = txt_clip.set_position(("center", "center")).margin(bottom=80, opacity=0)
        clips.append(CompositeVideoClip([clip, txt_clip]))

    if not clips:
        raise ValueError("Brak segmentów do renderowania tekstowego.")

    final_clip = concatenate_videoclips(clips, method="compose").set_fps(fps)
    final_clip.write_videofile(str(output_path), codec="libx264", audio_codec="aac", fps=fps)
    return Path(output_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Renderuj wideo na podstawie current_video_state.json")
    parser.add_argument("--state", default="current_video_state.json", help="Ścieżka do pliku stanu wideo")
    parser.add_argument("--output", default="output.mp4", help="Ścieżka do pliku wyjściowego MP4")
    parser.add_argument("--assets-dir", default="assets", help="Katalog z plikami assetów")
    parser.add_argument("--audio", default=None, help="Opcjonalny plik audio do dodania jako ścieżka dźwiękowa")
    parser.add_argument("--text-only", action="store_true", help="Renderuj tylko tekstowe slajdy bez assetów video")
    args = parser.parse_args()

    if args.text_only:
        render_text_only_video(state_path=args.state, output_path=args.output)
    else:
        render_video_from_state(
            state_path=args.state,
            output_path=args.output,
            assets_dir=args.assets_dir,
            audio_path=args.audio,
        )
