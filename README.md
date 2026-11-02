# Video Studio plugin

Skills and a local editing runner for Video Studio, distributed through a Git-backed plugin marketplace.

## Install

For agent-led setup, copy the prompt from the Studio web app or ask your agent to follow [SETUP.md](SETUP.md). It manages installation, updates, connection checks, and local rendering checks. You may need to approve sign-in.

Add this marketplace in Codex:

```sh
codex plugin marketplace add life-efficient/video-studio-plugin
```

Refresh or restart the desktop app, open the Plugins directory, select the **Video Studio** source, and install **Video Studio**. Connect the required registered Video Studio app with your own Studio account, then run `$video-studio-setup` in a new chat.

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

## Connection repair in 0.1.1

Version 0.1.1 uses the registered Studio app through `.app.json`, with a compatibility manifest for older clients. It removes the standalone OAuth binding from 0.1.0, which did not supply a registered OAuth client.

Refresh the marketplace and update the installed plugin:

```sh
codex plugin marketplace upgrade video-studio-team
codex plugin add video-studio@video-studio-team
```

Verify version 0.1.1 or newer in plugin settings, complete **Connect** for the required app, then start a fresh chat and run `$video-studio-setup`. Local rendering success does not prove account authorization. If the app is unavailable to your account or sign-in fails, report the exact stage and sanitized error. Do not share credentials or repeat restarts without a connection change.

This distribution targets supported Codex/ChatGPT clients with registered app connections. Other agents need their own supported authentication configuration; a raw MCP URL alone does not establish a usable OAuth client.
