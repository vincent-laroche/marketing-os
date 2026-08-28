---
name: email-ship-approval
description: The final approval gate for a Hair Solutions Co. email — the seven checks an email must pass before it can be called ready to ship. Use when asked whether an email is approved, ready, done, or shippable, or before proposing any send, schedule, or automation activation. Runs after mailerlite-email-preflight, which it includes as gate 0. Pairs with hair-solutions-email-design-system (what it should look like) and mailerlite-html-blocks (how it was built).
---

# Email ship approval — the seven gates

Defined by Vincent, 2026-08-19. An email is **approved** only when all seven gates pass. Any gate
failing means **NOT APPROVED** — there is no partial credit and no "approved with notes".

Report every gate explicitly, including the ones that pass. Never infer a gate from another gate.
A gate you could not check is **NOT VERIFIED**, which is not a pass.

## Gate 0 — automated preflight

Run `mailerlite-email-preflight` first. Exit 0 required. It catches structure, palette, geometry,
merge-tag syntax, image attributes, dead links and compliance. It cannot judge meaning; gates 1–7
are the judgement.

---

## Gate 1 — copy verified against the master database

Authority: the `Body` column of
`Email Reference File/emails_master 831f4e0d84e0831992d481ae881cfede_all.csv`, matched on
`Email name`. Also check `Subject`, `Preview Text`, `CTA`, `Missing Modules`.

Compare **rendered text against the database, sentence by sentence** — not by eye, and not by
trusting a builder's docstring that claims the copy is verbatim. Extract the visible text from the
built blocks and diff it.

Copy must be **verbatim**. Re-splitting a sentence, swapping a full stop for an em dash, promoting
a clause into a heading, or tightening a line are all edits and all fail this gate unless the
deviation is recorded as approved (see gate 2).

`<br/>` and `&nbsp;` are typography, not copy — they do not change the words and are allowed.

`Missing Modules` non-empty ⇒ the email is **blocked**, not shippable.

## Gate 2 — module count meets or exceeds the database

`Module Stack` in the master states the required modules.

- The built email may contain **more** modules than the database lists.
- It may **never** contain fewer.

Extra modules are permitted, but each one must be recorded as an approved deviation in
`mailerlite/BUILD-LEDGER.md` — naming the module, who approved it, and when. An unrecorded extra
module fails this gate; a missing module fails it outright and cannot be waived.

*Precedent: WB-1's master lists 3 modules; it ships 7. Approved by Vincent 2026-08-19 and recorded
in the ledger.*

## Gate 3 — brand compliant

Run `atelier-zero-brand-compliance` against the rendered email and its source. Verdict must be
`COMPLIANT`. `CONDITIONAL` does not pass this gate.

Geometry authority is the Figma **Email Design System** (`9Il504CQE8jLaUTBVzphqc`) and its export
`/Users/vMac/00_inbox/Downloads/email-marketing-main/DESIGN.md` wherever `PLATFORM_EMAIL.md` is
silent — radius, spacing scale, shadow. Palette roles and voice still come from the brand spec.

## Gate 4 — every module saved to the library in three surfaces

Every module used in the email must exist as a **Saved block** in MailerLite in all three surfaces:

| Variant | Surface |
|---|---|
| Bone | `#F7F1DE` |
| Paper | `#EFE7D2` |
| Ink | `#15140F` |

Naming: `<Module> - <Surface>`, e.g. `Divider - Bone`. Verify by opening **Saved blocks** in the
drag-and-drop editor and reading the list — do not assume a block was saved because it was built.

> **Resolved 2026-08-19 — Bone is a legal surface.**
> This gate previously conflicted with `PLATFORM_EMAIL.md` §1.1, which forbade Bone as a section
> surface (exempting only `Divider`). Vincent readmitted Bone as a main surface on 2026-08-19 and
> §1.1 now carries the change, so a Bone variant is compliant, not a deviation.
>
> Two constraints survive that change and this gate does not waive them:
> **Paper Dark `#DDD2B6` and Ink Soft `#2A2620` are still never section surfaces**, and **Bone must
> never sit in a section directly adjacent to Paper** — two near-identical sands touching is the
> effect that was rejected on sight on 2026-08-11. A saved Bone variant is fine; a Bone card
> stacked against a Paper card in a built email is a MAJOR under gate 3.

## Gate 5 — every link and button actually resolves

Not a syntax check. **Open each destination and confirm it lands where the copy promises.**

- Every `href` and every button, including the footer and the unsubscribe token.
- Confirm the landing page is the *specific* next step named in the copy. A "Return to your cart"
  button that opens the homepage is a failure a validator cannot see.
- `mailto:` links: confirm the address and that the pre-filled subject is right.
- `{$unsubscribe}` does not resolve in preview — verify it in the test send from gate 6.
- Record the status and the final URL after redirects for each link in the report.

## Gate 6 — a copy is sent to Vincent

A real copy must land in Vincent's inbox so he can see it: `info@hairsolutions.co`.

> **This is a send, and sends are gated.** A test send is still a send. Ask for explicit approval
> in the current conversation immediately before sending, every time — a previous approval never
> carries, and neither does this skill. This gate *requires* the send; it does not authorise it.

After it arrives, confirm with Vincent that he has seen it. His confirmation is the gate, not the
send receipt.

## Gate 7 — a full-height screenshot is filed in Figma

Capture the whole email as one tall image and upload it to the Figma **Email Design System** so the
shipped artifact sits beside the designs.

```
1. Serve the assembled HTML locally:  python3 -m http.server <port>
   (the browser mangles file:// into https://file://)
2. Resize the viewport tall enough for the entire email, then screenshot with save_to_disk.
3. Upload:  upload_assets  fileKey 9Il504CQE8jLaUTBVzphqc  count 1
   POST the raw PNG bytes to the returned single-use URL with Content-Type: image/png.
   Without a nodeId it lands as a new frame on the file's current page.
```

Limits: **10MB per asset** — a full-height 2× capture of a long email will exceed that, so capture
at 1× or split. Confirm the upload landed on the intended page before calling this gate passed;
"current page" depends on what is open in the file.

---

## Verdict

Report exactly:

1. **APPROVED** or **NOT APPROVED**
2. A line per gate: `PASS` / `FAIL` / `NOT VERIFIED`, each with the evidence that decided it
3. For every failure: the exact fix and which gate must be re-run
4. Deviations recorded (gate 2) and conflicts raised (gate 4)
5. The next action and the approval class it needs

**Approval authorises nothing on its own.** Scheduling, sending to a list, activating an automation
and importing contacts each need fresh explicit approval in the current conversation, after
approval, every time.
