# Local checkout handoff

For local Video Studio edits, the Editing view reads `GET /api/ideas/<idea-id>/exports`. The current local implementation registers completed files in `work/video-edits/<idea-id>/exports/manifest.json`.

1. Confirm the idea ID and current stage from the live board. Read the latest export’s feedback, including whole-video comments and `referenceExportName` comments whose times refer to an older version. Before starting an authorized revision, PATCH the latest export with `{"status":"editing"}` so the server records when editing began. Confirm the delivered scope and any unresolved issues to explain in the iteration notes.
2. Copy the completed media into that idea's `exports/` directory using a simple filename containing letters, digits, hyphens or underscores and `.mp4` or `.webm`. Preserve original recordings and previous versions.
3. Read the existing manifest and preserve other entries. Atomically write a JSON array with entries such as:

```json
[{"name":"edit-02.mp4","poster":"edit-02-poster.png"}]
```

Do not save `kind` or a descriptive iteration `label`: the stable studio version and change notes identify the iteration. `poster` is optional and names a PNG/JPG in the same directory. Use a representative actual rendered frame. Do not write a symlink or an arbitrary file path. Copy files completely before registering them.
4. Populate that iteration’s metadata through `PATCH /api/ideas/<idea-id>/exports/<filename>` with `Content-Type: application/json`:

```json
{
  "status": "needs_review",
  "delivered": true,
  "notes": "Replaced the opening with the new take and shortened the pause before the evidence, addressing the request for a faster, more direct hook.",
  "sourceTakeIds": ["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"],
  "sourceClips": [{"id":"project:street-wide-01","label":"Street wide shot"}]
}
```

Use actual IDs, not the illustrative values above. Read take IDs from `GET /api/ideas/<idea-id>/recordings`; include every take whose video or audio appears in this iteration. For other clips, use stable catalogue or project asset IDs and concise labels, with their provenance retained in the edit workspace. Multiple takes and clips may be used together. Empty arrays mean none used; do not assign every available take, assume the latest take, or count clips studied only as style references. Consult the running local API's current field descriptions; do not infer storage schema from this example.

Write `notes` when completing every iteration, rather than waiting for the user to fill it in. Use one concrete change per line so the app can present change bullets. Explain the changes and their evidence-backed reasons; for a first cut, explain the choices made. State partial scope or unresolved issues where relevant instead of adding a type or descriptive iteration label. Preserve user feedback already in the field and prior iterations. Avoid generic praise, fabricated rationale, or a claim that something changed when it did not. Read existing metadata before updating; send only the fields being changed.
Send `delivered: true` at handoff to record the server-owned delivery timestamp once. New iterations begin as `needs_review`. The reviewer changes the latest iteration to `needs_editing` when their comments are ready; never make that decision for them. Preserve historical statuses, feedback timestamps, and status events. Use the API for status changes so timestamps are server-recorded, not invented.

5. Read back `/api/ideas/<idea-id>/exports`; check the stable version, download name, byte size, notes, all source IDs, and media response (a range request is sufficient). Open the idea's Editing view without starting playback and verify the export card, visible source list, notes, and download link. Never click Play for verification.
Downloads use `[video title] v[studio version]` with the actual media extension. Read the version and `downloadName` from the live listing; never infer the version from a render filename or renumber older iterations.
6. Retain chat/repository download copies as useful handoffs, but do not treat those copies as proof of registration. Report any failure to attach or visually verify.

This file-based adapter is for the local app. For a hosted instance, inspect its supported persistent storage/upload path before transferring files. A local filesystem copy does not establish hosted availability. Never put edited exports in the original recordings collection to bypass a missing export route.
