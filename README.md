# Video Studio plugin

Skills and a local editing runner for Video Studio, distributed through a Git-backed plugin marketplace.

## Install

For agent-led setup, copy the prompt from the Studio web app or ask your agent to follow [SETUP.md](SETUP.md). It manages installation, updates, connection checks, and local rendering checks. The copied instructions include your personal connection token; keep them private.

Add this marketplace in Codex:

```sh
codex plugin marketplace add life-efficient/video-studio-plugin
```

Refresh or restart the desktop app, open the Plugins directory, select the **Video Studio** source, and install **Video Studio**. Copy **Connect your agent** instructions from your signed-in Studio account to configure personal-token access, then run `$video-studio-setup`. An existing working managed app connection remains supported.

If the command is unavailable, ask Codex to add `https://github.com/life-efficient/video-studio-plugin` as a plugin marketplace using its supported local setup. Installing the source alone does not connect your account or grant video access.

The plugin includes setup, first-edit, revision, and recording-script skills. Rendering runs locally. Python 3.9 or newer, FFmpeg, and FFprobe are required. Project-specific renderers can require additional dependencies. Normal Windows installation needs no symlinks.

## Test

Run setup, create a new iteration for an authorized test video, add one review comment in Studio, then use a fresh chat and empty workspace to recover the editable snapshot and deliver a revision. Keep original recordings and earlier versions intact.

The package was tested using synthetic media and isolated editing workspaces on macOS. A real Windows edit and revision remain the Windows acceptance check.

## Updates

```sh
codex plugin marketplace upgrade video-studio-team
```

Refresh the client and install or refresh the offered plugin version. Updates do not change Studio permissions.

## Included files

The installable plugin is under `plugins/video-studio/`. Its [Windows and runner guide](plugins/video-studio/README.md) covers local dependencies and the editing workflow.

Recordings, production projects, credentials, and reference footage are not included. Studio data remains protected by sign-in and project permissions.

## Personal-token connection in 0.1.3

Version 0.1.3 supports a separate bearer-authenticated agent endpoint. The registered Studio app is optional. Copy connection instructions from your own signed-in Studio account and follow [SETUP.md](SETUP.md). The public repository contains no tokens and installation alone grants no video access.

Refresh the marketplace and update the installed plugin:

```sh
codex plugin marketplace upgrade video-studio-team
codex plugin add video-studio@video-studio-team
```

Verify the installed version matches the current release. Local rendering success does not prove account authorization. The agent must verify actual read-only Studio tools. Do not share credentials in diagnostic reports or repeat restarts without a connection change.

Other agents can use the same endpoint with their supported HTTP MCP bearer-token configuration and private secret storage. The personal-token endpoint does not use OAuth login.
