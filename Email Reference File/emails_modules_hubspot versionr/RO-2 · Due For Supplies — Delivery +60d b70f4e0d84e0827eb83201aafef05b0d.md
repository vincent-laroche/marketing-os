# RO-2 · Due For Supplies — Delivery +60d

Body: [Hero - Text-led]
You're about due for supplies.

[Text - Opening]
Hi {{ firstname }},

You last ordered supplies {{ days_since_supply_order }} days ago.

At a normal reapplication cycle, that's about when adhesive and remover run out. Not a guess — that's the maths on a two-week bond.

The reason I flag it: running out mid-cycle is when people improvise with the wrong solvent, and that's the single most common way a good system gets ruined.

[Product - Dynamic recommendations] (recommended)
What you'd normally need now:
{{ recommended_reorder_items }}

[Text - Reassurance]
If you've changed routine and need something different, reply and tell me what you're using now — I'll adjust the list rather than send you the default.

Vincent

[Button - Primary CTA]
Reorder supplies →

[Footer - Preference centre]
Build Status: Needs building in HubSpot
CTA: Reorder supplies →
Email Channel: Marketing
HubSpot Email ID: 214989746983
Hubspot Matched: Yes
Module Stack: (Header - Centered logo) (Hero - Text-led) (Text - Opening) [Product - Dynamic recommendations] (Text - Reassurance) (Button - Primary CTA: reorder supplies) (Footer - Preference centre)
Modules Used: Header - Centered logo - Light (https://app.notion.com/p/Header-Centered-logo-Light-586f4e0d84e0821a960b015f18443fb8?pvs=21), Hero - Text-led - Light (https://app.notion.com/p/Hero-Text-led-Light-963f4e0d84e08227a47b8102d3cfa40c?pvs=21), Text - Opening - Light (https://app.notion.com/p/Text-Opening-Light-09af4e0d84e08274be7e01b5ade1e13c?pvs=21), Product - Dynamic recommendations - Light (https://app.notion.com/p/Product-Dynamic-recommendations-Light-bcaf4e0d84e082ef91cd016f15fff865?pvs=21), Text - Reassurance - Light (https://app.notion.com/p/Text-Reassurance-Light-5d3f4e0d84e082fe98ef010e47535c71?pvs=21), Button - Primary CTA - Light (https://app.notion.com/p/Button-Primary-CTA-Light-5cef4e0d84e08240b53a0126a9c9667a?pvs=21), Footer - Preference centre - Light (https://app.notion.com/p/Footer-Preference-centre-Light-fa4f4e0d84e082819ba601163ca05b5a?pvs=21)
Position: 2
Preview Text: Based on when you last ordered, not a guess.
Series: J4 · Reorder · Master
Series Total: 6
Subject: You're about due for supplies
Subscription Type: Hair Care Guidance
Workflow IDs: Journey · Reorder · Master

<aside>
✉️ Subject: You're about due for supplies
Preview: Based on when you last ordered, not a guess.

</aside>

### Body

Hi {{ firstname }},

You last ordered supplies {{ days_since_supply_order }} days ago.

At a normal reapplication cycle, that's about when adhesive and remover run out. Not a guess — that's the maths on a two-week bond.

What you'd normally need now:
{{ recommended_reorder_items }}

The reason I flag it: running out mid-cycle is when people improvise with the wrong solvent, and that's the single most common way a good system gets ruined.

If you've changed routine and need something different, reply and tell me what you're using now.

Vincent

### CTA

Reorder supplies →

---

### Build notes

Timing: Delivery + 60 days · consumables branch. Keep record: Reorder Subscription 1of3 — Friendly Reminder (214989746983, this record). Requires days_since_supply_order from the Data workflows — do NOT send this email with an unresolved token.

Journey: Journey · Reorder · Master · Subscription: Hair Care Guidance · Module stack: (Header - Centered logo) (Layout - Plain-text founder wrapper) [Product - Dynamic recommendations] (Footer - Preference centre)