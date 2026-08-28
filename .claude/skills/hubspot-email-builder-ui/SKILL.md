---
name: hubspot-email-builder-ui
description: Assemble or verify HubSpot Marketing Email drag-and-drop drafts through the HubSpot email builder UI. Use when working in app.hubspot.com email editor, adding custom modules from the sidebar, searching module names such as Launch/Header/Split/Footer, dragging modules onto the canvas, or learning/replaying Vincent's demonstrated email assembly workflow.
---

# HubSpot Email Builder UI

## Overview

Use the HubSpot editor UI when Vincent asks to assemble an email manually, when API wiring is not trusted, or when the module picker must be used. Treat the visible editor and autosave state as the source of truth.

Always prepare the complete module queue before entering the HubSpot editor. The UI pass should be execution only: search, drag, place, repeat. Do not decide the structure while inside the editor.

Do not publish, send, archive, delete, or update live published content unless Vincent explicitly asks for that exact action. Assembling means editing the draft/canvas and leaving it ready for review.

## Recorded Pattern

Vincent demonstrated the general HubSpot module assembly pattern. The specific modules selected in the recording were examples only; the reusable lesson is the simple edit/search/drag/repeat rhythm.

1. Start from the Marketing Email list.
2. Select the email to edit by hovering over its row and clicking the inline `Edit` button. Do not rely on the corner/detail-page edit button unless the row hover control is unavailable.
3. Once inside the editor, use the module picker search field in the left sidebar.
4. Search with one word or a few letters only, not long names or internal module IDs:
   - `Head` for header modules.
   - `spl` for `Split Media (CH)`.
   - `laun` or `Launch` for launch modules.
   - `Foot` for `Email Footer (CH)`.
5. Select the matching module from the list below the search field and drag it exactly where it belongs on the canvas.
6. When happy with that section, click the plus sign on the far-left sidebar to return to the add/module picker.
7. Repeat: search one word or a few letters, find the module, drag it where it belongs.
8. Wait for `Autosaved with unpublished changes` before final review.

The event stream happened to show these modules being added successfully, but do not treat this as a fixed required stack:

- `Launch · Header Centered · Dark (CH)`
- `Split Media (CH)`
- `Launch · Feature List 5 (CH)`
- `Launch · Wordmark Pair (CH)`
- `Launch · Product Grid 3 (CH)`
- `Email Footer (CH)`

## Browser Control

Use the Browser plugin against the in-app browser or existing Chrome tab. Prefer DOM snapshots to understand the editor state, but use visible UI interactions for drag/drop because HubSpot's builder is iframe-heavy and drag/drop-based.

Stable UI anchors:

- Top editor state: `Autosaved with unpublished changes`, `Unsaved changes`, `Update`.
- Left sidebar heading: `Add`.
- Sidebar tabs: `Modules`, `Sections`.
- Sidebar search field: `Search`.
- Picker groups: `Recently used modules`, `All default modules`, `Custom modules`.
- Canvas is inside the preview iframe; module drops should visibly add content and often open the module edit panel.

## Assembly Workflow

1. Navigate to the email editor.
   - If starting from details, click `Edit Email`.
   - If starting from the list, open details or direct editor URL when known.

2. Prepare the module queue before editing.
   - Write the full ordered list of sections/modules that will be added.
   - Include the short search term for each module.
   - Include the target placement, for example `top`, `after hero`, `before footer`.
   - Include any field/copy notes needed for that module.
   - Keep this queue visible while working through the editor.
   - Do not start dragging modules until the queue is complete.

   Example queue shape:

   | Order | Search | Module | Placement | Notes |
   |---|---|---|---|---|
   | 1 | `Head` | Header module | Top | Brand header |
   | 2 | `spl` | Split Media (CH) | After header | Hero |
   | 3 | `Launch` | Launch · Feature List 5 (CH) | After hero | Five changes |
   | 4 | `Foot` | Email Footer (CH) | Bottom | Compliance/footer |

3. Open the editor.
   - Preferred: hover over the target email row and click the inline `Edit` button.
   - Fallback: open details and click `Edit Email`, or use the direct editor URL if known.

4. Verify the target email.
   - Check the H1/email name.
   - Check subject and preview text in the sidebar.
   - Confirm the canvas corresponds to the target email before editing.

5. Add modules manually from the prepared queue.
   - Click the sidebar `Search` field.
   - Clear any previous query.
   - Type one short search term at a time: one word, or only a few letters.
   - Wait for matching module cards.
   - Drag the exact module card onto the desired place on the canvas.
   - If a module edit panel opens, check its title and fields.
   - When ready for another section, click the plus sign on the far-left sidebar to return to the picker.
   - Repeat the same search and drag pattern.

6. Use search terms that match displayed names.
   - Do not search full internal names like `hsc_launch_feature_list_5`; HubSpot may show `No matches`.
   - Use `Launch` to reveal all launch modules.
   - Use `Foot` to find `Email Footer (CH)`.
   - Use `spl` to find `Split Media (CH)`.
   - If the intended module does not appear, shorten the query instead of adding more words.

7. Verify after each drop.
   - The module edit panel should name the dropped module.
   - The canvas should show new content.
   - Estimated size may increase.
   - Autosave should settle before the next drag.

8. Final verification.
   - Confirm all expected modules are visible on the canvas.
   - Confirm footer/compliance block exists.
   - Confirm `Autosaved with unpublished changes` is visible.
   - Do not click `Update` unless Vincent asks to update the published email.

## Launch Email Notes

For Hair Solutions Co. launch emails, the module picker should expose these launch modules when searching `Launch`:

- `Launch · Belief List (CH)`
- `Launch · Feature List 5 (CH)`
- `Launch · Founder Pillars (CH)`
- `Launch · Header Centered (CH)`
- `Launch · Header Centered · Dark (CH)`
- `Launch · Product Grid 3 (CH)`
- `Launch · Question List (CH)`
- `Launch · Wordmark Pair (CH)`

Prefer this manual order for launch assembly when starting from a blank or simple draft:

1. Header.
2. Hero or split media.
3. Feature list.
4. Wordmark pair or question list when relevant.
5. Product grid.
6. Founder/belief/CTA sections as needed.
7. Email Footer (CH) and HubSpot compliance footer if they are distinct in the draft.

If the API has already assembled a draft, use the UI workflow to verify and add any missing visible modules rather than rebuilding blindly.
