---
name: iterate-video-edit
description: Revise an existing Video Studio edit using the user's review comments while preserving everything outside the requested changes. Use for requests to iterate a video edit, apply edit feedback, or work on the next video ready for editing. Prefer this over edit-video for feedback-led iterations; use edit-video for a new edit or an explicitly requested full redesign. Do not use for script-only revisions or app development.
---

# Iterate Video Edit

Apply review feedback to an existing video without changing anything the user did not comment on.

## Contract Checklist

- Work on the latest iteration of the selected video; earlier versions are references, not replacement baselines.
- Only make changes requested by the user's comments or explicit instructions. Leave other scenes, visuals, fonts, audio, and timing intact.
- Keep every delivered iteration in its own version folder with its export and a recoverable editable snapshot. Start the next iteration by copying that snapshot into a new folder. Never edit a delivered snapshot in place.
- Follow current Studio conventions rather than assuming API routes, storage paths, or field names.

## Workflow

1. Select the next iteration.
   - If the user names a video or version, follow that instruction. Otherwise choose the video waiting longest in the ready-for-editing queue, and iterate its latest version. The equivalent status may be called “Needs editing”. Use the time it became ready, not its original creation date. If that timestamp is unavailable, use the oldest feedback timestamp and disclose the fallback.
   - If this computer is not configured, run `$video-studio-setup`. Read current Studio instructions and inspect its live state. If nothing is ready, report that rather than treating any commented video as authorized for editing.
   - Anti-patterns: editing a superseded version by default, choosing the newest arrival over the oldest waiting video, guessing review completion from comment presence.

2. Resolve the feedback into a bounded change list.
   - Read all comments attached to the selected iteration, including whole-video comments and references to earlier versions. Inspect each referenced version and region so “this was better” refers to the actual treatment the user selected.
   - Match every planned change to a comment. A whole-video comment permits only the change it describes, not an unrelated redesign. Ask a focused question only if conflicting or ambiguous feedback prevents a faithful edit.
   - Anti-patterns: interpreting reference timestamps against the current version, silently broadening feedback, substituting personal taste for the user's direction.

3. Copy the baseline into a new version folder before editing.
   - Use the packaged runner and [production handoff](../edit-video/references/studio-handoff.md) to prepare the authorized video in a writable workspace outside the plugin. Locate the editable snapshot corresponding to the latest delivered iteration. Use one folder per version within the video workspace, for example `versions/v003/` and `versions/v004/`; follow an existing equivalent convention rather than relocating old work. Never overwrite or reuse an existing version folder.
   - Copy the baseline project into the new folder, including timeline, layers/tracks, editing code, styles, fonts, assets, render settings, and dependency lockfiles needed to reproduce it. Do not use hard links or writable symlinks for editable files. Large original footage may remain shared through stable references if its identity is recorded and it is never modified.
   - Record which Studio iteration/export each snapshot belongs to, its parent version, the project entry point, and the referenced source files. Use current Studio metadata where supported, otherwise keep a small manifest alongside the snapshot. Compare file hashes to verify the copied editable inputs match before making changes. Keep renders and caches out of the preserved baseline.
   - If a legacy edit has no snapshot, preserve its existing editable project before touching it and verify that it corresponds to the delivered baseline. If that correspondence cannot be established, report the gap rather than claiming the export alone is an editable snapshot or silently rebuilding it.
   - Anti-patterns: editing the only project copy, changing files shared with older versions, preserving only an MP4, labeling unrelated current sources as an old snapshot.

4. Make the requested edits.
   - Work only in the new copy, reusing its assets, typography, scene structure, and settings. For feedback referencing an older edit, read that version’s preserved snapshot and copy only the requested elements into the new project; never modify the old snapshot. Use the installed edit-video skill for relevant tooling, silent review, and delivery mechanics; its new-edit design workflow is not permission to restyle this iteration.
   - Do not change anything that was not commented on. In particular, no unsolicited font substitutions, visual polish, new transitions, branding refreshes, music changes, or rewrites. If a requested change necessarily affects adjacent timing, limit the adjustment to that dependency and record why. If unrelated content cannot be preserved, stop and explain before broadening the edit.
   - Mark work as started using the Studio's current workflow. Preserve the user's comments and history.
   - Anti-patterns: rebuilding the film from scratch, changing shared styles that alter untouched scenes, silently replacing missing fonts or assets.

5. Verify and deliver the new iteration.
   - Review the source diff against the copied baseline: every substantive change must map to feedback or a documented necessary dependency. Recheck baseline hashes to confirm the old snapshot was not changed.
   - Compare the render with the baseline using silent frames/contact sheets, checking both the requested fixes and untouched regions. Account for timestamp shifts caused by requested cuts; check typography, layout, assets, audio configuration, and transitions for unintended changes. Do not play media unless specifically authorized.
   - Register the new iteration through the current Studio workflow, ready for review. Record what changed and why, the feedback addressed, any necessary dependent timing changes, and the footage actually used. Read back the saved iteration and its snapshot mapping. Retain the new version folder as its immutable baseline for the next edit, preserving all previous versions and feedback.
   - Anti-patterns: checking only changed scenes, overwriting the baseline, inventing completion timestamps, marking unresolved feedback as addressed.

## Anti-Patterns

- Treating an iteration as an opportunity to improve the whole video.
- Following general style guidance over the user's specific preservation constraint.
- Baking implementation-specific endpoints or storage schemas into this skill.

## Output

Identify the video and new iteration, briefly list feedback addressed, link the delivered edit, identify its preserved snapshot and parent version, and disclose any unresolved comments or verification limits. Confirm preservation only to the extent checked.
