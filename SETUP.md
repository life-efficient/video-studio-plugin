# Set up Video Studio

Follow this guide as the user's agent. Complete the supported setup steps yourself. Ask the user only for sign-in, consent, or a decision that cannot be resolved from their existing settings. Preserve unrelated plugins, working connections, and files.

## 1. Install or update

Use the public marketplace `https://github.com/life-efficient/video-studio-plugin`. Read the current package version from `plugins/video-studio/plugin.json` on its `main` branch, rather than assuming an installed version is current.

For Codex, inspect existing marketplace and plugin state. Add the marketplace only if absent:

```sh
codex plugin marketplace add life-efficient/video-studio-plugin
```

If already configured, refresh it:

```sh
codex plugin marketplace upgrade video-studio-team
```

Install or update the plugin using the client's supported plugin controls or CLI:

```sh
codex plugin add video-studio@video-studio-team
```

Verify the installed package version matches the current published version. A refreshed catalog is not proof that the installed copy updated. The package includes skills and a local runner. Its registered Video Studio app is optional: preserve an existing working app connection, but colleagues can use a personal-token MCP connection instead.

## 2. Connect the user's account

### Browser approval connection (preferred)

Version 0.1.4 includes the local connection helper at `local-agent/helper.py`. It opens Studio for the user to sign in with ChatGPT and approve the displayed connection code. The helper receives the credential directly and stores it in Windows Credential Manager, macOS Keychain, or a supported Linux desktop credential store. No token needs to pass through chat, a copied prompt, command arguments, environment variables, or MCP configuration.

Resolve the installed plugin root before using any paths. Use the verified Python 3.9+ interpreter to create a dedicated virtual environment outside the plugin cache. Keep a copy of `local-agent/helper.py` and `local-agent/requirements.txt` in a stable user-owned agent directory, updating them from the plugin when upgrading. Keep the virtual environment in that directory too. Do not replace an existing working environment blindly.

For Windows PowerShell, set `$StudioPlugin` to the actual installed plugin folder and use:

```powershell
$StudioAgent = Join-Path $env:LOCALAPPDATA 'VideoStudio\agent'
New-Item -ItemType Directory -Force -Path $StudioAgent | Out-Null
Copy-Item -LiteralPath "$StudioPlugin\local-agent\helper.py" -Destination "$StudioAgent\helper.py"
Copy-Item -LiteralPath "$StudioPlugin\local-agent\requirements.txt" -Destination "$StudioAgent\requirements.txt"
py -3 -m venv "$StudioAgent\venv"
& "$StudioAgent\venv\Scripts\python.exe" -m pip install -r "$StudioAgent\requirements.txt"
& "$StudioAgent\venv\Scripts\python.exe" "$StudioAgent\helper.py" connect
```

If `py -3` is unavailable, substitute the verified `python` interpreter. For macOS/Linux, use a stable user-owned directory, such as `$HOME/.local/share/video-studio/agent`, create its `venv` with the verified `python3`, and use `venv/bin/python` for dependency installation and helper commands. Install the helper's declared requirements from the public PyPI registry through the person's approved package installation route. Do not install plaintext keyring fallback packages.

The agent starts `connect` itself and lets the user complete browser sign-in and approval. Compare the helper's displayed code with the page before approving. The request expires after ten minutes. If the browser does not open, show only the helper's verification link and code, never a device secret or token. Follow any host-required consent prompt for creating credentials. If approval delivery is interrupted or expires, run `connect` again to start a fresh request.

After `connect` succeeds, merge this **stdio** MCP entry using the actual absolute interpreter and stable helper paths. Preserve unrelated configuration and avoid duplicate Video Studio entries:

```toml
[mcp_servers.video_studio]
command = "/absolute/user/agent/venv/bin/python"
args = ["/absolute/user/agent/helper.py", "serve"]
```

On Windows, the command is the virtual environment's `Scripts\python.exe`. Use TOML literal strings for Windows paths containing backslashes. Do not put `url`, `bearer_token_env_var`, or a literal token on this stdio entry. The helper sends authenticated HTTPS requests to the fixed Studio endpoint and rereads the OS credential store on each request. Reconnecting does not require changing the MCP entry or restarting Codex to inherit an environment variable. If the client needs to reload changed MCP configuration, reload it once through its supported controls or open a fresh session.

Run the helper's `status` command to check whether a credential is saved without printing it. `disconnect` removes only the local saved copy; revoke the connection from Studio to disable every copy. If the OS credential store is unavailable or locked, report that specific issue and let the user unlock or configure the supported store. Do not silently fall back to a file or environment variable. See the bundled [helper guide](local-agent/README.md).

### Existing direct bearer connection (fallback)

Preserve an existing working direct bearer connection if the user prefers it. The endpoint remains `https://video-studio-agent.life-efficient.chatgpt.site/agent`, using a private account token and the client's supported secret mechanism. This route does not use OAuth login. Token names must match the client's configured `bearer_token_env_var`; merely setting a terminal variable does not update an already running desktop process. Do not echo tokens or embed them in command arguments. Prefer the browser approval helper for new installations or repairs so users do not manage credentials manually.

### Existing managed app connection

If the registered Video Studio app is already available and connected, it remains supported. Use the person's own normal Connect flow when needed. Website sign-in alone does not authorize the agent. An unavailable optional app does not prevent the personal-token route.

### Verify the connection

Discover tools, including lazy-loaded tools where supported. Run actual read-only `list_channels` and `list_videos` calls, filtering videos with an accessible `channelId`. Confirm editing tools such as `prepare_edit` are available without calling them on a real video during setup.

Distinguish failures:

- Helper credential missing or expired: run `connect` again and complete browser approval. A locked OS store requires unlocking that store. For a deliberately retained direct bearer connection, inspect its exact configured environment variable separately.
- HTTP 401: the credential is missing, expired, invalid, or revoked. Run the helper's `connect` flow again; do not request a token in chat.
- HTTP 403: the account lacks Studio permission. Report the access error for the owner to review.
- Connected but tools absent: inspect tool discovery and the actual error. Refresh or start a new chat only after a connection or package change. Do not prescribe repeated restarts.
- Network failure: report the inaccessible host separately from authentication.

If a new chat is unavoidable, give one short continuation prompt with the verified setup state and remaining check. Do not rerun unchanged successful local checks merely because the chat changed. Successful authenticated use automatically renews the connection to a rolling 90-day expiry, with renewal written at most once daily. The agent keeps the same secret. An unused connection expires, and you can revoke it from Studio; never describe installation alone as a successful account connection.

## 3. Check local rendering

Run the installed `$video-studio-setup` skill. Locate the runner relative to that installed package and discover Python 3.9 or newer, FFmpeg, and FFprobe. On Windows use a verified `py -3` or `python` interpreter and ensure the editing client receives the updated PATH. Use the person's approved installation method for missing tools; ask only for permissions or choices that actually require the user.

Run the synthetic rendering check in a new empty writable folder outside the plugin. Inspect its output and frame without playing media. A previously verified render may be reused when the same machine, tools, and configuration are unchanged.

## 4. Report readiness

Report success only after the installed plugin, actual account/tool access, and local rendering are verified. Briefly state which Studio organizations are accessible and whether editing tools are available. If blocked, give the exact failing stage and the single next action, distinguishing it from checks already passed.

Setup does not authorize downloading, editing, uploading, archiving, or publishing a real video. Wait for the user's project request before doing production work.
