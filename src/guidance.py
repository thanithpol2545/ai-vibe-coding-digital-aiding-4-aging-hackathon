import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

_FONT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts", "THSarabunNew.ttf"))

EXERCISE_GUIDES = {
    "Finger Tapping": {
        "icon": "👆",
        "position": "นั่ง",
        "prep": [
            ("🪑", "นั่งเก้าอี้ หลังตรง"),
            ("🤲", "ยกมือขึ้นระดับอก"),
            ("🖐️", "หันฝ่ามือเข้าหากล้อง"),
            ("👆", "แตะนิ้วชี้-นิ้วโป้ง ให้ใหญ่และเร็ว"),
        ],
        "cues": {
            "setup": "👇 วางมือในกรอบสีเขียว",
            "go": "แตะนิ้วชี้กับนิ้วโป้งให้ใหญ่และเร็ว! ⚡",
            "steady": "ทำได้ดีแล้ว! รักษาจังหวะ steady! 💪",
            "almost": "อีกนิดเดียว! สุดแรง! 🔥",
            "done": "เยี่ยมมาก! 🎉",
            "nohand": "🖐️ หันฝ่ามือเข้าหากล้อง",
            "outside": "👇 ขยับมือมาไว้ในกรอบสีเขียว",
        },
        "hand_pos": "center",
    },
    "Reach-to-Target": {
        "icon": "🏃",
        "position": "ยืน",
        "prep": [
            ("🧍", "ยืนตรง เท้ากว้างเท่าช่วงไหล่"),
            ("🤲", "แขนทั้งสองข้างอยู่ข้างลำตัว"),
            ("🖐️", "หันฝ่ามือเข้าหากล้อง"),
            ("🏃", "เอื้อมแขนทั้งสองไปข้างหน้า"),
        ],
        "cues": {
            "setup": "🧍 ยืนในกรอบสีเขียว",
            "go": "เอื้อมแขนไปข้างหน้า! 🏃",
            "steady": "ต่อเนื่อง! 💪",
            "almost": "อีกไม่กี่ครั้ง! 🔥",
            "done": "ยอดเยี่ยม! 🎉",
            "nohand": "🖐️ หันฝ่ามือเข้าหากล้อง",
            "outside": "🧍 ขยับเข้ามาในกรอบ",
        },
        "hand_pos": "full_body",
    },
    "Combined": {
        "icon": "🔄",
        "position": "นั่ง",
        "prep": [
            ("🪑", "นั่งเก้าอี้ หลังตรง"),
            ("🤲", "ยกมือขึ้นระดับอก"),
            ("🖐️", "หันฝ่ามือเข้าหากล้อง"),
            ("🔄", "สลับแตะนิ้วกับเอื้อมแขน"),
        ],
        "cues": {
            "setup": "👇 วางมือในกรอบสีเขียว",
            "go": "เริ่มด้วยแตะนิ้ว แล้วเอื้อมแขน! 🔄",
            "steady": "เก่งมาก! ทำสลับไปมา! 💪",
            "almost": "ใกล้เสร็จแล้ว! 🔥",
            "done": "เยี่ยมมาก! 🎉",
            "nohand": "🖐️ หันฝ่ามือเข้าหากล้อง",
            "outside": "👇 ขยับมือมาในกรอบ",
        },
        "hand_pos": "center",
    },
}


def get_cue(test_type: str, phase: str) -> str:
    return EXERCISE_GUIDES.get(test_type, EXERCISE_GUIDES["Finger Tapping"])["cues"].get(phase, "")


def _box(frame, x1, y1, x2, y2, color, alpha=0.55):
    o = frame.copy()
    cv2.rectangle(o, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(o, alpha, frame, 1 - alpha, 0, frame)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)


def _uses_thai(text):
    return any('\u0E00' <= c <= '\u0E7F' or '\u0E80' <= c <= '\u0EFF' or ord(c) > 127 for c in text)


def _draw_pil_text(frame, text, x, y, color=(255, 255, 255), bg=None, font_size=22):
    pad_x, pad_y = 4, 2
    bgr = tuple(reversed(color))
    font = ImageFont.truetype(_FONT_PATH, font_size)
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    if bg:
        bg_rgb = tuple(reversed(bg))
        draw.rectangle(
            (x - pad_x, y - th - pad_y, x + tw + pad_x, y + pad_y),
            fill=bg_rgb,
        )
    draw.text((x, y - th), text, font=font, fill=bgr)
    frame[:] = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return tw, th


def _txt(frame, text, x, y, color=(255, 255, 255), scale=0.55, thick=2, bg=None, max_w=None):
    if _uses_thai(text) and os.path.isfile(_FONT_PATH):
        font_size = max(14, int(scale * 40))
        return _draw_pil_text(frame, text, x, y, color, bg, font_size)
    if max_w:
        while cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thick)[0][0] > max_w and scale > 0.3:
            scale -= 0.05
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thick)
    if bg:
        cv2.rectangle(frame, (x - 6, y - th - 4), (x + tw + 6, y + 4), bg, -1)
    cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick)


def draw_setup_overlay(frame: np.ndarray, test_type: str):
    h, w = frame.shape[:2]
    guide = EXERCISE_GUIDES.get(test_type, EXERCISE_GUIDES["Finger Tapping"])

    dim = cv2.addWeighted(frame, 0.30, np.zeros_like(frame), 0.70, 0)

    bar_h = 80
    cv2.rectangle(dim, (0, 0), (w, bar_h), (30, 30, 30), -1)
    _txt(dim, f"📋 {guide['icon']} {test_type} — เตรียมตัวก่อนบันทึก", 20, 55,
         (255, 255, 100), 0.9, 3)

    step_h = 38
    total_steps_h = len(guide["prep"]) * step_h + 30
    start_y = bar_h + 20

    _box(dim, 10, start_y - 5, 350, start_y + total_steps_h, (0, 0, 0), 0.3)
    _txt(dim, "📝 ขั้นตอนการเตรียมตัว", 20, start_y + 16, (255, 255, 200), 0.65, 2)

    for i, (emoji, text) in enumerate(guide["prep"]):
        y = start_y + 45 + i * step_h
        step_num = i + 1
        cv2.circle(dim, 35, y - 6, 14, (0, 200, 100), -1)
        cv2.circle(dim, 35, y - 6, 14, (255, 255, 255), 2)
        _txt(dim, str(step_num), 27, y, (255, 255, 255), 0.5, 2)
        _txt(dim, f"{emoji}  {text}", 60, y, (240, 240, 240), 0.65, 2)

    zone_color = (0, 200, 100)
    if guide["hand_pos"] == "center":
        zx1, zy1 = int(w * 0.06), int(h * 0.16)
        zx2, zy2 = int(w * 0.94), int(h * 0.54)
        cv2.rectangle(dim, (zx1, zy1), (zx2, zy2), zone_color, 4)
        _txt(dim, "👐  วางมือตรงนี้", zx1 + 15, zy1 + 35, zone_color, 0.65, 3, bg=(0, 0, 0))
        cv2.rectangle(dim, (zx1, zy1), (zx2, zy2), (0, 80, 40), 2)
    elif guide["hand_pos"] == "full_body":
        zx1, zy1 = int(w * 0.10), int(h * 0.06)
        zx2, zy2 = int(w * 0.90), int(h * 0.80)
        cv2.rectangle(dim, (zx1, zy1), (zx2, zy2), zone_color, 4)
        _txt(dim, "🧍  ยืนในบริเวณนี้", zx1 + 15, zy1 + 35, zone_color, 0.65, 3, bg=(0, 0, 0))

    _txt(dim, get_cue(test_type, "setup"), w // 2 - 200, h - 60,
         (255, 255, 0), 0.7, 3, bg=(0, 0, 0))
    _txt(dim, "🎬 กดปุ่ม 'เริ่มบันทึก' ด้านล่าง →", w // 2 - 210, h - 25,
         (180, 180, 180), 0.5, 2)

    _txt(dim, "🔊 ระบบจะแนะนำด้วยเสียง", w - 230, h - 90,
         (100, 200, 255), 0.5, 2, bg=(0, 0, 0))

    return dim


def draw_countdown(frame: np.ndarray, seconds_left: int):
    h, w = frame.shape[:2]
    _box(frame, w // 2 - 140, h // 2 - 90, w // 2 + 140, h // 2 + 80, (0, 0, 0), 0.4)
    color = (0, 255, 100) if seconds_left > 1 else (0, 100, 255)
    cv2.putText(frame, str(seconds_left), (w // 2 - 70, h // 2 + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 6, color, 10)
    _txt(frame, "เตรียมตัว...", w // 2 - 100, h // 2 - 95, (200, 200, 200), 0.8, 2)


def draw_recording_overlay(frame: np.ndarray, hands_detected: bool,
                           test_type: str, elapsed: int, duration: int):
    h, w = frame.shape[:2]
    remaining = max(0, duration - elapsed)

    # Bigger REC indicator
    cv2.circle(frame, (35, 35), 10, (0, 0, 255), -1)
    cv2.circle(frame, (35, 35), 14, (0, 0, 200), 3)
    _txt(frame, "REC", 55, 42, (0, 0, 255), 0.65, 3)

    _txt(frame, f"⏱ {remaining}s / {duration}s", w - 160, 42,
         (255, 255, 255), 0.55, 2, bg=(0, 0, 0))

    zx1, zy1 = int(w * 0.06), int(h * 0.10)
    zx2, zy2 = int(w * 0.94), int(h * 0.54)
    cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 180, 80), 2)

    if not hands_detected:
        _txt(frame, get_cue(test_type, "nohand"),
             w // 2 - 200, h - 30, (255, 200, 0), 0.7, 3, bg=(0, 0, 0))
        return

    progress = 1.0 - (remaining / max(duration, 1))
    bar_w = int(300 * progress)
    bar_x = w // 2 - 150
    bar_y = h - 60
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + 300, bar_y + 16), (50, 50, 50), -1)
    if bar_w > 0:
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + 16), (0, 200, 100), -1)

    if remaining > 6:
        msg, clr = get_cue(test_type, "go"), (100, 255, 100)
    elif remaining > 3:
        msg, clr = get_cue(test_type, "steady"), (200, 255, 100)
    elif remaining > 0:
        msg, clr = get_cue(test_type, "almost"), (0, 200, 255)
    else:
        msg, clr = get_cue(test_type, "done"), (0, 255, 200)

    _txt(frame, msg, w // 2 - 200, h - 30, clr, 0.7, 3, bg=(0, 0, 0))
