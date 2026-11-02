---
name: video-studio-setup
description: Set up or diagnose the Video Studio plugin on this computer, connect an authorized Studio account, verify local video tools, or enable live skill development. Use for first-time installation, a new editing machine, or broken local setup. Do not use to perform an edit, revise feedback, or write a recording script.
---

# Video Studio Setup

Connect Video Studio and verify a portable local editing workspace.

Use the bundled [setup guide](../../SETUP.md) for the installation and connection sequence. When online, reconcile it with the current public guide at `https://github.com/life-efficient/video-studio-plugin/blob/main/SETUP.md` so an old installed skill does not repeat superseded setup advice. Inspect the latest published package version before prescribing a version-specific repair.

## Contract Checklist

- Resolve the installed plugin root from this skill, never from a personal absolute path.
- Use each editor's authorized Studio account; never copy another person's credentials or use service keys.
- Keep plugin files read-only during normal editing and use a separate writable workspace.
- Verify dependency checks and an actual synthetic render without playing media.
- Do not claim another person's computer was tested from an isolated local test.

## Workflow

1. Locate and check the package.
   - The plugin root is two directories above this skill. The runner is `packages/local-runner/video_studio.py` within that root. Discover a working Python 3.9+ interpreter first. On Windows prefer `py -3` when available, otherwise verify `python --version`; on macOS/Linux use the available `python3` interpreter. Run `<PYTHON> "<PLUGIN_ROOT>/packages/local-runner/video_studio.py" --help` and `doctor`, quoting paths with spaces. Substitute the verified interpreter for `<PYTHON>` in subsequent examples.
   - On Windows verify both `ffmpeg.exe` and `ffprobe.exe` with `Get-Command ffmpeg, ffprobe` in PowerShell. Their directory must be on `PATH` for the editing client, not only an existing terminal. Restart the client after changes and rerun `doctor`. Normal plugin installation copies files and requires no symlinks or Developer Mode.
   - Require Python 3.9 or newer and working FFmpeg/FFprobe. Install missing dependencies using the person's approved package manager, then rerun the check. Rendering frameworks used by a particular editable project may require additional dependencies.
   - Anti-patterns: assuming Homebrew exists, executing an old machine's paths, treating the plugin cache as an edit workspace
2. Connect the person's account.
   - Use the registered Video Studio app required by the plugin and its normal Connect/sign-in flow. The package's `.app.json` references that app; the skills being installed or enabled does not establish app authorization. Read accessible organizations and videos to confirm the intended project is available.
   - If the connection tools are absent, first inspect the installed package version, `plugin.json`, `.app.json`, and plugin/app settings. Use targeted tool discovery for `list_organizations`, `list_videos`, and `prepare_edit`, including lazy-loaded tools when supported. Report whether the app dependency is missing, not connected, denied, or connected with a stale tool inventory. Do not infer sign-in state from a missing tool alone.
   - Version 0.1.0 used a standalone OAuth MCP declaration without a pre-registered OAuth client. If that version is installed, refresh the public marketplace with `codex plugin marketplace upgrade video-studio-team`, then update/reinstall `video-studio@video-studio-team` through the supported plugin interface. Verify version 0.1.1 or newer and the required Studio app. Preserve existing settings and do not remove working connections. Complete Connect if the app is available; if it is unavailable, report that exact error so the owner can resolve app distribution. A new chat is useful only after a connection or package change, not as a repeated substitute for diagnosing it.
   - Do not run standalone `codex mcp login` against this URL unless a supported, pre-registered OAuth client has been supplied. Do not invent client IDs, copy credentials, or create an unauthenticated workaround. When blocked, give the failed connection stage and a sanitized error message without tokens, browser callback URLs, or authorization codes.
   - Prefer the authenticated MCP bridge described in the runner README: call `prepare_edit`, fetch its assets through connected MCP tools into a local staging directory, prepare from that manifest, and deliver through a generated upload plan. Route media chunks programmatically, never through conversation text.
   - Optional direct sessions use `create_edit_session` for the exact authorized video. Store its response in a private session JSON file outside the plugin and project snapshots and use the runner's `--session-file` option only where the hosting layer supports it. Never display tokens or put them in chat, shell history, logs, screenshots, or version control. Do not bypass hosting authentication.
   - After connecting, call `list_organizations` and `list_videos` as read-only probes. Distinguish authentication success from authorization: a 401 requires sign-in, a 403 requires access review, and absent production tools on an otherwise working connection indicate a tool inventory/version gap. A review-only connection does not permit production work. Do not prepare or download a real project unless the user has requested that project; successful setup needs read-only access checks and synthetic local media only.
   - Anti-patterns: copying a service key, reusing another editor's identity, guessing that missing access means no videos exist
3. Verify local rendering.
   - Run `smoke --workspace <NEW_EMPTY_DIRECTORY>` using the runner. Inspect the generated checks and frames silently; do not launch a player.
   - This fixture contains synthetic media only and does not upload or alter a Studio video. Report its actual result, operating system, and any missing dependencies. A macOS isolated-workspace result does not certify Windows; the actual editor must pass the local check and a real edit/revision on their computer.
   - Anti-patterns: using private footage as a setup fixture, uploading a smoke test to a real project, claiming audio playback review
4. Prepare the first authorized project.
   - Continue here only when the user requested a specific project. For setup-only requests, stop after verified read-only account access and the synthetic render; do not fetch real recordings just to prove the connection works.
   - Run `prepare --manifest <MANIFEST_JSON> --assets <DOWNLOADED_ASSETS> --workspace <NEW_DIRECTORY>` after the MCP bridge fetch, or use a verified direct session with `prepare --video <VIDEO_ID> --workspace <NEW_DIRECTORY>`. Inspect its manifest, fetched recordings, script, feedback, and editable baseline before editing.
   - For a new edit use `$edit-video`; for feedback-led revisions use `$iterate-video-edit`. Follow [production handoff](../edit-video/references/studio-handoff.md).
   - Anti-patterns: starting a revision without its matching editable baseline, overwriting an existing workspace, treating setup as authorization to publish
5. Configure development links only when requested.
   - Development linking requires the application development checkout containing `scripts/plugin-dev-links.py`; that helper is not included in the public plugin repository or installed package. Confirm the helper exists before proceeding. If it is absent, keep the ordinary copied installation and report that development linking needs that checkout. For a verified application development checkout, use `<PYTHON> "<CHECKOUT>/scripts/plugin-dev-links.py" --source "<CHECKOUT>"` with the verified interpreter. It links individual skill folders into the active Codex skills directory and verifies their resolved paths. It refuses conflicts unless `--backup-conflicts` was explicitly selected.
   - On Windows, symlinks may require Developer Mode or elevated privileges; do not enable either just for a normal installation. Use the ordinary copied plugin unless the user specifically requests development links.
   - Linked development skills update immediately on disk. Plugin marketplace installs use a cached copy, so rebuild and refresh/reinstall the plugin when testing the distributed package. Avoid simultaneously enabling duplicate cached and development skills.
   - Anti-patterns: replacing the entire user skills directory, deleting a conflicting skill, promising marketplace caches are live symlinks

## Anti-Patterns

- Bundling private recordings, references, credentials, or production projects in the plugin.
- Treating successful setup as proof of a complete real edit or another machine's verification.
- Requiring a repository checkout for ordinary installed-plugin editing.

## Output

Report the connected project, resolved package path, dependency and synthetic-render results, development links if requested, and any remaining access or project-specific requirements. Keep credentials private.

Check troubleshooting behavior with [setup scenarios](tests/scenarios.md).
