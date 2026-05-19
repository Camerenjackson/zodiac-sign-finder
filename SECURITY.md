# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 2.x     | Yes       |

## Reporting a vulnerability

If you find a security issue, please **open a private report** on GitHub (Security → Report a vulnerability) or contact the repository owner directly. Do not open a public issue for sensitive bugs.

## Security properties of this app

This project is designed as a **local-only desktop utility**:

| Topic | Behavior |
| ----- | -------- |
| Network | **No** network requests, APIs, or telemetry |
| Data storage | **No** files written; birth date stays in memory only |
| Authentication | **None** — no accounts or secrets |
| Dependencies (runtime) | **None** beyond Python’s standard library + tkinter |
| Clipboard | Copies **your own** calculated result when you choose “Copy result” |

### Input handling

- Month is chosen from a **read-only** dropdown (canonical month names).
- Day is validated as an integer within the valid range for that month.
- Error messages avoid echoing untrusted long strings back to the user.

### Building the `.exe`

PyInstaller is a **development-only** dependency (`requirements-build.txt`). Only install it when building locally. Do not commit `dist/` or `build/` folders to Git.

## What not to commit

Never commit:

- `.env` files or API keys (this app does not use them)
- `dist/*.exe` or `build/` output (use [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository) for binaries instead)
