---
name: edit-video
description: Edit or rebuild a video from supplied footage or audio using the requested style and references. Use for complete edits, revisions, motion graphics, and requested captions. For writing a recording script, use face-camera-recording-script; for standalone contact-sheet extraction without editing, use contact-sheet-keyframes.
---

# Edit Video

Complete a reference-grounded video edit, using internal rendered checks to verify the visual direction before expanding it into a full film.

## Contract Checklist

- Preserve the approved recording, wording, and intended meaning unless changes are authorized.
- Inspect actual reference frames before choosing the visual system. A style name, written summary, font, or palette is not sufficient evidence.
- Map each major treatment to a reference passage and explain how its composition and motion serve this narration.
- Render and compare a representative opening before producing the full edit. Resolve material style mismatches first.
- Carry an authorized full edit through revision, final review, and delivery. Style rejection or corrective feedback does not create a user approval checkpoint; stop at a sample only when the user explicitly requests sample-only work or a pause for feedback.
- Verify both visual fidelity and technical quality; passing export checks does not establish a style match.
- Review silently through timestamped contact sheets. Playback requires a direct user request for that specific media.
- Keep narration captions off unless requested.
- Preserve a portable editable snapshot and its asset identities for every delivered version. Never include session credentials in a snapshot.
- Register every delivered iteration on the matching Video Studio idea with AI-written change notes and all takes/clips actually used; a file in `outputs/` alone is not a completed handoff.

## Workflow

1. Establish the brief and source boundaries.
   - Follow any workspace `AGENTS.md`. Resolve the plugin root from this skill and use a writable edit workspace outside an installed plugin. In a source checkout, retain the existing ignored `work/video-edits/<edit-id>/` and `outputs/` conventions. If the machine is not configured, run `$video-studio-setup`.
   - Confirm approved footage, script, requested style, duration, and channel brand/assets in Video Studio. Apply branding loosely where appropriate without altering source evidence.
   - Preserve originals and record source provenance. Separate authentic evidence, contextual photography, and illustrative/generated props.
   - Anti-patterns: replacing approved delivery, fabricating incident evidence, forcing a brand template onto every scene.

2. Study the reference's actual visual language.
   - Use the project's supplied or authorized reference library (a source checkout may have `CATALOGUE.md`); the plugin does not distribute third-party reference footage. Select passages relevant to the intended beats, and extract timestamped sheets at 0.25–0.5-second intervals, denser around cuts or fast motion. Inspect larger frames for detail.
   - Record reference file and timestamps plus concrete observations: asset medium, object scale/crop, depth and layering, background texture, typography, source-document treatment, camera movement, entrances/exits, and timing relative to narration.
   - Create a short beat map: narration/time range, reference passage, observed mechanism, proposed assets/composition/motion. Distinguish observed features from your proposed adaptation.
   - If reference frames are inaccessible, report that limitation and resolve it before claiming fidelity. Do not silently substitute a generic style.
   - Anti-patterns: treating catalogue descriptions as visual inspection, matching only colors and fonts, assuming any animation matches a motion reference.

3. Design scenes from the reference mechanisms.
   - Use the observed asset medium and composition deliberately. A photographic editorial collage calls for photographic objects/cutouts, layered source material, deliberate scale/crops, and timed reveals, rather than automatically substituting vector icons, schematic diagrams, dashboards, or text cards.
   - These are conditional choices, not a universal house style: use diagrams or icons when the brief/reference supports them. Do not turn this example into a mandatory laptop, cash stack, serif font, or monochrome preset.
   - Tie meaningful composition changes to narration beats. Changing an overlay on the same dominant prop is not enough when the reference changes the scene's visual focus.
   - Use actual source clippings for evidence. Never fabricate an email, call interface, or incident photograph and present it as authentic. Record generated props as illustrations.
   - Keep text purposeful; avoid redundant narration titles, routine eyebrow labels, and corner credits unless requested, necessary for understanding, or required for attribution.
   - Anti-patterns: generic icons replacing photographic references, one repeated layout for unrelated beats, decorative motion with no narrative function, invented evidence.

4. Validate the direction on an actual rendered sample.
   - Render a representative opening, usually 15–25 seconds, covering more than one visual mechanism and at least one transition. Judge rendered frames, not just a storyboard or code.
   - Make a side-by-side reference/output comparison and evaluate it using the Visual Fidelity Gate below. Revise material failures before building the rest.
   - Perform this checkpoint autonomously, including after rejected styling or corrective feedback. Fix failures, compare again, and continue the authorized full film without waiting for approval.
   - Stop after delivering a sample and silent sheets only when the user explicitly requests sample-only work or says to pause for feedback before continuing. A request to show progress or a preview during an authorized full edit does not by itself cancel the remaining work.
   - Anti-patterns: rendering the whole film before testing the direction, declaring success because assets are photographic, claiming a match without frame comparison, treating style rejection as a mandatory feedback stop.

5. Extend and review the complete edit.
   - Carry the validated visual grammar across the film while varying treatments with the story. Revisit the beat map for each new section instead of repeating the opening template.
   - Extract fine-grained timestamped sheets across the entire final render, with larger frames for text/detail and denser samples around transitions. Check the Visual Fidelity Gate as well as clipping, overlap, safe margins, contrast, missing assets, and timing.
   - Assess audio silently with transcripts, waveform, loudness, and clipping checks. Do not claim a listening review from these checks.
   - Never open/play video or audio for research or review, or launch media URLs/preview pages that may autoplay. If timing is uncertain, extract denser frames rather than starting playback.
   - Anti-patterns: checking only attractive hero frames, treating technical validity as style approval, unexpected audio playback.

6. Deliver the appropriate artifact.
   - For a Video Studio edit, preserve the project with the packaged local runner, then follow [Studio handoff](references/studio-handoff.md) to register the export on the exact idea, then read back its media listing and verify the Editing view silently. Keep the idea in Editing unless a later stage is authorized.
   - Populate the iteration’s single notes field yourself with concrete changes and why they were made, including relevant user feedback. For the first cut, describe the editing choices and rationale. Preserve existing user notes; never invent feedback or motivations. Record every used take/clip, including when a revision switches or combines sources.
   - Identify iterations by their stable studio version and concrete change notes. Do not save an iteration type (`kind`) or descriptive iteration `label`. Explain partial scope or unresolved issues in notes and the handoff; never present a rejected full edit or short sample as the completed film.
   - Supply the finished video or clearly identified direction sample, a silent contact sheet, and a download link. Embed video only when it will not start playback; otherwise use the sheet as the preview.
   - Report scope and material limitations honestly, retain provenance and editable sources in the edit workspace, and satisfy any asset attribution requirements.
   - Anti-patterns: calling a direction sample the finished film, hiding unresolved style differences, leaving change notes for the user to fill in, assigning unused footage, autoplaying the handoff.

## Visual Fidelity Gate

Compare actual output frames and transition sequences with the selected reference passages. Record concrete discrepancies and fixes in the edit workspace, not a generic claim that it looks good.

- **Asset language:** Are the medium, realism, and treatment consistent with the reference? Photography alone is not sufficient.
- **Composition:** Do object scale, framing, negative space, layering, and depth reflect the reference's approach? Is the intended focal point clear?
- **Motion and rhythm:** Do entrances, reveals, camera changes, and scene changes track the narration and reference cadence? Does the sequence evolve beyond overlays on one prop?
- **Typography and evidence:** Is text integrated into imagery rather than defaulting to title slides? Are source excerpts readable, faithful, and complete enough to preserve meaning?
- **Finish:** Inspect actual-size frames for awkward crops, weak contrast, overlaps, implausible cutouts, and repetitive layouts. A reference match cannot excuse unreadable evidence.

A material failure in any gate category, including unreadable or misleading evidence, typography, contrast, overlaps, or other finish defects, blocks expansion to the full edit. Fix it and compare again. Do not compensate with more decorative animation or unsupported claims of fidelity.

## Anti-Patterns

- Treating a named creator/style as a palette, font pairing, or generic mood.
- Replacing a difficult reference treatment with the easiest available graphic.
- Conflating a technically clean export with a convincing visual result.
- Applying the same stock prop or layout to every clause.
- Inventing factual evidence to make a collage look authentic.
- Reviewing media through playback without an explicit request.
- Stopping an authorized full edit at a direction sample because the user rejected an earlier style.

## Output

Deliver the completed video, silent contact sheet, download link, and concise scope/limitations. Deliver only a clearly labeled sample when that is the user's explicit requested scope or stopping point. Keep the beat map, frame comparison, provenance, and review notes with the editable project. Behavioral regression cases are in [tests/scenarios.md](tests/scenarios.md).
