# Security Policy

## Supported versions

Only the latest release receives fixes. Cursor Mover is a small single-purpose
utility with one maintainer; there are no long-term support branches.

## Reporting a vulnerability

Please **do not open a public issue** for a security problem.

Use GitHub's [private vulnerability reporting](https://github.com/iAaquibjawed/cursor-mover/security/advisories/new)
instead. Expect an acknowledgement within seven days.

Useful details to include: the affected version, your macOS version, and the
smallest set of steps that demonstrates the problem.

## What is in scope

Cursor Mover holds no credentials and makes no network requests, so the
interesting surface is narrow:

- **AppleScript construction (macOS).** The app shells out to `osascript` for
  dialogs and notifications. All interpolated text goes through
  `applescript_quote()` in `src/cursor_mover/systemui/applescript.py`. A way to
  escape that quoting and execute arbitrary AppleScript is in scope.
- **Subprocess construction (Linux).** `notify-send` is invoked with an argument
  list, never a shell string. A way to reach a shell is in scope.
- **Accessibility permission (macOS).** The app requests Accessibility access,
  which is a powerful entitlement. Anything that lets another process leverage
  Cursor Mover's grant is in scope.
- **Settings file handling.** The settings JSON is parsed on launch from a
  per-platform location. Crashes are a bug; code execution would be a
  vulnerability.

## What is out of scope

- The app moving your cursor. That is the entire purpose of the tool.
- Gatekeeper and SmartScreen warnings on unsigned builds. This is documented in
  the README, and the fix is to sign and notarize, not a vulnerability.
- Cursor Mover not working on Wayland. Wayland forbids pointer control by
  design; that is the platform behaving correctly.
- Using Cursor Mover to defeat idle or presence detection in other software.
  That is a policy question between you and whoever runs that software.
