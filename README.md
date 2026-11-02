# Video Studio plugin

Skills and a local editing runner for Video Studio, distributed through a Git-backed plugin marketplace.

## Install

Add this marketplace in Codex:

```sh
codex plugin marketplace add life-efficient/video-studio-plugin
```

Refresh or restart the desktop app, open the Plugins directory, select the **Video Studio** source, and install **Video Studio**. Connect your own Studio account, then run `$video-studio-setup` in a new chat.

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
