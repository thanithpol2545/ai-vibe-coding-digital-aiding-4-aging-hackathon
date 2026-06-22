import os, base64, io, hashlib
from gtts import gTTS
from logger import setup_logger

logger = setup_logger("voice_guide")

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

_CACHE = {}

PHRASES = {
    "finger_tapping": {
        "setup": "วางมือในกรอบสีเขียว หันฝ่ามือเข้าหากล้อง ยกมือขึ้นระดับอก",
        "go": "เริ่ม แตะนิ้วชี้กับนิ้วโป้ง ให้ใหญ่และเร็วที่สุด",
        "steady": "ทำได้ดีแล้ว รักษาจังหวะต่อไป",
        "almost": "อีกไม่กี่วินาที สุดแรง",
        "done": "เยี่ยมมาก เสร็จแล้ว",
        "nohand": "หันฝ่ามือเข้าหากล้อง",
    },
    "reach_to_target": {
        "setup": "ยืนในกรอบสีเขียว แขนทั้งสองข้างอยู่ข้างลำตัว หันฝ่ามือเข้าหากล้อง",
        "go": "เริ่ม เอื้อมแขนทั้งสองไปข้างหน้า",
        "steady": " smooth ต่อเนื่อง",
        "almost": "อีกไม่กี่วินาที",
        "done": "ยอดเยี่ยม เสร็จแล้ว",
        "nohand": "หันฝ่ามือเข้าหากล้อง",
    },
    "combined": {
        "setup": "วางมือในกรอบสีเขียว ยกมือขึ้นระดับอก หันฝ่ามือเข้าหากล้อง",
        "go": "เริ่ม ด้วยการแตะนิ้ว แล้วเอื้อมแขน สลับกันไป",
        "steady": "เก่งมาก ทำสลับไปมา",
        "almost": "ใกล้เสร็จแล้ว",
        "done": " fantastic เสร็จแล้ว",
        "nohand": "หันฝ่ามือเข้าหากล้อง",
    },
    "countdown": {
        "3": "สาม",
        "2": "สอง",
        "1": "หนึ่ง",
    },
    "common": {
        "ready": "เตรียมตัว",
        "complete": "วิเคราะห์เสร็จสิ้น",
    },
}


def _phrase_key(test_type: str, phase: str) -> str:
    return f"{test_type}_{phase}"


def _get_phrase(test_type: str, phase: str) -> str:
    test_key = {
        "Finger Tapping": "finger_tapping",
        "Reach-to-Target": "reach_to_target",
        "Combined": "combined",
    }.get(test_type, "finger_tapping")

    phrases = PHRASES.get(test_key, PHRASES["finger_tapping"])
    return phrases.get(phase, "")


def _get_countdown_phrase(num: int) -> str:
    return PHRASES["countdown"].get(str(num), str(num))


def _get_common_phrase(phase: str) -> str:
    return PHRASES["common"].get(phase, "")


def _generate_audio(text: str, lang: str = "th") -> bytes:
    cache_key = hashlib.md5(text.encode()).hexdigest()
    cached_path = os.path.join(AUDIO_DIR, f"{cache_key}.mp3")
    if os.path.exists(cached_path):
        with open(cached_path, "rb") as f:
            return f.read()

    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        data = buf.read()
        with open(cached_path, "wb") as f:
            f.write(data)
        return data
    except Exception as e:
        logger.warning("TTS failed for '%s': %s", text[:20], e)
        return b""


def get_audio_html(text: str, lang: str = "th") -> str:
    data = _generate_audio(text, lang)
    if not data:
        return ""
    b64 = base64.b64encode(data).decode()
    return f'<audio autoplay style="display:none"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'


def get_cue_audio(test_type: str, phase: str) -> str:
    phrase = _get_phrase(test_type, phase)
    return get_audio_html(phrase) if phrase else ""


def get_countdown_audio(num: int) -> str:
    phrase = _get_countdown_phrase(num)
    return get_audio_html(phrase) if phrase else ""


def get_common_audio(phase: str) -> str:
    phrase = _get_common_phrase(phase)
    return get_audio_html(phrase) if phrase else ""
