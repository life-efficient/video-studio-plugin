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

### Personal-token connection

Use the signed-in website's **Connect your agent** popover. It creates this person's token and includes it in the copied instructions. The public guide and plugin never contain a token. If none was supplied and no working connection exists, ask the user to copy fresh instructions from their own Studio account. Do not request their password or reuse another person's credentials.

Configure a Streamable HTTP MCP server at:

```text
https://video-studio-agent.life-efficient.chatgpt.site/agent
```

For Codex, merge this entry into its existing user configuration, preserving unrelated entries:

```toml
[mcp_servers.video_studio]
url = "https://video-studio-agent.life-efficient.chatgpt.site/agent"
bearer_token_env_var = "VIDEO_STUDIO_ACCESS_TOKEN"
```

Store the supplied secret as the user's private `VIDEO_STUDIO_ACCESS_TOKEN` environment variable using the platform's supported secure mechanism, and ensure the Codex process inherits it. On Windows, a user-scoped environment setting affects newly launched processes; a terminal's temporary variable does not update an already running desktop client. Do not put the literal token in TOML, shell arguments/history, reports, screenshots, source control, or project snapshots. User environment variables are credentials, not encrypted storage. Prefer an existing credential store or client secret integration where supported. Redact the copied secret from all diagnostic output.

This endpoint uses bearer authentication. Do not run `codex mcp login`, start an OAuth flow, or reuse the original website `/mcp` URL for this token. If changing an existing failed entry, preserve other working servers and avoid duplicate names. For another agent, use its supported HTTP MCP bearer-header configuration with equivalent private secret storage.

### Existing managed app connection

If the registered Video Studio app is already available and connected, it remains supported. Use the person's own normal Connect flow when needed. Website sign-in alone does not authorize the agent. An unavailable optional app does not prevent the personal-token route.

### Verify the connection

Discover tools, including lazy-loaded tools where supported. Run actual read-only `list_organizations` and `list_videos` calls. Confirm editing tools such as `prepare_edit` are available without calling them on a real video during setup.

Distinguish failures:

- Missing environment variable: configure the user's secret and ensure the agent process receives it.
- HTTP 401: the token is missing, expired, invalid, or revoked. Generate fresh instructions in Studio.
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
