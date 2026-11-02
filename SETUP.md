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

Verify the installed package version matches the current published version. A refreshed catalog is not proof that the installed copy updated. The package includes `plugin.json`, `.codex-plugin/plugin.json`, `.app.json`, skills, and a local runner. Its required registered Video Studio app provides authenticated MCP tools. Do not add a second standalone OAuth server from the raw MCP URL.

For another agent, check whether it can load these skills and authorize the registered app before configuring anything. If it cannot, report that precise compatibility limit. Do not claim the raw MCP URL alone is a working connection.

## 2. Connect the user's account

Open the required Video Studio app's normal **Connect** flow using the person's own authorized account. Website sign-in and agent authorization are separate. If user action is necessary, open the relevant screen when supported and ask for the single sign-in or consent action. Never ask for credentials in chat or copy credentials from another account or browser.

Discover the app's tools, including lazy-loaded tools where supported. Verify access with actual read-only `list_organizations` and `list_videos` calls. Confirm editing tools such as `prepare_edit` are available without calling them on a real video during setup.

If blocked, distinguish:

- Missing required app: verify the installed package mapping and version.
- App unavailable to this account: report the exact app availability error for the Studio owner to resolve.
- Sign-in required or HTTP 401: complete normal authorization.
- Access denied or HTTP 403: report the account access error; do not alter permissions or weaken authentication.
- Connected but tools absent: inspect the client's tool inventory and actual error. Refresh or start a new chat only after a connection or package change. Do not prescribe repeated restarts.

If a new chat is unavoidable, give the user one short continuation prompt with the verified setup state and the remaining check. Do not rerun successful unchanged local checks merely because the chat changed. Keep callback URLs, authorization codes, tokens, and credentials out of reports.

## 3. Check local rendering

Run the installed `$video-studio-setup` skill. Locate the runner relative to that installed package and discover Python 3.9 or newer, FFmpeg, and FFprobe. On Windows use a verified `py -3` or `python` interpreter and ensure the editing client receives the updated PATH. Use the person's approved installation method for missing tools; ask only for permissions or choices that actually require the user.

Run the synthetic rendering check in a new empty writable folder outside the plugin. Inspect its output and frame without playing media. A previously verified render may be reused when the same machine, tools, and configuration are unchanged.

## 4. Report readiness

Report success only after the installed plugin, actual account/tool access, and local rendering are verified. Briefly state which Studio organizations are accessible and whether editing tools are available. If blocked, give the exact failing stage and the single next action, distinguishing it from checks already passed.

Setup does not authorize downloading, editing, uploading, archiving, or publishing a real video. Wait for the user's project request before doing production work.
