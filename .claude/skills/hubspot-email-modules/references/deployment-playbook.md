# HubSpot Email Modules Deployment Playbook

Exact `hs cms` commands for this account, with the failure modes actually hit while building this module set and how they were resolved. There is no local repo and no `npm` build step in this workflow — see `SKILL.md` for why.

`hs` CLI is already installed and authenticated (`hs accounts list` → default account is `HairSolutionsCo [standard] (50966981)`). All commands below assume `--account 50966981` explicitly anyway — don't rely on the default silently being correct in a session that might touch other accounts.

## Discover before you fetch

`hs cms list <path>` is much cheaper than a full fetch when you just need to see what's there:

```bash
hs cms list email_modules --account 50966981          # top-level families
hs cms list email_modules/cart-recovery --account 50966981   # subfolder contents
```

A `[ERROR] The request was not found` from `hs cms list` on a specific path means that path genuinely doesn't exist — it's a reliable signal, not a flaky error. Use it to rule out stale paths from old docs before assuming they're real.

## Fetch

```bash
hs cms fetch email_modules ./scratch-dir --account 50966981
```

Fetches the whole tree. For a single module: `hs cms fetch email_modules/header_centered_logo.module ./scratch-dir --account 50966981`. This is a real network operation per file — fetching the whole ~84-module tree takes a while and produces a lot of "Wrote file ..." log lines; that's normal, not a hang.

## Edit locally, then upload

```bash
hs cms upload ./scratch-dir/email_modules email_modules --account 50966981
```

**Uploading one prepared folder in a single call is much more reliable than looping `hs cms upload` per module.** A loop over ~15+ individual `hs cms upload` or `hs cms mv` calls can hit the surrounding tool's 2-minute timeout mid-run — it still completes whatever it got through, so check `hs cms list` on the affected path afterward and finish the remainder in a second pass. A single call over a whole folder tree (even ~250 files across 84 modules) has completed reliably in one shot every time it's been tried.

Never pass `--clean` unless you intend to delete anything at the destination that isn't in your local folder — this is a shared live account, not a personal sandbox.

## Always verify by fetching back

```bash
rm -rf ./verify-dir
hs cms fetch email_modules/<the module you changed> ./verify-dir --account 50966981
```

Upload success in the CLI output is necessary but not sufficient — read the fetched-back content and check the actual thing you changed (a hex value, a field default, a module_id being assigned to a brand-new module). This has caught real problems: an upload that reported success but where a `fields.json` schema error only surfaced on a *later* upload attempt of a sibling file, for instance.

## Moving files (`hs cms mv`)

```bash
hs cms mv "email_modules/final/family.module" "email_modules/family.module" --account 50966981
```

Marked beta by HubSpot; works fine for single moves. Same 2-minute-timeout caveat as upload applies if looping over many — verify with `hs cms list` on the source path afterward (empty = fully moved) rather than trusting the loop completed.

## Deleting

```bash
hs cms delete "email_modules/some_stale_folder" --account 50966981
```

Irreversible. Before deleting anything found while poking around (not something the user explicitly named), check what's actually in it and whether it's referenced anywhere — but once the user has given an explicit, itemized list of what to delete, just execute it; re-confirming a list they already gave precisely is more friction than help.

## Bulk find/replace across many modules

For a fix that applies identically across many files (a color, a structural pattern), fetch the whole tree, run a Python script against all the `module.html`/`fields.json` files with a regex tight enough to only match the one thing you mean, print a count of files changed vs. skipped, spot-check 2-3 outputs before uploading, then upload the whole tree back in one call. This is how the wrapper-transparency fix and the image-resize-wiring fix were applied across 84 and 28 modules respectively in this project — both were single Python passes over the fetched tree, not per-file manual edits.

**Watch for substring false positives when verifying with `grep -o`.** A pattern like `width:100%;background:` can match *inside* `max-width:100%;background:` on a completely different element than the one you're trying to check — always read the full relevant snippet (`cat`, not just `grep -o`) before concluding a fix didn't apply.

## Known failure modes

### "URL field at path X has an invalid default value"
Only appears at upload time, not from local JSON validation. The `default` for a `type: "url"` field must be `{"type": "EXTERNAL", "href": "..."}` directly, with a `supported_types` array as a sibling key — not `{"default": {"url": {...}, "open_in_new_tab": ..., "no_follow": ...}}`. See SKILL.md's Field Patterns section for the exact working shape, copied from a field HubSpot actually accepted.

### Resize/color controls in the drag-and-drop editor do nothing
Two different root causes, don't conflate them:
1. **Image width/height controls do nothing** → the field is declared `resizable: true` but `module.html` hardcodes the pixel value instead of reading `{{ module.field.width }}` / `.height`. Fix: reference the field.
2. **Background/font color controls do nothing** → these were never wired as real fields at all; every color is a hardcoded hex value in the HTML by design, so brand colors can't drift. The Styles-tab color pickers you see are HubSpot's own generic per-module panel, unconnected to anything — this isn't a bug to silently fix, it's a real design tradeoff (locked brand colors vs. free-form pickers) to confirm with the user before changing.

### "The creator prevented editing this module"
Check `meta.json` has `"global": false` and every field in `fields.json` has `"locked": false`. If those are already correct, the specific *email draft* may have inserted the module as a module-id-only widget rather than a proper path-based body — that's a draft-level problem, separate from the module definition, and needs the draft inspected directly with explicit approval before touching it. Never publish/send while doing this.

### Module default changed but an existing email still shows the old value
Expected — module defaults only affect *new* instances of the module. An email draft that already has the module dropped in keeps whatever field values were saved into that specific instance. Fix the draft directly if it needs updating; don't expect a module-level change to retroactively update it.

## Report format

End any deployment work with: which module folders changed, what was uploaded, the live fetch-verification result (not just "upload succeeded"), and what was deliberately left untouched — especially existing email drafts, sends, CRM data, or workflows, since none of that is in scope for module-level work.
