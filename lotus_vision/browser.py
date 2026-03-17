"""Browser-based screenshot and action execution using Playwright.

Used in CI environments where there's no physical display.
"""

import base64

from playwright.sync_api import Page, sync_playwright


class Browser:
    """Manages a headless browser for the CUA agent."""

    def __init__(self, headless: bool = True, viewport_width: int = 1280, viewport_height: int = 900):
        self.headless = headless
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self._playwright = None
        self._browser = None
        self._page: Page | None = None

    def start(self, url: str) -> None:
        """Launch browser and navigate to URL."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._page = self._browser.new_page(
            viewport={"width": self.viewport_width, "height": self.viewport_height}
        )
        self._page.goto(url, wait_until="networkidle")

    def screenshot(self) -> tuple[str, tuple[int, int]]:
        """Take a screenshot and return (base64_png, (width, height))."""
        png_bytes = self._page.screenshot(full_page=False)
        b64 = base64.standard_b64encode(png_bytes).decode("utf-8")
        return b64, (self.viewport_width, self.viewport_height)

    def execute_action(self, action: dict) -> str:
        """Execute a CUA action in the browser."""
        action_type = action.get("type")
        coordinate = action.get("coordinate")

        if action_type == "click":
            x, y = coordinate
            self._page.mouse.click(x, y)
            return f"Clicked at ({x}, {y})"

        elif action_type == "double_click":
            x, y = coordinate
            self._page.mouse.dblclick(x, y)
            return f"Double-clicked at ({x}, {y})"

        elif action_type == "type":
            text = action.get("text", "")
            self._page.keyboard.type(text, delay=30)
            return f"Typed: {text}"

        elif action_type == "key":
            key = action.get("key", "")
            self._page.keyboard.press(key)
            return f"Pressed key: {key}"

        elif action_type == "scroll":
            x, y = coordinate
            direction = action.get("direction", "down")
            amount = action.get("amount", 3)
            delta = amount * 100
            if direction == "down":
                delta = -delta
            self._page.mouse.move(x, y)
            self._page.mouse.wheel(0, -delta if direction == "up" else delta)
            return f"Scrolled {direction} at ({x}, {y})"

        elif action_type == "move":
            x, y = coordinate
            self._page.mouse.move(x, y)
            return f"Moved cursor to ({x}, {y})"

        elif action_type == "screenshot":
            return "screenshot_requested"

        else:
            return f"Unknown action: {action_type}"

    def stop(self) -> None:
        """Close browser and cleanup."""
        if self._page:
            self._page.close()
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()
