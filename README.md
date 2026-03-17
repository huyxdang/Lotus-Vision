# Lotus Vision

Visual QA agent that tests your app the way real users see it — not through the DOM. It screenshots your UI, navigates like a human, and simulates user personas (elderly, colorblind, non-native speakers) to catch accessibility, usability, and aesthetic issues before they reach production.

**Drop it into your CI pipeline. Every PR gets visual QA'd before merge.**

## How It Works

1. PR triggers Lotus Vision in CI (GitHub Actions)
2. Agent launches your app, takes screenshots, and navigates it as different user personas
3. Finds issues: bad contrast, broken layouts, untranslatable text, confusing flows
4. Posts a review comment on the PR with screenshots and findings
5. Blocks merge until issues are addressed

## TODO
- [ ] Build the CUA agent (screenshot → reason → act loop)
- [ ] Persona system (accessibility, i18n, elderly users, etc.)
- [ ] GitHub Actions integration (run on PR, post review comments)
- [ ] Demo — PR with subtle UI bugs caught by the agent