---
name: mailerlite-html-blocks
description: Use when building, pasting, or saving custom HTML modules in MailerLite — creating a Code block, injecting module HTML, saving it as a reusable Saved block, updating one, or debugging why a Code block "isn't rendering". Covers the drag-and-drop template editor, the Atelier Zero module library, and Hair Solutions Co. brand rules (account 2582639).
---

# MailerLite HTML blocks

Build a module as a Code block in a **drag-and-drop template**, then save it as a **Saved block**
so it can be reused. Run `mailerlite-email-preflight` before anything ships.

## 0. The thing that wastes the most time

**Code blocks NEVER render in the editor canvas. By design, not a bug.**

The canvas shows a grey box reading *"This placeholder is not visible in preview mode."* That
sentence is about the placeholder — the grey box exists only in the editor and vanishes in preview,
where your HTML renders. The canvas cannot execute arbitrary HTML inside its own DOM without
breaking its layout and drag layer. There is no setting. Do not "fix" working HTML because the
canvas looks empty.

**The canvas DOM does not contain your HTML either.** Reading `innerHTML` off the canvas returns
placeholder markup, so you cannot verify a push from the builder page. The block HTML lives in the
editor's model; the only rendered copy is the preview.

Verify cheapest-first:
1. **Local contact sheet / assembled preview** — `scripts/make_contact_sheet.py`. Instant.
2. **Template Preview** — My templates → hover card → **Preview**. Wait ~10s; images lazy-load and
   an early screenshot shows alt text, which looks like a broken image but isn't.
3. **Direct preview URL** — `dashboard.mailerlite.com/preview/templates/<id>`. Best for machine
   verification: the rendered email is same-origin, so computed styles can be read straight off it.

```js
[...document.querySelectorAll('table.az-module-shell')].map(s => {
  const cs = getComputedStyle(s);
  return { bg: cs.backgroundColor, radius: cs.borderTopLeftRadius,
           border: cs.borderTopWidth + ' ' + cs.borderTopColor,
           w: Math.round(s.getBoundingClientRect().width) };
})
```

4. **Campaign → Preview and test.**

Serve local previews over `http://127.0.0.1:<port>` (`python3 -m http.server`). The browser tool
mangles `file://` into `https://file://`.

## 1. Get into the right editor

| Surface | Editor | Code block? |
|---|---|---|
| Campaign made via Import HTML | **Custom HTML editor** — one pane, whole email | No |
| **My templates → Edit** | **Drag & drop editor** | **Yes** |

The browser tab title says which. Work in **My templates** (left nav, bottom):
`dashboard.mailerlite.com/templates` (`?page=2` for the rest); editor is `/templates/<id>/content`.

## 2. Add a Code block

Category is **Special → Code** (last item). Faster: type `code` in the rail's **Search..** box —
it isolates the one thumbnail, no scrolling. Mouse-wheel scrolling inside the rail and the canvas
does not work (both are iframes); use search, or scroll via JS.

Drag with a real `left_click_drag`; synthetic JS clicks do not work. **Drag once per session, then
duplicate.** Hovering a block shows its toolbar ~71px above the block centre:

`⠿ drag` `▲` `▼` … `🔖 save as block` `✏️ edit` `👁 hide` `⧉ duplicate` `🗑 delete`

## 3. Inject the HTML

The panel is **CodeMirror 5**. Typing kilobytes is far too slow — set the value directly:

```js
const cms = [...document.querySelectorAll('.CodeMirror')].filter(e => e.offsetParent !== null);
const cm = cms[cms.length - 1].CodeMirror;
cm.setValue(html); cm.refresh();
```

Guard it when you are unsure which block is open — read `cm.getValue()` first and abort on a
signature string from a different module. Then **Save settings**.

**GOTCHA: "Done editing" (top-right, green) is NOT save.** It leaves the editor. Use **Save
settings** for the block, then **Save template** for the template.

**Wrapper background must be OFF.** In the block panel, `Background` → toggle **OFF**. Left ON it
paints a hard rectangle behind your rounded card and destroys the stacking. This is a MailerLite
setting, separate from `background-color` in your HTML.

## 4. Save as a reusable block

**🔖** → name → **Save**. To overwrite: tick **Update existing block**, pick it from the
*Select block to update* dropdown, then **Save and update block**. Name by purpose and tone, never
by campaign: `Header - Centered logo - Light`.

**Actions → Remove content blocks** wipes the whole template and is gated behind typing `REMOVE`.
Prefer per-block deletes. Version history (clock icon) can recover.

## 4b. Driving the editor reliably

These cost real time on 2026-08-19. They are not optional technique.

**The first click after a page load never registers.** Navigate, wait ~10s, click a block, check for
a visible CodeMirror — if there is none, click again. Batching a whole edit run straight after a
`navigate` silently does nothing for the first two or three steps.

**Recompute block coordinates before every click.** The canvas scrolls itself as you edit, so
coordinates captured a minute ago point at a different block. Skipping this once patched the footer
twice and left the sign-off untouched. Read positions fresh:

```js
const f = document.getElementById('content-builder-iframe');
const d = f.contentDocument; const fr = f.getBoundingClientRect();
[...d.querySelectorAll('.can-be-active.block')].slice(1)   // [0] is "View in browser"
  .map((b, i) => ({ block: i + 1,
    y: Math.round((fr.top + b.getBoundingClientRect().top +
                   b.getBoundingClientRect().height / 2) * SCALE) }));
```

`SCALE` is screenshot pixels per CSS pixel — derive it once by clicking a known block and comparing
(≈0.8725 on this display), because screenshots are not 1:1 with page coordinates.

**Neither the canvas nor the block rail scrolls with the mouse wheel** — both are iframes. Use
`element.scrollIntoView({block:'center'})` inside the iframe, then recompute coordinates.

**Guard every write with a signature check.** Read `cm.getValue()` first and abort if it does not
look like the block you meant to edit. Cheap, and it is the only thing standing between a stray
click and overwriting the wrong module.

**Patch in place rather than re-sending whole blocks.** For a change confined to one attribute,
regex the existing value — smaller, and it cannot corrupt the parts you did not mean to touch:

```js
let v = cm.getValue();
if (!/border:none;border-radius:16px/.test(v)) return 'unexpected shell - aborting';
v = v.replace('border:none;border-radius:16px', 'border:1px solid #DED6C2;border-radius:20px');
cm.setValue(v); cm.refresh();
```

**Adding blocks:** select an existing Code block and press **⧉ duplicate**. Selection stays on the
original, so duplicate repeatedly to add several, then fill each. Toolbar sits ~70px above the block
centre: `⠿` `▲` `▼` … `🔖` `✏️` `👁` `⧉` `🗑`. `▲` moves a block up one position.

**Deleting a saved block:** Saved blocks rail → hover the row → trash → **Confirm block removal**.
Wait for the dialog to finish animating: clicking `Delete` while it is still fading in does nothing
at all and reports no error. Screenshot, confirm the button is solid red, then click. Re-read the
list afterwards — the rail can show a stale entry until reopened.

## 4c. Bulk work: drive the Angular scope, don't click

For more than a handful of blocks, stop clicking. The editor is Angular 1.x inside
`#content-builder-iframe`, and every block element carries a scope you can drive directly. One
scratch Code block then serves a whole run — no dragging, no duplicating, ~8s per block.

```js
const ifw = document.getElementById('content-builder-iframe').contentWindow;
const bs  = ifw.document.querySelectorAll('.can-be-active.block');   // [0] is "View in browser"
const sc  = ifw.angular.element(bs[bs.length - 1]).scope();

sc.data.variables.code.value = html;                    // the Code block's HTML — no CodeMirror
sc.data.variables.isContentBackground.value = 'off';    // the wrapper-Background-OFF rule
sc.$apply();
```

The scope also gives you `remove()`, `duplicateitemfn`, `editBlock`, `hidefn`,
`moveblockupfn`/`moveblockdownfn`, `canSaveCustomBlock()`.

Saving as a reusable block is a **parent-window** function — `window.openBlockTemplateModal(sc)` opens
the "Save block template" dialog. Its input is `ng-model`-bound, so a plain `.value =` is ignored;
use the native setter plus an `input` event, then click `Save`, wait for the text "Block saved", and
click "Continue editing".

```js
const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
setter.call(input, name);
input.dispatchEvent(new Event('input', {bubbles: true}));
```

**Do not try to replay the HTTP call.** Saving posts to
`groot.mailerlite.com/builder/custom_blocks/save`, but that endpoint is not reachable cross-origin
from the dashboard: `fetch` and `XHR`, JSON and form-encoded, with and without credentials, from the
page world and the extension's isolated world all return status 0. Let the app make its own request.

### Three traps in any self-driving loop here

1. **Chrome throttles `setTimeout` in a background tab to about once a minute.** A loop looks hung —
   progress frozen, modal open on screen, timeout branches never firing. It is not your bug. Keep the
   editor tab **foregrounded** for the whole run and re-activate it before each poll.
2. **Wrap every step in try/catch, the scope lookup included.** An exception inside a `setTimeout`
   callback is uncaught, kills the chain silently, and looks exactly like the throttling above.
3. **Injected `<script>` runs in the page world; extension-evaluated JS does not.** Extension JS sees
   the DOM and `localStorage` but not `angular`/`jQuery`/`CodeMirror`, and its `fetch` carries the
   extension's origin. Inject a script element and pass results back via a DOM attribute.

### Verify the library without opening the rail

The whole saved-block list ships in the editor page's inline scripts, readable after any reload:

```js
const s = [...document.querySelectorAll('script')].map(x => x.textContent).join('\n');
s.split('"title":"' + name + '"').length - 1;    // 0 = missing, 1 = good, >1 = duplicate
```

Check the **duplicate** count, not just presence: re-saving an existing name creates a *second* block
rather than overwriting, unless "Update existing block" is ticked. Confirm what actually saved before
re-running a failed batch — a stalled run that appears to have done nothing may have saved its first
item already.

## 5. Fragment rules

- Fragment only: strip `<!doctype>`, `<html>`, `<head>`, `<body>`.
- **Forbidden:** JavaScript, `embed`, `frame`, `iframe`, `form`, `input`, `object`, `textarea`.
- Tables + inline styles. A `<style>` block saves fine but headers/footers don't need one.
- Prefer images from **MailerLite's File Manager** (`storage.mlcdn.com/account_image/2582639/…`).
  Those URLs cannot be transformed, so size the `<img>` to the asset's real aspect ratio.
- Converter: `scripts/make_mailerlite_blocks.py` (source → fragments, palette + geometry fixed).

## 6. Design rules (learned the hard way)

**Flush stacking.** Sections butt against each other with no gap, so alternating surfaces read as
stacked boxes. Outer wrapper cell is `padding:0 12px` — **zero vertical**; card is
`max-width:576px`. Atelier Zero ships `padding:7px …`, which is what puts gaps between cards.

`CARD + 2 × GUTTER = 600` (the spec's maximum wrapper). The gutter doubles as the mobile edge
margin, so it cannot go far below 12px without crowding the phone bezel.

**Radius is role-based, not one value** — from the Figma Email Design System, not the brand spec,
which is silent on radius: nav/header **8**, hero **12**, footer/divider **16**, title/content/CTA
**20**, pill **999**.

**Every card carries a 1px hairline, in solid hex — never `rgba()`.** Figma draws it as
`rgba(21,20,15,0.08)`; Outlook's Word engine cannot parse `rgba()` and may fall back to black,
putting a hard outline round every card. Pre-composite per surface: `#DED6C2` on Paper, `#2A2620`
on Ink, `#E5DFCD` on Bone.

**One light at a time.** Card surfaces are **Paper `#EFE7D2`**, **Bone `#F7F1DE`** or
**Ink `#15140F`** (Coral for at most one accent block, never header/footer). Bone became a legal
card surface on 2026-08-19 (Vincent) — see `PLATFORM_EMAIL.md` §1.1. **Paper Dark `#DDD2B6` and Ink
Soft `#2A2620` are still not surfaces.** Never put Bone and Paper in adjacent cards: two cards in
slightly different lights reads as a mistake, and it is one. Alternate either light against Ink.

**Every section is a Code block, including text ones.** Native MailerLite text/footer blocks cannot
take the rounded-card treatment, so they break the stack. That includes the footer.

**Don't structure what should be spoken.** Copy written as a person talking stays prose. Lists,
rules and inset panels are for genuinely enumerable things — specs, features, steps. Splitting a
founder's sentence into bullets makes it read like a survey form.

**Section grammar** (from the reference campaigns): coral eyebrow with a leading `—` dash,
letterspaced uppercase 11px → large centred title 26px/800 → muted centred body 15px → optional
coral pill CTA (`border-radius:999px`, Ink label). Alternate Ink / Paper down the email.

## 7. Brand facts

Authority: `brand-design-system/specs/PLATFORM_EMAIL.md`. It exists at **two paths that are
byte-identical** (verified 2026-08-19) — `/Users/vMac/08_brand/…` and `/Users/vMac/07_design/brand/…`.
Either is fine; re-read the file at use time and never trust a palette cached in a project doc.

| Role | Hex |
|---|---|
| Paper — light surface + body bg | `#EFE7D2` |
| Ink — dark surface | `#15140F` |
| Bone — text on Ink, inset panel on Paper | `#F7F1DE` |
| Paper Dark — dividers on light | `#DDD2B6` |
| Ink Soft — dividers on dark | `#2A2620` |
| Ink Mute — muted body on light | `#5A5448` |
| Coral — accent, ≤1 block per email | `#ED6F5C` |

**The Atelier Zero library ships a near-miss palette** — every colour a few points off, which is why
modules from different families never quite match. `make_mailerlite_blocks.py` maps them. Role
matters and is easy to invert:

- `#F6EFD9` is the light **card surface** (50 uses on `.az-module-shell`) → **Paper**
- `#EDE3CC` is **text on dark cards** (never a surface) → **Bone**

Also: `#151411`/`#181714`→Ink, `#25221D`/`#3A362F`/`#333533`→Ink Soft, `#C7BFAC`/`#DDD4BF`→Paper Dark,
`#807B6B`→Ink Mute, `#EA6452`→Coral.

**Approved wordmarks** (inline "co", MailerLite File Manager, both transparent):
- Ink letterforms, for light surfaces — `…/2582639/KFEEEOLO86h7tNAsKTXCNm7jzoBw1XZ4S3TXEZD9.png` (1580×473, tight)
- Bone letterforms, for dark surfaces — `…/2582639/6YZqwFXIewpePuTHcJLQmFlttJt1y0sAAo1GkX5f.png` (1860×822, ~24px baked margin)

Glyph block is ~1580×475 in both. To render the wordmark at 220px:
light → `width="220" height="66"`, `padding:24px 26px`;
dark → `width="259" height="114"`, `padding:0 26px` (its own margin is the padding).
Both give a 114px card. The older square 600×600 wordmarks are a 3-line lockup — **superseded**.

## 8. Personalization

Syntax is `{$field}` or, with a fallback, **`{$field|default('value')}`** — the fallback value
**must be quoted**. MailerLite's own docs show `{$tag|default('Value')}`.
`{$field default="value"}` is **wrong** and prints literally to subscribers.

**Unquoted fallbacks appear to blank the whole tag, silently.** On 2026-08-19 a test send of WB-1
containing `{$name|default(there)}` and `{$months_since_last_order|default(a few)}` arrived with
*both* tags rendered as empty strings — not literal, not the fallback — leaving "It's been a while,"
followed by a bare "." and "your last order was  months ago". The subscriber record had both fields
populated, so this was not a missing-data case. Note `a few` contains a space, which cannot survive
unparsed. Both were rewritten to the quoted form; **verification of the fix is still pending a test
send.** Until that lands, treat the unquoted form as the prime suspect but not proven — the other
live candidate is that test sends do not personalize at all (see below).

Fields live at `dashboard.mailerlite.com/subscribers/fields` — verify a tag exists before using it.
`{$unsubscribe}` is the real unsubscribe token. Merge tags never resolve in Preview; that is normal.

**Test sends are not a reliable personalization check.** MailerLite documents that "test emails allow
you to preview the layout of a campaign and do not test full functionality", while claiming `{$email}`,
`{$name}` and `{$last_name}` *do* work in them. Their own recommendation is to duplicate the campaign
and send it to yourself as a regular subscriber. So a blank name in a test send is not by itself proof
that the tag is broken — rule out the syntax first, then confirm with a real send to a one-person
group (a different permission class: ask first).

## 9. Guardrails

Building and saving blocks/templates is drafting. Test sends, scheduling, sending, automation
activation, imports and deletions need fresh explicit approval — see the email-marketing plugin's
`action-gates.md`.

Run `mailerlite-email-preflight` before proposing anything for release, then **`email-ship-approval`**
— the seven-gate final check that decides whether an email is approved at all.
