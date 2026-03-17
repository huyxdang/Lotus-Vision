"""Core CUA agent: screenshot → reason → act loop."""

import time

import anthropic

from .browser import Browser
from .personas import get_persona

DEFAULT_MODEL = "claude-sonnet-4-20250514"
MAX_STEPS = 50


def run_agent(
    url: str,
    task: str,
    persona: str = "default",
    model: str = DEFAULT_MODEL,
    max_steps: int = MAX_STEPS,
    headless: bool = True,
) -> list[dict]:
    """
    Run the visual QA agent.

    Args:
        url: The URL to test.
        task: What to test.
        persona: Persona name from personas.py.
        model: Anthropic model to use.
        max_steps: Maximum interaction steps before stopping.
        headless: Run browser headlessly (True for CI, False for local debugging).

    Returns:
        List of findings.
    """
    client = anthropic.Anthropic()
    persona_config = get_persona(persona)

    system_prompt = (
        f"You are Lotus Vision, a visual QA agent testing a web application.\n\n"
        f"Persona: {persona_config['name']}\n"
        f"{persona_config['system_prompt']}\n\n"
        f"Your task: {task}\n"
        f"URL to test: {url}\n\n"
        "Instructions:\n"
        "1. Look at each screenshot carefully through the lens of your persona.\n"
        "2. Navigate the app by clicking, scrolling, and typing to explore it.\n"
        "3. When you find an issue, describe it clearly with its severity "
        "(critical, major, minor).\n"
        "4. When you are done testing, respond with DONE and a summary of all findings.\n"
        "5. Be specific about locations — describe where on screen the issue is.\n"
        '6. Format each finding as: [SEVERITY] Issue description | Location on page'
    )

    browser = Browser(headless=headless)
    browser.start(url)

    try:
        screenshot_b64, screen_size = browser.screenshot()

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": screenshot_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            f"I've opened {url} in the browser. "
                            f"Please begin testing as the '{persona_config['name']}' persona. "
                            f"Screen size: {screen_size[0]}x{screen_size[1]}."
                        ),
                    },
                ],
            }
        ]

        findings = []

        for step in range(max_steps):
            print(f"\n--- Step {step + 1}/{max_steps} ---")

            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages,
                tools=[
                    {
                        "type": "computer_20250124",
                        "name": "computer",
                        "display_width_px": screen_size[0],
                        "display_height_px": screen_size[1],
                        "display_number": 1,
                    }
                ],
            )

            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            # Check if agent is done
            text_parts = [b.text for b in assistant_content if hasattr(b, "text")]
            full_text = " ".join(text_parts)

            if "DONE" in full_text:
                print("\nAgent finished testing.")
                findings.append(
                    {
                        "type": "summary",
                        "text": full_text,
                        "persona": persona_config["name"],
                    }
                )
                break

            # Look for tool use blocks
            tool_uses = [b for b in assistant_content if b.type == "tool_use"]
            if not tool_uses:
                if text_parts:
                    print(f"Agent says: {full_text[:200]}")
                break

            # Execute each action
            tool_results = []
            for tool_use in tool_uses:
                action = tool_use.input
                inner_action = action.get("action", action)
                action_type = inner_action.get("type", "unknown")
                print(f"Action: {action_type}")

                result_text = browser.execute_action(inner_action)

                # Take a new screenshot after any action
                time.sleep(0.5)
                screenshot_b64, screen_size = browser.screenshot()
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": screenshot_b64,
                                },
                            },
                            {"type": "text", "text": result_text},
                        ],
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        return findings

    finally:
        browser.stop()
