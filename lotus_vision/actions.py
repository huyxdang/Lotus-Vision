"""Execute actions returned by the model."""

import time

import pyautogui

# Disable pyautogui's fail-safe for automated use
pyautogui.FAILSAFE = False


def execute_action(action: dict, screen_size: tuple[int, int]) -> str:
    """Execute a computer use action and return a status message."""
    action_type = action.get("type")
    coordinate = action.get("coordinate")

    if action_type == "click":
        x, y = coordinate
        pyautogui.click(x, y)
        return f"Clicked at ({x}, {y})"

    elif action_type == "double_click":
        x, y = coordinate
        pyautogui.doubleClick(x, y)
        return f"Double-clicked at ({x}, {y})"

    elif action_type == "type":
        text = action.get("text", "")
        pyautogui.typewrite(text, interval=0.03)
        return f"Typed: {text}"

    elif action_type == "key":
        key = action.get("key", "")
        pyautogui.hotkey(*key.split("+"))
        return f"Pressed key: {key}"

    elif action_type == "scroll":
        x, y = coordinate
        direction = action.get("direction", "down")
        amount = action.get("amount", 3)
        scroll_val = -amount if direction == "down" else amount
        pyautogui.scroll(scroll_val, x=x, y=y)
        return f"Scrolled {direction} at ({x}, {y})"

    elif action_type == "move":
        x, y = coordinate
        pyautogui.moveTo(x, y)
        return f"Moved cursor to ({x}, {y})"

    elif action_type == "screenshot":
        return "screenshot_requested"

    else:
        return f"Unknown action: {action_type}"
