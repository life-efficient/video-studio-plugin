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
   - Follow the bundled setup guide's browser approval flow using `local-agent/helper.py` from the plugin root. Copy the helper and its declared requirements to a stable user-owned agent directory outside the plugin cache, create a dedicated Python environment there, and explicitly install its requirements from the public PyPI registry through the approved installation route. Run that interpreter with the helper's `connect` command. Let the user compare the displayed code, sign in to Studio with ChatGPT if necessary, and approve the browser request. Honor host-required consent for credential creation.
   - The helper saves the credential in Windows Credential Manager, macOS Keychain, or a supported Linux desktop credential store. Do not request, copy, print, or manually configure a token. If the OS store is locked or unavailable, report that blocker instead of falling back to plaintext files or environment variables. Approval requests expire after ten minutes; restart `connect` after an expired request or interrupted credential delivery. The helper's `status` command reports presence without revealing the credential.
   - Configure a stdio MCP server with the actual absolute virtual-environment Python command and arguments `["<STABLE_HELPER_PATH>", "serve"]`. On Windows use `venv\Scripts\python.exe`; on macOS/Linux use `venv/bin/python`. Do not add `url` or `bearer_token_env_var` to this entry. Preserve unrelated settings and working connections. The helper rereads OS credentials per request, so a reconnect does not require changing configuration or inheriting new environment variables. Reload the client only when needed to load a changed MCP entry.
   - The registered Studio app remains optional. Preserve an already working managed app or direct bearer connection when preferred; these do not block the helper route. Discover `list_channels`, channel-filtered `list_videos`, and `prepare_edit`, including lazy-loaded tools where supported. Installed skills and a saved credential are not proof of account access: make actual read-only tool calls. A 401 requires reconnecting through browser approval, a 403 requires owner access review, and a network failure is separate. Do not run `codex mcp login` on the personal-token endpoint or invent OAuth client IDs. Keep diagnostics free of credentials.
   - Prefer the authenticated MCP bridge described in the runner README: call `prepare_edit`, fetch its assets through connected MCP tools into a local staging directory, prepare from that manifest, and deliver through a generated upload plan. Route media chunks programmatically, never through conversation text.
   - Optional direct sessions use `create_edit_session` for the exact authorized video. Store its response in a private session JSON file outside the plugin and project snapshots and use the runner's `--session-file` option only where the hosting layer supports it. Never display tokens or put them in chat, shell history, logs, screenshots, or version control. Do not bypass hosting authentication.
   - After connecting, call `list_channels` and `list_videos` with an accessible `channelId` as read-only probes. Distinguish authentication success from authorization: a 401 requires renewed authentication, a 403 requires access review, and absent production tools on an otherwise working connection indicate a tool inventory/version gap. A review-only connection does not permit production work. Do not prepare or download a real project unless the user has requested that project; successful setup needs read-only access checks and synthetic local media only.
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
