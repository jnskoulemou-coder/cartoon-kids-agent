import random
from pathlib import Path

import config
import main
import youtube_uploader
from topics import TOPICS

STATE_FILE = config.ROOT_DIR / ".topic_index"


def _next_index() -> int:
    if STATE_FILE.exists():
        index = int(STATE_FILE.read_text().strip() or "0")
    else:
        index = 0
    STATE_FILE.write_text(str((index + 1) % len(TOPICS)))
    return index % len(TOPICS)


def _make_title(topic: str) -> str:
    title = f"{topic[0].upper()}{topic[1:]}"
    return f"{title} | Happy Family"


def run_daily():
    index = _next_index()
    entry = TOPICS[index]
    print(f"[daily_task] Topic {index + 1}/{len(TOPICS)}: [{entry['type']}] {entry['topic']}")
    result = main.run(entry["topic"], entry["type"])

    title = _make_title(result["topic"])
    if entry["type"] == "journey":
        hashtags = "#kidsadventure #elephant #funforkids #storytime"
        tags = ["kids adventure", "elephant", "children's story", "fruit adventure"]
    else:
        hashtags = "#funnycat #funnyrabbit #animalcomedy #catsvsrabbits"
        tags = ["funny cat", "funny rabbit", "animal comedy", "cartoon animals", "cat and rabbit"]
    description = f"{result['narration']}\n\n{hashtags}"

    print("Uploading to YouTube (public)...")
    youtube_uploader.upload_video(
        result["video_path"],
        title=title,
        description=description,
        tags=tags,
        privacy_status="public",
    )

    _cleanup(result)


def _cleanup(result: dict) -> None:
    """Remove the generated video and intermediate files once upload succeeded,
    so finished videos don't pile up and fill the disk."""
    paths_to_remove = [
        result["video_path"],
        result["downloads_copy"],
        result["script_path"],
        result["voice_path"],
        *result["scene_paths"],
    ]
    for path in paths_to_remove:
        path = Path(path)
        if path.exists():
            try:
                path.unlink()
            except OSError as e:
                print(f"Could not delete {path}: {e}")
    print("Cleaned up local video and working files.")


if __name__ == "__main__":
    run_daily()
