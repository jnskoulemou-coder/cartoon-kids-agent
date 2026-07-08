import argparse
import shutil
from pathlib import Path

import config
import image_generator
import motion_generator
import story_generator
import video_assembler
import voice_generator

DOWNLOADS_DIR = Path.home() / "Downloads"


def run(topic: str, content_type: str = None) -> dict:
    print(f"Generating story for: {topic}")
    story = story_generator.generate_story(topic, content_type)
    print(f"[{story['content_type']}]")
    print(story["narration"])

    slug = topic.lower().replace(" ", "_")[:40]
    script_path = config.ASSETS_DIR / f"{slug}_script.txt"
    script_path.write_text(story["narration"], encoding="utf-8")

    print("Generating voice-over...")
    voice_path = config.ASSETS_DIR / f"{slug}_voice.mp3"
    voice_generator.generate_voice(story["narration"], voice_path)

    print("Generating scene images...")
    scene_image_paths = []
    for i, scene in enumerate(story["scenes"]):
        scene_path = config.ASSETS_DIR / f"{slug}_scene{i + 1}.png"
        image_generator.generate_image(scene, scene_path)
        scene_image_paths.append(scene_path)

    print("Animating scenes...")
    scene_paths = []
    for i, (scene_image, scene_desc) in enumerate(zip(scene_image_paths, story["scenes"])):
        motion_path = config.ASSETS_DIR / f"{slug}_scene{i + 1}_motion.mp4"
        motion_generator.generate_motion(scene_image, motion_path, prompt_text=scene_desc)
        scene_paths.append(motion_path)

    print("Assembling final video...")
    output_path = config.OUTPUT_DIR / f"{slug}.mp4"
    video_assembler.assemble_video(voice_path, scene_paths, story["narration"], output_path)

    print(f"Done: {output_path}")

    downloads_copy = DOWNLOADS_DIR / output_path.name
    shutil.copy2(output_path, downloads_copy)
    print(f"Copied to {downloads_copy}")

    return {
        "video_path": output_path,
        "downloads_copy": downloads_copy,
        "script_path": script_path,
        "voice_path": voice_path,
        "scene_paths": scene_image_paths + scene_paths,
        "narration": story["narration"],
        "content_type": story["content_type"],
        "topic": topic,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate a full cartoon kids video from a topic")
    parser.add_argument("topic", help="Topic for the story")
    parser.add_argument("--type", choices=list(story_generator.CONTENT_TYPES), help="Content type (random if omitted)")
    args = parser.parse_args()

    run(args.topic, args.type)


if __name__ == "__main__":
    main()
