# Video Studio plugin

Edit videos locally and return versioned exports and editable projects to shared Studio review.

## Install

For agent-led installation, follow the maintained [setup guide](SETUP.md). The same guide is published at `https://github.com/life-efficient/video-studio-plugin/blob/main/SETUP.md`.

Add the public marketplace with `codex plugin marketplace add life-efficient/video-studio-plugin`. Refresh or restart the desktop client, select the **Video Studio** plugin source, install **Video Studio**, and connect your own Studio account. Run `$video-studio-setup` in a new chat.

The client downloads the skills and runner from this repository, so no ZIP transfer is needed. Account permissions determine which videos you can edit. See [the marketplace guide](https://github.com/life-efficient/video-studio-plugin#readme) for installation and updates.

## Windows setup

### Updating an installation with missing Studio tools

Version 0.1.1 uses the registered Studio app for authentication. A successful local rendering check does not establish that the account connection works.

```powershell
codex plugin marketplace upgrade video-studio-team
codex plugin add video-studio@video-studio-team
```

Verify the installed version is 0.1.1 or newer, then use **Connect** for the required Video Studio app in plugin settings. Open a new chat after updating/connecting and run `$video-studio-setup`. If the app is unavailable or Connect fails, report the exact stage and sanitized error. Do not send access tokens, callback URLs, authorization codes, or passwords. Repeated restarts cannot supply a missing connection or OAuth client.

The registered app must be available to the signed-in account, and Studio permissions still apply. Availability on another person's account must be verified there.

A normal installation uses the client's installed plugin copy. It does not need symlinks, Developer Mode, administrator access for skill links, or a checkout of the application source.

1. Install the plugin from the marketplace above. Run `$video-studio-setup` so the assistant locates its installed plugin folder and checks the computer. Keep editing workspaces outside that folder. The manual commands below use `$StudioPlugin` for that installed plugin folder.
2. Check for Python in PowerShell:

   ```powershell
   Get-Command py, python -ErrorAction SilentlyContinue
   py -3 --version
   ```

   Use Python 3.9 or newer. If the `py` launcher is unavailable but `python --version` reports a suitable version, use `python` in place of `py -3` in the commands below. A Windows App Execution Alias that opens the Store is not an installed Python interpreter.
3. Install FFmpeg and FFprobe through the computer's approved software route. Both `ffmpeg.exe` and `ffprobe.exe` must be available on `PATH`. After changing `PATH`, restart the terminal and the editing client so they receive the updated environment. Verify:

   ```powershell
   Get-Command ffmpeg, ffprobe
   # Set $StudioPlugin to the installed plugin folder found during setup.
   py -3 "$StudioPlugin\packages\local-runner\video_studio.py" doctor
   ```

4. Run the synthetic check in a new empty folder. Use a new folder name if that location already contains files:

   ```powershell
   $StudioSmoke = Join-Path $env:USERPROFILE 'Documents\VideoStudio\smoke-check-01'
   py -3 "$StudioPlugin\packages\local-runner\video_studio.py" smoke --workspace "$StudioSmoke"
   ```

   Inspect the generated frame and returned checks without playing the video. Then sign in with the editor's own Studio account and run `$video-studio-setup` to prepare an authorized project. Normal editing workspaces should remain outside the plugin folder.

The extracted-package tests were run in isolated workspaces on macOS. These instructions do not establish a Windows test result. Complete the dependency and synthetic checks on the actual Windows computer, then verify one real edit and feedback revision before considering that editor's installation ready.

## First use

1. Run `$video-studio-setup` to verify Python 3.9 or newer, FFmpeg, FFprobe, account access, and a small synthetic render. Project-specific renderers may require Node or additional packages.
2. Choose a video you are authorized to edit. The assistant prepares a writable workspace with the script, source recordings, feedback, and the latest editable baseline where available.
3. Ask for a new edit with `$edit-video`, or apply review comments with `$iterate-video-edit`. `$face-camera-recording-script` prepares spoken copy before recording.
4. The assistant preserves a versioned editable snapshot, renders locally, reviews silently, and uploads a new iteration for review. Previous versions remain available.

Original recordings, reference clips, fonts, and project assets are fetched from authorized project sources; they are not bundled with the plugin. A first edit needs supplied footage and references. A revision needs the matching editable baseline. Legacy exports without that baseline need an explicit recovery step before they can be faithfully revised.

## Credentials and local files

Sign in through the Studio MCP connection. Production transfer sessions are limited to the selected video and expire. Store a session response only in a private local file and keep it out of snapshots, source control, and chat. Never distribute service credentials.

The local runner supports direct session transfers where the hosting environment accepts them. If the host requires its outer authenticated MCP connection, the assistant uses that connection to prepare a local manifest and fetch assets, then uploads the runner's delivery plan through the same connection. See [runner instructions](packages/local-runner/README.md) for supported commands and transfer details.

Rendering occurs on the editor's computer. This release does not provide cloud rendering or automatically install project-specific rendering frameworks. Verify the actual first project after the synthetic setup check.
