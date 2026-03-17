"""CLI entry point for Lotus Vision."""

import argparse
import json
import sys

from .agent import run_agent
from .personas import list_personas


def main():
    parser = argparse.ArgumentParser(
        description="Lotus Vision — Visual QA agent for CI pipelines"
    )
    parser.add_argument("url", help="URL to test")
    parser.add_argument(
        "-t", "--task",
        default="Explore the application and find usability, accessibility, and visual issues.",
        help="What to test",
    )
    parser.add_argument(
        "-p", "--persona",
        default="default",
        choices=list_personas(),
        help="User persona to simulate",
    )
    parser.add_argument(
        "--all-personas",
        action="store_true",
        help="Run with all personas sequentially",
    )
    parser.add_argument(
        "-s", "--max-steps",
        type=int,
        default=20,
        help="Maximum interaction steps (default: 20)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file for findings (JSON)",
    )

    args = parser.parse_args()

    personas_to_run = list_personas() if args.all_personas else [args.persona]
    all_findings = []

    for persona in personas_to_run:
        print(f"\n{'='*60}")
        print(f"Running as: {persona}")
        print(f"{'='*60}")

        findings = run_agent(
            url=args.url,
            task=args.task,
            persona=persona,
            max_steps=args.max_steps,
        )
        all_findings.extend(findings)

    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_findings, f, indent=2)
        print(f"\nFindings written to {args.output}")
    else:
        print("\n" + "="*60)
        print("FINDINGS SUMMARY")
        print("="*60)
        for finding in all_findings:
            print(json.dumps(finding, indent=2))


if __name__ == "__main__":
    main()
