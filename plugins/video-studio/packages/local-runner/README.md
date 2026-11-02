# Video Studio local runner

The runner prepares local editing workspaces, preserves editable versions, verifies renders, and transfers finished iterations through Video Studio. It uses Python 3.9+ and the standard library. FFmpeg and FFprobe are required for rendering checks. Projects using a Node renderer also need Node/npm and their own locked dependencies.

On Windows, use `py -3` or the installed `python` executable in place of `python3` below. Quote paths containing spaces. The runner accepts Unicode filenames and spaces, and rejects Windows device names, trailing filename dots/spaces, control characters, alternate data streams, and case-insensitive path collisions. These portability checks run on every operating system.

Run commands from any directory, using the installed plugin's path:

```sh
python3 /path/to/video-studio/packages/local-runner/video_studio.py doctor
python3 /path/to/video-studio/packages/local-runner/video_studio.py smoke --workspace /path/to/new-smoke-workspace
```

`smoke` generates one second of synthetic video with a silent audio track, verifies its dimensions and duration, and extracts a PNG. It does not play media. It does not establish that a particular project's fonts, dependencies, or renderer work.

## Download through the authenticated MCP connection

This is the default transport, including on hosts whose outer sign-in gateway prevents direct API access. The agent uses the user's authenticated Video Studio connector. No browser cookies or service credentials are needed.

1. Call `prepare_edit({videoId})` through the connector and save the returned JSON to `manifest.json`. Keep download staging separate from the editable workspace.
2. Initialize staging:

   ```sh
   python3 /path/to/video_studio.py stage --manifest /path/to/manifest.json --workspace /path/to/download-staging
   ```

3. For each manifest file, call `read_edit_file_chunk({videoId,fileId: file.id,offset:0,length:1048576})`. Feed its JSON result directly to the runner on standard input:

   ```sh
   python3 /path/to/video_studio.py receive --workspace /path/to/download-staging --file FILE_ID < /path/to/chunk-result.json
   ```

   The input may be the decoded tool value, a JSON-RPC response, or the connector's `content`/`structuredContent` result. Capture chunk results programmatically into local files or stdin. Do not print media base64 into the conversation. The runner returns only `nextOffset`, completion, and a checksum. Request the next chunk at that offset until complete. Chunks must arrive in order; mismatched offsets are rejected. Keep a failed partial transfer for an explicit retry or remove it before restarting from zero.

4. Verify and prepare the downloaded files:

   ```sh
   python3 /path/to/video_studio.py prepare --manifest /path/to/manifest.json --assets /path/to/download-staging --workspace /path/to/edit
   ```

The result contains `studio-project.json` and all manifest assets at their relative paths. Files with `kind: snapshot` are portable ZIP snapshots. Restore the latest snapshot to a new editable directory before revising it. Legacy `kind: project` files may require a project-specific correspondence check before being treated as an existing version's baseline.

## Preserve and continue an editable version

Keep render outputs and caches separate from the editable source folder. Put the timeline, code, assets, dependency lockfiles, and render configuration in that source folder. The snapshot excludes dependency caches such as `node_modules`; dependencies must be reproducible from lockfiles. Credentials and symlinks cause a snapshot error.

```sh
# For a downloaded latest snapshot, install its complete baseline first:
python3 /path/to/video_studio.py import-version --snapshot /path/to/edit/snapshots/v001.mp4.snapshot.zip --workspace /path/to/edit --version v001
# For a first edit, preserve the completed project instead:
python3 /path/to/video_studio.py snapshot --workspace /path/to/edit --version v001 --project /path/to/edit/current-project
python3 /path/to/video_studio.py verify --workspace /path/to/edit --version v001
python3 /path/to/video_studio.py restore --snapshot /path/to/edit/versions/v001/snapshot.zip --workspace /path/to/edit/next-project
```

Run `import-version` only for a downloaded existing iteration, or `snapshot` for a newly completed first edit. They both create `versions/v001`; choose the applicable command, not both. `import-version` checks the archive against the prepared Studio file checksum and latest iteration number, and installs all files needed for future parent verification.

Edit only `next-project`. Never edit the preserved `versions/v001/project`. After rendering the revision, preserve `next-project` as `v002` with `--parent v001`. Snapshot creation checks that the preserved parent is unchanged. It creates both `versions/vNNN/project/` and `snapshot.zip`, with a checksum manifest. Restore checks paths and all file checksums, then writes to an empty destination. It never runs downloaded code. Inspect a restored project before installing dependencies or running its renderer.

Large original footage may be referenced from the prepared workspace instead of duplicated in every version. Record the relative paths and SHA-256 values in the editable project, and ensure all referenced source assets remain available in Studio. The runner verifies archived files; it cannot infer a renderer's external asset dependencies.

## Upload through the authenticated MCP connection

Create a delivery plan after preserving the completed editable project:

```sh
python3 /path/to/video_studio.py deliver --workspace /path/to/edit --version v001 --export /path/to/final.mp4 --export-name v001.mp4 --notes "Describe the changes and why they were made." --recording SOURCE_TAKE_ID --plan-only
```

Use the source take's stable 32-character ID, not the `source:...` transfer file ID. Repeat `--recording` for every take actually used. Omit it when no recorded take was used. Add each additional used source clip with `--clip '{"id":"stable-project-clip-id","label":"Readable clip name"}'`; clips-only and generated-only edits may leave recorded takes empty. Do not list unused references. Version numbers must be the next Studio iteration number. The runner verifies the immutable snapshot and checks the export's actual duration using FFprobe. It writes `versions/v001/upload-plan.json`, containing the `begin_edit_upload` arguments and absolute local asset paths. This is a plan, not a completed upload. The plan contains a stable `requestId`; retries reuse it.

The agent then:

1. Calls `begin_edit_upload(plan.arguments)` through the authenticated connector. Save `uploadId` and `partBytes` from the response.
2. For both `video` and `snapshot`, produce sequential parts beginning at 1, using the server's exact `partBytes` value. R2 multipart storage requires full 8 MiB nonfinal parts.

   ```sh
   python3 /path/to/video_studio.py upload-part --plan /path/to/edit/versions/v001/upload-plan.json --upload-id UPLOAD_ID --asset video --part-number 1 --part-bytes 8388608 --output /path/to/part-arguments.json
   ```

   Read the generated JSON programmatically and pass it directly as `write_edit_upload_part` arguments through the connector. Do not expose the base64 in chat. `--output` returns a small summary. Without `--output`, stdout is the tool argument JSON and must be captured, not displayed. Calculate the number of parts as `ceil(asset size / partBytes)`. The final part may be smaller. The runner refuses changed upload inputs. Retry the same upload ID and part number after an interrupted transfer.
3. Calls `complete_edit_upload({videoId,uploadId})` after both assets are uploaded. Verify the returned export name, version, snapshot checksum, and review status against the plan.
4. Reads `list_video_exports` back to confirm the saved iteration and change notes. Keep the local editable versions for future revisions.

An authenticated connector's transport must support the server's 8 MiB part size. If the client cannot pass that size without truncation, stop with that specific transport limitation. Do not substitute a service credential or expose transfer data in chat.

## Optional direct session transport

On a host that accepts bearer-authenticated editing requests without a separate sign-in gateway, call `create_edit_session({videoId})` through the connector. Save its response in a private local file:

```json
{"endpoint":"https://studio.example/api/editing","token":"SCOPED_SESSION_TOKEN","expiresAt":"2030-01-01T00:00:00.000Z"}
```

On Unix, set file permissions to `600`. The runner rejects expired or world-readable session files and credential-bearing URLs. Never put the token in a command argument, source control, logs, or the conversation. Alternatively set `VIDEO_STUDIO_EDIT_TOKEN` privately and supply `--endpoint`.

```sh
python3 /path/to/video_studio.py --session-file /path/to/private-session.json prepare --video VIDEO_ID --workspace /path/to/edit
python3 /path/to/video_studio.py --session-file /path/to/private-session.json deliver --workspace /path/to/edit --version v001 --export /path/to/final.mp4 --notes "Describe changes." --recording SOURCE_TAKE_ID
```

Direct delivery performs the upload loop programmatically and validates the returned snapshot checksum. Session files are not needed for connector-mediated transfers. Refresh an expired session through the authenticated connector.

## Verification

```sh
python3 -m unittest discover -s /path/to/video-studio/packages/local-runner -p 'test_*.py' -v
```

Tests cover portable Windows path validation and case collisions, an 8 MiB multipart boundary, a second-machine baseline import and revision, a synthetic render, verified snapshot restore, rejected traversal and secrets, preserved-parent drift, connector-staged downloads, upload chunk integrity, and a local JSON-RPC fixture. They do not demonstrate access from a second physical machine or a hosted production upload.
