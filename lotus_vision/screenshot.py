"""Screen capture utilities."""

import base64
import io

from PIL import Image


def take_screenshot() -> tuple[str, tuple[int, int]]:
    """Take a screenshot and return (base64_png, (width, height))."""
    import pyautogui

    img = pyautogui.screenshot()
    # Resize to max 1280px wide to keep tokens reasonable
    max_width = 1280
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
    return b64, (img.width, img.height)
