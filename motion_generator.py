import argparse
import base64
import time
from pathlib import Path

import requests

import config

API_BASE = "https://api.dev.runwayml.com/v1"
RUNWAY_VERSION = "2024-11-06"

HEADERS = {
    "Authorization": f"Bearer {config.RUNWAY_API_KEY}",
    "X-Runway-Version": RUNWAY_VERSION,
    "Content-Type": "application/json",
}


def _image_to_data_uri(image_path: Path) -> str:
    ext = image_path.suffix.lstrip(".").lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def generate_motion(image_path: Path, output_path: Path, prompt_text: str = "") -> Path:
    """Turn a still image into a short animated video clip using Runway's image-to-video model."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    body = {
        "promptImage": _image_to_data_uri(image_path),
        "model": "gen4_turbo",
        "ratio": "720:1280",
        "duration": 5,
    }
    if prompt_text:
        body["promptText"] = prompt_text

    response = requests.post(f"{API_BASE}/image_to_video", headers=HEADERS, json=body, timeout=60)
    if not response.ok:
        print(f"[DEBUG] Runway start response: {response.status_code} {response.text}")
    response.raise_for_status()
    task_id = response.json()["id"]

    while True:
        time.sleep(10)
        result = requests.get(f"{API_BASE}/tasks/{task_id}", headers=HEADERS, timeout=30)
        result.raise_for_status()
        data = result.json()
        status = data.get("status")
        if status in ("PENDING", "RUNNING", "THROTTLED"):
            print(f"[motion_generator] {image_path.name}: {status}...")
            continue
        if status == "SUCCEEDED":
            video_url = data["output"][0]
            video_bytes = requests.get(video_url, timeout=60).content
            output_path.write_bytes(video_bytes)
            return output_path
        raise RuntimeError(f"Runway generation failed: {data}")


def main():
    parser = argparse.ArgumentParser(description="Animate a still image into a short video clip using Runway")
    parser.add_argument("image", help="Path to the source image")
    parser.add_argument("output", help="Output mp4 path")
    parser.add_argument("--prompt", default="", help="Optional motion description")
    args = parser.parse_args()

    path = generate_motion(Path(args.image), Path(args.output), args.prompt)
    print(f"Saved animated clip to {path}")


if __name__ == "__main__":
    main()
