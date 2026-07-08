import argparse
import json
import random

from anthropic import Anthropic

import config

CONTENT_TYPES = {
    "animals": {
        "label": "talking animal characters only (no fruit, no children). Always "
        "include a funny rabbit and/or a funny cat among the characters, "
        "with a fun, comedic tone - make it genuinely funny, aimed at making viewers laugh. "
        "Classic slapstick chase-comedy style (in the spirit of a lighthearted cat-and-mouse "
        "rivalry cartoon) works great: silly chases, near-misses, clever tricks, physical "
        "comedy, exaggerated reactions - but always playful and harmless, friends by the end. "
        "Also mix in fun dance moments - a cat busting silly dance moves, a rabbit hopping "
        "and dancing, animals having a dance-off together - for variety alongside the chases",
    },
}

SYSTEM_PROMPT_TEMPLATE = """You write short children's cartoon video scripts (TikTok/Reels/Shorts), \
in ENGLISH only. The subject of this video: {label}.

Important rules:
- Only use the character types described above for this video.
- About 60 seconds of spoken narration (150-160 words), simple and joyful language for a young child.
- A story with a beginning, middle, and end, with a small lesson (health, nature, friendship, \
effort, sharing...).
- Characters must always be ACTIVE and doing something physical - running, jumping, dancing, \
racing, climbing, playing, chasing, building, swimming. Avoid scenes of characters just standing \
and talking; every scene should show clear physical action and motion.
- No markdown, no emoji, no hashtags in the narration.

You must also split the story into exactly 4 scenes for illustration. For each scene, write a \
short visual description (one sentence) that captures a clear physical action or movement \
(mid-run, mid-jump, mid-dance, etc., not a static pose), always specifying "children's cartoon \
illustration style, bright colors, simple shapes, dynamic action pose" and naming the characters present.

Respond with ONLY a JSON object, no other text, in this exact shape:
{{"narration": "...", "scenes": ["scene 1 description", "scene 2 description", "scene 3 description", "scene 4 description"]}}"""


def generate_story(topic: str, content_type: str = None) -> dict:
    content_type = content_type or random.choice(list(CONTENT_TYPES))
    label = CONTENT_TYPES[content_type]["label"]

    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=2000,
        system=SYSTEM_PROMPT_TEMPLATE.format(label=label),
        messages=[
            {"role": "user", "content": f"Topic: {topic}"},
        ],
    )
    text_blocks = [block.text for block in message.content if block.type == "text"]
    text = "".join(text_blocks).strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    story = json.loads(text)
    story["content_type"] = content_type
    return story


def main():
    parser = argparse.ArgumentParser(description="Generate a cartoon story (fruits, animals, kids, or mixed)")
    parser.add_argument("topic", help="Topic for the story (e.g. 'why sleep matters')")
    parser.add_argument("--type", choices=list(CONTENT_TYPES), help="Content type (random if omitted)")
    args = parser.parse_args()

    story = generate_story(args.topic, args.type)
    print(f"[{story['content_type']}]")
    print(story["narration"])
    print()
    for i, scene in enumerate(story["scenes"], 1):
        print(f"Scene {i}: {scene}")


if __name__ == "__main__":
    main()
