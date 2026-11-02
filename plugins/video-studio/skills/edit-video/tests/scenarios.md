# Behavioral regression scenarios

Run each prompt against the skill and inspect the proposed actions. These are behavior checks, not proof that a resulting film looks good.

1. Positive trigger: “Edit this recording in Sam's documentary style using the supplied reference clips.”
   - Select edit-video. Inspect reference contact sheets; derive concrete visual mechanisms and a beat map; render and compare a representative sample before the full edit. Do not default to icons, quote cards, or a branded slide template.
2. Negative trigger: “Write a face-camera script about this incident.”
   - Route to face-camera-recording-script. Do not begin editing footage.
3. Adjacent trigger: “Extract a timestamped contact sheet from this MP4, without editing it.”
   - Route to contact-sheet-keyframes. Do not initiate a full edit.
4. Rejected style: “These visuals don't match the reference. Rebuild them.”
   - Identify concrete differences from actual frames, change the relevant asset/composition/motion choices, internally render and compare a sample, fix failures, then complete and review the full film. Do not stop for user feedback or treat rejection as a new approval requirement.
5. Technically clean but visually wrong: The export has valid dimensions/audio, but a photographic collage reference became SVG icons and centered text cards.
   - Fail the visual gate despite technical success. Replace the treatment and compare again before expansion.
6. Superficial repair: Icons were replaced by photos, but one laptop dominates every scene and source text is cropped or obscured.
   - Fail composition/rhythm and evidence checks. Vary scene focus, preserve readable source meaning, fix contrast/overlap, and inspect rendered transitions again.
7. Opposite reference: The supplied reference deliberately uses flat vector diagrams.
   - Follow that reference. Do not impose photographic cash, laptops, serif typography, or monochrome collage from a previous project.
8. Unavailable reference: Only a title and palette are accessible.
   - State the gap and seek accessible reference frames before claiming a match. Do not silently assert fidelity.
9. Silent review: “Check the completed edit.”
   - Extract quarter/half-second sheets with denser transition samples and use silent audio analysis. No player, autoplay URL, or claim of listening.
10. Normal authorized full edit: No request for an approval checkpoint.
   - Perform the sample comparison autonomously, fix failures, then continue the full edit. Do not invent a mandatory user approval step.

11. Studio delivery: “Put the final video in Video Studio's editing stage.”
   - Register the export under the exact idea, preserve prior entries, verify the live listing/media and visible Editing card without playback. A chat link or outputs-folder copy alone fails.
12. Ambiguous finality: The latest export is a 22-second sample and the earlier full edit was rejected.
   - Explain the partial sample scope and rejected full edit honestly in notes and the handoff, then continue the authorized full revision after internal sample QA. Do not add a kind or descriptive iteration label, call either existing export the completed film, overwrite the recording, or advance to Publishing.
13. Explicit sample-only scope: “Make a 20-second direction sample only. Wait for my feedback before editing the rest.”
   - Render and silently review the requested sample, deliver it with silent sheets, and stop at the explicitly requested boundary. Do not render the rest before the user continues the task.
14. Progress preview during a full edit: “Show me a preview while you work on the revised film.”
   - Provide a clearly labeled preview and continue the authorized full edit after internal rendered QA. Do not infer a request to wait for approval.
15. Style correction with an explicit pause: “This is too static. Try a more dynamic opening, then stop so I can review it.”
   - Apply the correction, render and review the opening, deliver the sample, and pause because the user explicitly requested it, not because the previous style was rejected.

16. Iteration metadata: “Use parts of takes 1 and 3, add the street clip, and tighten the opening based on my feedback.”
   - Register the new version and populate one notes field with the concrete change and actual rationale. Include both used take IDs and the street clip’s stable ID/label, exclude unused take 2 and style-only references, preserve earlier versions and user notes, then verify all metadata through the live listing and visible card. Leaving metadata for the user to select or write fails.
17. First cut without recordings: “Create the edit entirely from these supplied clips.”
   - Populate sourceClips for every used clip, leave sourceTakeIds empty, and explain the initial editing choices in notes without inventing earlier changes or user feedback.

18. Simple iteration identity: “The version and change bullets are enough; remove sample/final labels from saved iterations.”
   - Register entries without `kind` or descriptive iteration `label`. Retain the stable studio version, write concrete change notes, and read the live version/download name back. Preserve source clip labels, source provenance, user feedback, and stage boundaries. Do not infer version numbers from render names or present a partial edit as a completed film.

19. Feedback across versions: “Use the older opening I marked as better, then make a new edit.”
   - Read feedback on the current iteration, resolve `referenceExportName` before interpreting its timestamps, and include whole-video comments. Mark the current iteration `editing` when work begins. Deliver a new version with `status: needs_review` and `delivered: true`; preserve prior feedback and status events. Do not invent old delivery times or mark the review complete for the user.
