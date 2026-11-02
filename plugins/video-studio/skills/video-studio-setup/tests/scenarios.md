# Setup behavior checks

These scenarios assess the workflow instructions, not a live second-machine certification.

1. Positive: "Install Video Studio on my new editing laptop."
   - Select video-studio-setup; verify package location, own account, dependencies, and synthetic render before preparing a writable project.
2. Negative: "Write a face-camera script for this topic."
   - Select face-camera-recording-script; do not configure production sessions or render.
3. Adjacent: "Apply the comments on the latest edit."
   - Select iterate-video-edit. Use setup only if dependencies or access are missing; do not treat setup as the edit itself.
4. Cached install: The plugin lives in a read-only client cache.
   - Keep edits outside the plugin. Resolve bundled runner and helpers from the installed package, with no repository or personal paths.
5. Existing local skill: An unrelated folder occupies iterate-video-edit.
   - Refuse replacement by default; explicit backup mode moves the entire folder to a recoverable backup before linking. Never replace the user's whole skill directory.
6. Hosted outer authentication: A short-lived session receives an authentication error at the hosting edge.
   - Use authenticated MCP tools to bridge downloads and upload plans. Do not request a service key or copy a browser cookie.
7. Missing legacy baseline: A video export exists without editable sources.
   - Report the specific missing baseline and resolve recovery before claiming a faithful revision. Do not silently rebuild the video.
8. Windows interpreter: `python3` is missing, but the Python launcher is installed.
   - Verify `py -3 --version` is 3.9 or newer and invoke the quoted runner path with `py -3`. Do not assume a missing `python3` command means Python is unavailable.
9. Windows copied install: The editor has no symlink privileges and FFmpeg was just added to PATH.
   - Use the normal copied plugin. Restart the editing client so it receives PATH, then verify both FFmpeg and FFprobe and run the synthetic check. Do not enable Developer Mode or request administrator privileges for ordinary skill installation.
10. Skills-only success: Local doctor and synthetic render pass, but no Studio tools appear after a restart.
    - Do not rerun the render as an account test. Inspect the installed version and required app mapping, classify connection state using available evidence, update 0.1.0 to 0.1.1 or newer, and complete the registered app connection if available. Do not keep prescribing restarts or invent OAuth client IDs.
11. Registered app unavailable: The package contains the correct app mapping, but the person's account cannot access that app.
    - Report the unavailable dependency and sanitized error for the owner to resolve. Do not claim the public source grants account access, request a service credential, or weaken Studio authentication.
12. Setup-only permission boundary: Account discovery succeeds and the synthetic test passes.
    - Report verified access and local readiness without preparing, downloading, editing, uploading, or publishing a real video. A named project request is needed before the project workflow.
