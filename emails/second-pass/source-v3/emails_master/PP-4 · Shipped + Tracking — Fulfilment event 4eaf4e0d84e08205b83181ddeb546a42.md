# PP-4 · Shipped + Tracking — Fulfilment event

Body: [Hero - Text-led]
It's shipped.

[Text - Opening]
Hi {{ firstname }},

Your system is on its way. When it arrives, do these four things in order:

1. Open it over a table, not a sink. The lace is fine and static-prone.
2. Check the colour against your own hair in daylight, not indoors.
3. Don't cut anything yet. Try it on untrimmed first.
4. Take a photo of it as it came, before any modification.

That last one matters. If something isn't right, a photo of the unmodified system is what lets me sort it out for you quickly.

Vincent

[Commerce - Shipping tracking]
Tracking: {{ tracking_number }}
Carrier: {{ carrier }}
Expected: {{ estimated_delivery_date }}

[Button - Primary CTA]
Track your order →

[List - Support strip]
Delivery problem or damaged box? Reply with a photo and I'll take it from there.

[Footer - Preference centre]
Build Status: Needs building in HubSpot
CTA: Track your order →
Email Channel: Marketing
HubSpot Email ID: 214989746974
Hubspot Matched: Yes
Module Stack: (Header - Centered logo) (Hero - Text-led) (Text - Opening) (Commerce - Shipping tracking) (Button - Primary CTA: track your order) (List - Support strip) (Footer - Preference centre)
Modules Used: Header - Centered logo - Light (https://app.notion.com/p/Header-Centered-logo-Light-586f4e0d84e0821a960b015f18443fb8?pvs=21), Hero - Text-led - Light (https://app.notion.com/p/Hero-Text-led-Light-963f4e0d84e08227a47b8102d3cfa40c?pvs=21), Text - Opening - Light (https://app.notion.com/p/Text-Opening-Light-09af4e0d84e08274be7e01b5ade1e13c?pvs=21), Commerce - Shipping tracking - Light (https://app.notion.com/p/Commerce-Shipping-tracking-Light-c1ff4e0d84e08364a13401d6c47ba904?pvs=21), Button - Primary CTA - Light (https://app.notion.com/p/Button-Primary-CTA-Light-5cef4e0d84e08240b53a0126a9c9667a?pvs=21), List - Support strip - Light (https://app.notion.com/p/List-Support-strip-Light-9e5f4e0d84e0829299b3811647c638e6?pvs=21), Footer - Preference centre - Light (https://app.notion.com/p/Footer-Preference-centre-Light-fa4f4e0d84e082819ba601163ca05b5a?pvs=21)
Position: 4
Preview Text: Plus the quick-start steps for the day it lands.
Series: J1 · Post-Purchase · Master
Series Total: 7
Subject: It's shipped — tracking inside
Subscription Type: Order & Shipping Updates
Workflow IDs: Journey · Post-Purchase · Master

<aside>
✉️ Subject: It's shipped — tracking inside
Preview: Plus the quick-start steps for the day it lands.

</aside>

### Body

Hi {{ firstname }},

Your system is on its way.

Tracking: {{ tracking_number }}
Carrier: {{ carrier }}
Expected: {{ estimated_delivery_date }}

When it arrives, do these four things in order:

1. Open it over a table, not a sink. The lace is fine and static-prone.
2. Check the colour against your own hair in daylight, not indoors.
3. Don't cut anything yet. Try it on untrimmed first.
4. Take a photo of it as it came, before any modification.

That last one matters. If something isn't right, a photo of the unmodified system is what lets me sort it out for you quickly.

Vincent

### CTA

Track your order →

---

### Build notes

Timing: on fulfilment event — NOT a fixed delay. Replaces Post-Purchase 1of3 — Delivery QuickStart (214989746974, this record). Critical change: originally fired at +0d, before the item shipped; must be re-triggered off the fulfilment webhook.

Journey: Journey · Post-Purchase · Master · Subscription: Order & Shipping Updates · Module stack: (Header - Centered logo) (Layout - Plain-text founder wrapper) (Commerce - Shipping tracking) (Footer - Preference centre)