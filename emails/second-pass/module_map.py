"""Notion module family -> live HubSpot module slug.

Verify against `hs cms list email_modules --account 50966981` before trusting.
A value of None means the module genuinely does not exist in the account and the
composer must emit a labelled placeholder instead.
"""

MODULE_MAP = {
    # structural
    "Header - Centered logo":             "header_centered_logo",
    "Header":                             "header_centered_logo",   # PP-7b shorthand
    "Footer - Preference centre":         "preference_opt_down",
    "Footer - Standard":                  "footer_standard",
    "Footer - Social":                    "footer_social",
    "Footer - Wide":                      "footer_wide",
    "Layout - Plain-text founder wrapper": "plain_text_founder_wrapper",

    # hero / opening
    "Hero - Text-led":                    "hero_text_led",
    "Hero - Photo-led":                   "hero_photo_led",
    "Text - Masthead":                    "text_masthead",

    # one generic text block serves every semantic text slot
    "Text - Opening":                     "text_block_generic",
    "Text - Reassurance":                 "text_block_generic",
    "Text - Customer snapshot":           "text_block_generic",
    "Text - Section":                     "text_block_generic",
    "Text - Offer discount":              "text_block_generic",
    "Text - Base type guidance":          "text_base_type_guidance",

    # lists
    "List - Questions":                   "faq",
    "List - Support strip":               "support_strip",
    "M10 Support strip":                  "support_strip",          # PP-7b shorthand
    "List - Trust strip":                 "trust_badge_row",

    # commerce
    "Commerce - Order summary":           "commerce_order_summary",
    "Commerce - Shipping tracking":       "commerce_shipping_tracking",
    "Commerce - Quote and spec table":    "commerce_quote_spec_table",
    "Commerce - Cart line items":         None,   # M1 — does not exist
    "Commerce - Viewed product":          None,   # M3 — does not exist

    # product
    "Product - 3-up grid":                "product_goal_based_recommendation_3up",
    "Product - Dynamic recommendations":  None,   # deferred: wants native HubSpot/Shopify

    # signals / CTA
    "Signal - Promo code":                "promo_code_block",
    "Signal - Countdown":                 "countdown_expiry",
    "Button - Primary CTA":               "button_standalone_cta",

    # proof
    "Testimonial":                        "testimonial",
    # review_stars hardcodes five literal star glyphs in module.html — the
    # `rating` field only fills the "N/5" caption text, so no field value can
    # ever stop it rendering a fabricated 5-star graphic. Confirmed against
    # /tmp/live/review_stars.module/module.html 2026-08-11. Vincent's call:
    # treat as unavailable, same as the commerce modules with no live source.
    "Review stars":                       None,
    "Quote - Accent bar":                 "quote_accent_bar",
    "Quote - Centered":                   "quote_centered",
    "Stat bars":                          "stat_bars",

    # rich content
    "Photo - Feature story":              "photo_feature_story",
    "Photo - Founder note":               "photo_founder_note",
    "Column - Image and text":            "column_image_and_text",
    "Comparison":                         "visual_comparison_cards",  # chosen over live `comparison` (2-column head-to-head) because C-2 needs 2–3 options
    "Grid - Collections 4":               "grid_collections_4",
    "Timeline":                           "timeline",
    "FAQ":                                "faq",                    # alias for List - Questions

    # copy-desk markers, not modules — the composer renders these as placeholders
    "PULL from Proof Bank":               None,
    "PULL":                               None,
    "OFFER — confirm before send":        None,
}


def resolve(family):
    return MODULE_MAP.get(family)


def missing_families(emails):
    """Families used by a real stack that have no live module."""
    out = set()
    for e in emails:
        for s in e["stack"]:
            if s["family"] in MODULE_MAP and MODULE_MAP[s["family"]] is None:
                if not s["family"].startswith(("PULL", "OFFER")):
                    out.add(s["family"])
    return sorted(out)


PLACEHOLDER_HOST = "text_block_generic"

_REASON = {
    "Commerce - Cart line items":
        "Needs live Shopify cart data. Replace with the native HubSpot/Shopify cart module.",
    "Commerce - Viewed product":
        "Needs live catalogue data. Replace with the native HubSpot/Shopify product module.",
    "Product - Dynamic recommendations":
        "Deliberately deferred — replace with the native HubSpot/Shopify product-recommendations "
        "module so it pulls real price, image, stock and link.",
    "Review stars":
        "review_stars hardcodes five star glyphs in its own HTML regardless of the `rating` "
        "field, and the Proof Bank is empty — there is no real rating to show and no field "
        "value can suppress the fake stars. Needs a module fix before this can be live.",
    "PULL from Proof Bank":
        "Proof Bank is empty (confirmed 2026-08-11). Vincent supplies the approved quote.",
    "OFFER — confirm before send":
        "Offer terms need confirming before this email can ship.",
}


def placeholder_fields(family, qualifier="", copy=""):
    """Field values rendering a visible, labelled placeholder in a text_block_generic."""
    reason = _REASON.get(family, "Not available yet.")
    detail = qualifier or copy.strip()
    body = f"<p style='margin:0 0 12px;'>{reason}</p>"
    if detail:
        body += f"<p style='margin:0;'><em>Brief: {detail}</em></p>"
    return {
        "eyebrow": "Placeholder",
        "heading": f"[ {family} ]",
        "heading_accent": "",
        "body_text": body,
        "show_button": "no",
        "button_label": "",
        "button_url": {"href": "#"},
    }


# --- fields_for: v3 copy block -> live module field values -----------------
#
# ctx = defaults(folder) then ctx.update(values) downstream, so any field left
# out of the dict this returns silently keeps that module's demo placeholder
# content. Field names below are verified against /tmp/live/<module>/fields.json
# (see task-4-report.md for the module-by-module check).

import re as _re

ARROW = _re.compile(r"\s*[→>]+\s*$")


def _paras(copy):
    out = []
    for chunk in [c.strip() for c in (copy or "").split("\n\n") if c.strip()]:
        chunk = chunk.replace("\n", "<br>")
        out.append(f"<p style='margin:0 0 16px;'>{chunk}</p>")
    return "".join(out)


def _base(**kw):
    f = {"eyebrow": "", "heading": "", "heading_accent": "", "body_text": "",
         "show_button": "no", "button_label": "", "button_url": {"href": "#"}}
    f.update(kw)
    return f


NUM_RE = _re.compile(r"^\d+\.\s*")
BULLET_RE = _re.compile(r"^[·—]\s*")
INLINE_QA_RE = _re.compile(r'^"([^"]+)"\s*[—-]\s*(.+)$', _re.S)
QUOTE_ONLY_RE = _re.compile(r'^"[^"]+"$')


def _kv_lines(copy):
    """'Label: value' lines -> [(label, value), ...], in order, skipping blanks."""
    out = []
    for line in (copy or "").split("\n"):
        line = line.strip()
        if line and ":" in line:
            label, _, value = line.partition(":")
            out.append((label.strip(), value.strip()))
    return out


def _fill_slots(prefix_fmt, pairs, slots):
    """Fill named label_*/value_* slots from an ordered pairs list, blanking the rest."""
    f = {}
    for i, slot in enumerate(slots):
        label, value = pairs[i] if i < len(pairs) else ("", "")
        f[prefix_fmt.format(slot=slot, part="label")] = label
        f[prefix_fmt.format(slot=slot, part="value")] = value
    return f


def _trust_items(copy):
    return [s.strip() for s in (copy or "").split("·") if s.strip()]


def _split_items(copy):
    """Uncapped (question, answer) pairs, in document order.

    Handles three shapes seen in the v3 export: a quoted question with its
    answer inline after an em dash (C-1), a quoted question on its own line
    followed by an answer paragraph (CR-2), and a flat numbered/bulleted list
    of steps or facts with no real answer (PP-1, PP-2, PP-7b, RO-5) — those
    fill the question slot only. Shared by `_faq_items` (which caps/folds to
    5 slots for the live `faq` module) and `faq_all_unanswered`/
    `flat_list_fields` (the text_block_generic fallback, which needs every
    item, uncapped — see compose_v3._compose).
    """
    items = []
    for para in [p for p in (copy or "").split("\n\n") if p.strip()]:
        lines = [l for l in para.split("\n") if l.strip()]
        if len(lines) >= 2 and all(NUM_RE.match(l) or BULLET_RE.match(l) for l in lines):
            for l in lines:
                q = BULLET_RE.sub("", NUM_RE.sub("", l.strip())).strip()
                items.append((q, ""))
            continue
        text = para.strip()
        m = INLINE_QA_RE.match(text)
        if m:
            items.append((m.group(1).strip(), m.group(2).strip()))
            continue
        if len(lines) >= 2 and QUOTE_ONLY_RE.match(lines[0].strip()):
            q = lines[0].strip().strip('"')
            a = " ".join(l.strip() for l in lines[1:])
            items.append((q, a))
            continue
        q = BULLET_RE.sub("", NUM_RE.sub("", text)).strip()
        items.append((q, ""))
    return items


def _faq_items(copy, cap=5):
    """Split List - Questions / FAQ copy into (question, answer) pairs,
    capped/folded to the live faq module's 5 slots. Verified safe against
    /tmp/live/faq.module/module.html: each row is gated on
    `{% if module.faq_N_question %}`, so an empty faq_N_answer just renders
    an empty (but valid, non-broken) answer cell under the bold question line
    — that remains true for the (now rarer) case where this module IS still
    used, i.e. copy that is genuinely Q&A shaped. See faq_all_unanswered()
    for the flat-list case, which no longer reaches this module at all.
    """
    items = _split_items(copy)
    if len(items) > cap:
        head = items[:cap - 1]
        tail = items[cap - 1:]
        q5, a5 = tail[0]
        extra = [f"{q} — {a}" if a else q for q, a in tail[1:]]
        if extra:
            a5 = (a5 + " " if a5 else "") + " / ".join(extra)
        head.append((q5, a5))
        items = head
    return items


def faq_all_unanswered(copy):
    """True when every item _split_items() extracts from this copy has an
    empty answer — i.e. the copy is a flat list (checklist/timeline/
    checkpoints), not real Q&A. This is a property of the copy itself, not a
    hardcoded email code, so it keeps working as copy changes.

    An empty `copy` (no matching block at all) returns False — that case is
    handled upstream by compose_v3's own placeholder-for-unmatched-slot path,
    not by this fallback.

    The mixed case — some rows answered, some not — is deliberately NOT
    routed to the fallback by this function (it only fires when *every* row
    is unanswered). A mixed block stays on the `faq` module as before, and
    audit.py's faq_empty_answers() check will fail loudly on it rather than
    let it ship silently blank or have this function silently guess. Today
    (2026-08-11) every List - Questions/FAQ block in the 28-email set is
    cleanly all-answered (CR-2, C-1) or all-unanswered (PP-1, PP-2, PP-5,
    PP-7b, RO-5, C-0) — see test_compose_v3.py for a synthetic test of the
    mixed case documenting this decision.
    """
    items = _split_items(copy)
    return bool(items) and all(not a.strip() for _, a in items)


def flat_list_fields(qualifier="", copy=""):
    """Fields for the text_block_generic fallback used when a List -
    Questions/FAQ block's copy is a flat list, not real Q&A (see
    faq_all_unanswered). Every content field is set explicitly so none of
    text_block_generic's own demo defaults ('A clear next step' / 'Add
    concise, useful copy here.') can leak through (render_emails.block_html
    does ctx = defaults(folder) then ctx.update(values), so an omitted field
    inherits the demo default).

    No eyebrow or heading is invented: PP-7b and C-0 carry no qualifier in
    the v3 export, so heading stays "". Where a qualifier does exist (e.g.
    'what happens next timeline') it is carried into heading, title-cased,
    matching how every other family in this module derives its `eyebrow`
    from the qualifier. Every list item survives, verbatim and in order —
    none dropped, truncated, or capped (unlike the 5-slot faq module this
    replaces); bracketed copy-desk markers such as C-0's
    `{{ dynamic: ... }}` pass through untouched, same as everywhere else in
    this file.
    """
    items = _split_items(copy)
    lis = "".join(
        f"<li style='margin:0 0 10px;'>{(f'{q} — {a}' if a else q)}</li>"
        for q, a in items
    )
    body = f"<ul style='margin:0;padding-left:20px;'>{lis}</ul>" if lis else ""
    heading = qualifier.title() if qualifier else ""
    return {"eyebrow": "", "heading": heading, "heading_accent": "",
            "body_text": body, "show_button": "no", "button_label": "",
            "button_url": {"href": "#"}}


def _timeline_steps(copy, n=4):
    """Numbered steps -> [(heading, text), ...], capped at n. When there are
    more numbered items than slots, folds the overflow into the last slot's
    `text` rather than dropping it — see C-0's 5-step production window
    against the module's 4 slots."""
    items = []
    for line in (copy or "").split("\n"):
        m = _re.match(r"^\d+\.\s*(.+)$", line.strip())
        if m:
            items.append(m.group(1).strip())
    if len(items) <= n:
        return [(it, "") for it in items]
    head = [(it, "") for it in items[:n - 1]]
    tail = items[n - 1:]
    head.append((tail[0], " ".join(tail[1:])))
    return head


def _quote_parts(copy):
    """'Intro line: / token' and 'Label: value [· Label: value]' shapes -> (intro, pairs)."""
    lines = [l.strip() for l in (copy or "").split("\n") if l.strip()]
    intro, pairs = [], []
    pending_token = False
    for line in lines:
        kv = []
        for seg in [s.strip() for s in line.split("·")]:
            if ":" in seg:
                label, _, value = seg.partition(":")
                if value.strip():
                    kv.append((label.strip(), value.strip()))
        if kv:
            pairs.extend(kv)
            pending_token = False
            continue
        if line.endswith(":"):
            intro.append(line[:-1].strip())
            pending_token = True
            continue
        if pending_token:
            pairs.append(("Specification", line))
            pending_token = False
            continue
        intro.append(line)
    return " ".join(intro).strip(), pairs


def fields_for(family, qualifier="", copy="", email=None):
    email = email or {}
    copy = (copy or "").strip()
    eyebrow = qualifier.title() if qualifier else ""

    if family in ("Hero - Text-led", "Hero - Photo-led", "Text - Masthead"):
        # a hero's copy is its headline; keep any second paragraph as body.
        # hero_text_led / hero_photo_led / text_masthead all share this exact
        # 7-field shape (verified /tmp/live) so _base()'s full set is correct here.
        head, _, rest = copy.partition("\n\n")
        return _base(heading=head.strip(), body_text=_paras(rest))

    if family == "Layout - Plain-text founder wrapper":
        # plain_text_founder_wrapper fields: greeting, letter_text, signature,
        # show_button, button_label, button_url. No eyebrow/heading/body_text
        # here, so this does NOT use _base() (which would add those as inert
        # keys — Correction #4).
        lines = [l for l in copy.split("\n")]
        greeting = lines[0].strip() if lines and lines[0].strip().startswith("Hi") else ""
        rest = "\n".join(lines[1:]) if greeting else copy
        paras = [p.strip() for p in rest.split("\n\n") if p.strip()]
        signature = ""
        if paras and paras[-1].split("\n")[0].strip().startswith("Vincent"):
            signature = paras.pop().replace("\n", "<br>")
        return {"greeting": greeting, "letter_text": _paras("\n\n".join(paras)),
                "signature": signature, "show_button": "no", "button_label": "",
                "button_url": {"href": "#"}}

    if family == "Button - Primary CTA":
        # button_standalone_cta fields: eyebrow, heading, body_text,
        # show_button, button_label, button_url. No heading_accent — so this
        # does NOT use _base() either (Correction #4).
        label = ARROW.sub("", copy or email.get("cta", "")).strip()
        return {"eyebrow": "", "heading": "", "body_text": "",
                "show_button": "yes", "button_label": label,
                "button_url": {"href": "https://hairsolutions.co/"}}

    if family == "Signal - Promo code":
        code = ""
        m = _re.search(r"\b([A-Z][A-Z0-9]{4,})\b", copy)
        if m:
            code = m.group(1)
        terms = " ".join(l for l in copy.split("\n") if code not in l).strip()
        return {"heading": copy.split("\n")[0].strip(), "promo_code": code,
                "terms_text": terms, "button_label": "",
                "button_url": {"href": "https://hairsolutions.co/"}}

    # --- Round 2, Correction #4 (general case): these three families were
    # already landing their copy correctly via the generic fallback below
    # (their modules do have body_text), but that fallback always uses
    # _base()'s full 7-key shape, which stamps show_button/heading_accent
    # keys these modules don't have. The round-2 regression test (every
    # fields_for key must exist in its module's fields.json, across all 28
    # emails) caught these three in addition to the two named in the
    # coordinator's note, so they get the same treatment.

    if family in ("List - Support strip", "M10 Support strip"):
        # support_strip: eyebrow, heading, body_text, button_label, button_url.
        # No show_button, no heading_accent.
        return {"eyebrow": eyebrow, "heading": "", "body_text": _paras(copy),
                "button_label": "", "button_url": {"href": "#"}}

    if family == "Text - Base type guidance":
        # text_base_type_guidance: eyebrow, heading, body_text, show_button,
        # button_label, button_url. No heading_accent.
        return {"eyebrow": eyebrow, "heading": "", "body_text": _paras(copy),
                "show_button": "no", "button_label": "", "button_url": {"href": "#"}}

    if family == "Signal - Countdown":
        # countdown_expiry: eyebrow, heading, expiry_text, body_text,
        # button_label, button_url. No heading_accent, no show_button. The
        # copy here (e.g. "Valid for 7 days from this email.") IS the
        # validity statement, so it belongs in expiry_text — the module's
        # large bold deadline line — not body_text.
        return {"eyebrow": eyebrow, "heading": "", "expiry_text": copy,
                "body_text": "", "button_label": "", "button_url": {"href": "#"}}

    # --- Correction 1 (round 1): Testimonial uses its own real field names,
    # never placeholder_fields()'s text_block_generic-shaped keys. The module
    # exists in the live account to carry real Proof Bank quotes, but the
    # Proof Bank is empty as of 2026-08-11 — every block currently arrives as
    # a bracketed copy-desk instruction. That instruction must survive
    # verbatim into quote_text, and no name/detail/rating may be invented.
    # (Review stars was here too in round 1; round 2 moved it to `None` in
    # MODULE_MAP — see the PULL/OFFER branch below and task-4-report.md.)

    if family == "Testimonial":
        # testimonial.module fields: quote_text, customer_name, customer_detail,
        # customer_image, show_stars. customer_image is left untouched (its
        # default is an empty src, not a fabricated fact).
        quote = copy if copy else f"[ {family} — no Proof Bank content supplied ]"
        return {"quote_text": quote, "customer_name": "", "customer_detail": "",
                "show_stars": "no"}

    # --- Round 2: structured modules that were previously falling through to
    # the generic text_block_generic-shaped fallback below, silently dropping
    # their copy (those modules have no body_text field at all) and leaving
    # HubSpot's fabricated demo defaults (fake order numbers, tracking
    # numbers, trust-badge claims, quote figures...) to render as if real.

    if family == "Commerce - Order summary":
        # commerce_order_summary: eyebrow, heading, label_order/value_order,
        # label_spec/value_spec, label_status/value_status, label_eta/value_eta,
        # note, button_label, button_url. Every field explicitly set/blanked —
        # none of the module's fabricated demo defaults ('#HS-40218', 'In
        # production', 'Aug 24', ...) may survive.
        pairs = _kv_lines(copy)
        f = {"eyebrow": eyebrow, "heading": "", "note": "",
             "button_label": "", "button_url": {"href": "#"}}
        f.update(_fill_slots("{part}_{slot}", pairs, ["order", "spec", "status", "eta"]))
        return f

    if family == "Commerce - Shipping tracking":
        # commerce_shipping_tracking: eyebrow, heading, label_carrier/value_carrier,
        # label_tracking/value_tracking, label_eta/value_eta, note, button_label,
        # button_url. Same rule: blank every field, never inherit 'UPS Ground' /
        # '1Z999AA10123456784' / 'Aug 9'.
        pairs = _kv_lines(copy)
        f = {"eyebrow": eyebrow, "heading": "", "note": "",
             "button_label": "", "button_url": {"href": "#"}}
        f.update(_fill_slots("{part}_{slot}", pairs, ["carrier", "tracking", "eta"]))
        return f

    if family == "Commerce - Quote and spec table":
        # commerce_quote_spec_table: eyebrow, heading, label_1..5/value_1..5,
        # note, button_label, button_url. The copy's intro line goes to
        # heading; "Label: value" segments (· -separated on one line, as in
        # C-2's "Base: X · Hair: Y") fill label_N/value_N in order.
        intro, pairs = _quote_parts(copy)
        f = {"eyebrow": eyebrow, "heading": intro, "note": "",
             "button_label": "", "button_url": {"href": "#"}}
        for i in range(1, 6):
            label, value = pairs[i - 1] if i <= len(pairs) else ("", "")
            f[f"label_{i}"] = label
            f[f"value_{i}"] = value
        return f

    if family == "List - Trust strip":
        # trust_badge_row: item_1..4_icon/item_1..4_label. Only the labels are
        # set — icons are left untouched so the module's own icon glyphs
        # survive (decorative, not a fabricated fact). Every unused label slot
        # is explicitly blanked so demo claims like 'Secure Payment' cannot
        # leak in under an icon that has nothing real to say.
        items = _trust_items(copy)
        return {f"item_{i}_label": (items[i - 1] if i <= len(items) else "")
                for i in range(1, 5)}

    if family in ("List - Questions", "FAQ"):
        # faq: heading, faq_1..5_question, faq_1..5_answer. See _faq_items for
        # the three copy shapes this needs to handle.
        items = _faq_items(copy)
        f = {"heading": eyebrow}
        for i in range(1, 6):
            q, a = items[i - 1] if i <= len(items) else ("", "")
            f[f"faq_{i}_question"] = q
            f[f"faq_{i}_answer"] = a
        return f

    if family == "Timeline":
        # timeline: heading, step_1..4_label/heading/text (three fields per
        # step, not two). No `{% if %}` gate on any step, so an unused slot
        # must be fully blanked (label included) or it renders as a hollow row.
        steps = _timeline_steps(copy, 4)
        f = {"heading": eyebrow}
        for i in range(1, 5):
            h, t = steps[i - 1] if i <= len(steps) else ("", "")
            f[f"step_{i}_label"] = (f"Step {i}" if (h or t) else "")
            f[f"step_{i}_heading"] = h
            f[f"step_{i}_text"] = t
        return f

    if family == "Comparison":
        # visual_comparison_cards: eyebrow, card_1..3_name/attr_1/attr_2. No
        # body field at all, so a dynamic-instruction copy block (C-2's
        # `{{ dynamic: ... }}`) is carried visibly in card_1_name; cards 2 and
        # 3 are explicitly blanked so 'Option B'/'Option C' cannot leak in.
        card1 = f"[ {copy} ]" if copy else f"[ {family} — no content supplied ]"
        return {"eyebrow": eyebrow, "card_1_name": card1,
                "card_1_attr_1": "", "card_1_attr_2": "",
                "card_2_name": "", "card_2_attr_1": "", "card_2_attr_2": "",
                "card_3_name": "", "card_3_attr_1": "", "card_3_attr_2": ""}

    if family.startswith(("PULL", "OFFER")) or family == "Review stars":
        # Review stars (round 2): MODULE_MAP now maps it to None — its live
        # module hardcodes five star glyphs regardless of field values, so no
        # field mapping can honestly satisfy "no fabricated stars." It renders
        # through the same labelled-placeholder path as the three commerce
        # modules with no live source.
        # PULL/OFFER: defensive only — after the Task 1 fix these bracketed
        # copy-desk instructions no longer parse as their own family, they
        # arrive as copy text inside another family's block (handled by the
        # branches above). Kept in case a stray one ever slips through unparsed.
        return placeholder_fields(family, qualifier, copy)

    # every remaining text-ish family renders as a titled block
    return _base(eyebrow=eyebrow, heading="", body_text=_paras(copy))
