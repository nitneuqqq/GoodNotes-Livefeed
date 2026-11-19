"""Watch a mirrored GoodNotes screen and have Claude flag math mistakes as you write."""
import argparse
import base64
import io
import time
import winsound

import anthropic
from PIL import ImageChops, ImageGrab

SYSTEM = (
    "You are a math tutor watching a screenshot of a student's handwritten work in a notes app. "
    "Check every step on the page. If all steps so far are correct, or there is no math, reply with exactly: OK. "
    "Otherwise name the first wrong step, say in one or two sentences what is wrong, and show the corrected step. "
    "Ignore a last line that looks unfinished."
)


def thumb(img):
    return img.convert("L").resize((200, 200))


def changed(a, b):
    # Threshold ignores video-compression flicker from the screen mirror.
    return ImageChops.difference(a, b).point(lambda p: 255 if p > 40 else 0).getbbox() is not None


def check(client, img):
    img.thumbnail((1568, 1568))  # Claude's recommended max edge; bigger just costs more
    buf = io.BytesIO()
    img.save(buf, "PNG")
    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                         "data": base64.standard_b64encode(buf.getvalue()).decode()}},
            {"type": "text", "text": "Check my work."},
        ]}],
    )
    if response.stop_reason == "refusal":
        return None
    return "".join(b.text for b in response.content if b.type == "text").strip()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--region", help="left,top,width,height of the mirror window (default: whole screen)")
    p.add_argument("--pause", type=float, default=2.0, help="seconds of no writing before checking")
    args = p.parse_args()
    bbox = None
    if args.region:
        x, y, w, h = map(int, args.region.split(","))
        bbox = (x, y, x + w, y + h)

    client = anthropic.Anthropic()
    prev = sent = last_reply = None
    last_change = time.monotonic()
    print("Watching. Write in GoodNotes; Ctrl+C to stop.")
    while True:
        img = ImageGrab.grab(bbox=bbox, all_screens=True)
        small = thumb(img)
        now = time.monotonic()
        if prev is not None and changed(small, prev):
            last_change = now
        prev = small
        if now - last_change >= args.pause and (sent is None or changed(small, sent)):
            sent = small
            try:
                reply = check(client, img)
            except anthropic.APIConnectionError:
                print("Network error, will retry on next change.")
                sent = None
            except anthropic.APIStatusError as e:
                print(f"API error {e.status_code}: {e.message}")
                sent = None
            else:
                if reply and reply != "OK" and reply != last_reply:
                    winsound.MessageBeep()
                    print(f"\n[{time.strftime('%H:%M:%S')}] {reply}")
                last_reply = reply
        time.sleep(1)


if __name__ == "__main__":
    main()
