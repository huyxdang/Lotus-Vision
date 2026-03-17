"""CI runner — runs the agent with multiple personas and outputs findings."""

import argparse
import json

from .agent import run_agent
from .personas import list_personas


def main():
    parser = argparse.ArgumentParser(description="Lotus Vision CI runner")
    parser.add_argument("--url", required=True, help="URL to test")
    parser.add_argument(
        "--personas",
        nargs="+",
        default=["default"],
        choices=list_personas(),
        help="Personas to test with",
    )
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--max-steps", type=int, default=15, help="Max steps per persona")
    parser.add_argument(
        "--task",
        default="Explore the application and find usability, accessibility, and visual issues.",
    )

    args = parser.parse_args()

    all_findings = []
    for persona in args.personas:
        print(f"\n{'='*60}")
        print(f"Testing as: {persona}")
        print(f"{'='*60}")

        findings = run_agent(
            url=args.url,
            task=args.task,
            persona=persona,
            max_steps=args.max_steps,
            headless=True,
        )
        all_findings.extend(findings)

    with open(args.output, "w") as f:
        json.dump(all_findings, f, indent=2)

    print(f"\nWrote {len(all_findings)} findings to {args.output}")


if __name__ == "__main__":
    main()
