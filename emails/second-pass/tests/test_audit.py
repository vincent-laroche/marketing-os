import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from audit import card_bg

# A real module template that opens its final-card unconditionally (the correct
# shape) — `card_bg` must recover the background hex and never flag this blank.
REAL_CARD = (
    '<style>@media only screen and (max-width:480px){.final-card{width:100%!important}}</style>'
    '<table role="presentation" width="100%" style="width:100%;background:transparent;'
    'border-radius:16px;overflow:hidden;border-collapse:separate;">'
    '<tr><td align="center" style="padding:0;border-radius:16px;">'
    '<table role="presentation" class="final-card" width="600" '
    'style="width:600px;max-width:100%;background:#EFE7D2;border-radius:16px;'
    'overflow:hidden;border-collapse:separate;">'
    '<tr><td class="final-pad" style="padding:32px;">Real body copy goes here.</td></tr>'
    '</table></td></tr></table>'
)

# The exact shape the nine buggy live templates produce when `{% if
# module.button_label %}` gates the whole card (not just the button) and that
# condition is false: only the responsive style tag and a run of orphaned
# closing tags survive `strip_ifs`. No `class="final-card"` ever appears.
BLANK_RENDER = (
    '<style>@media only screen and (max-width:480px){.final-card{width:100%!important}'
    '.final-pad{padding:24px!important}.final-card td{box-sizing:border-box}}</style>'
    '</td></tr></table></td></tr></table>'
)


def test_real_content_block_is_not_flagged():
    """A block that actually opened its card must resolve to that card's bg,
    not be mistaken for a blank render."""
    assert card_bg(REAL_CARD) == "#EFE7D2"


def test_blank_render_is_detected():
    """A block whose conditional wrapping swallowed its own opening tags —
    the live text_base_type_guidance / plain_text_founder_wrapper / support_strip
    / etc. bug — must be detected as rendering no visible content."""
    assert card_bg(BLANK_RENDER) is None


def test_detection_survives_across_surfaces_and_case():
    """The regex keys off `class="final-card"...background:#HEX`, independent of
    which surface produced the hex or its letter case in the source markup."""
    ink_card = REAL_CARD.replace("#EFE7D2", "#15140f")
    assert card_bg(ink_card) == "#15140F"
