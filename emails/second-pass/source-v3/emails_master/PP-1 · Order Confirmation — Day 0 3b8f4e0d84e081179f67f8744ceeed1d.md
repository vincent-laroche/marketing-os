# PP-1 · Order Confirmation — Day 0

Body: [Hero - Text-led]
Your order is confirmed, {{ firstname }}.

[Text - Opening]
Hi {{ firstname }},

Your order is in. Thank you — genuinely.

Here's what happens now. Your system isn't sitting on a shelf waiting to be boxed; it gets made for you. That takes time, and I'd rather tell you that up front than have you wondering where it is.

[Commerce - Order summary]
Order number: {{ order_number }}
What you ordered: {{ product_summary }}
Estimated dispatch: {{ estimated_ship_date }}

[List - Questions: what happens next timeline]
1. Production starts — the base is cut and the hair is hand-tied to your spec
2. I email you when it goes into production
3. I email you when it ships, with tracking
4. It should be at your door around {{ estimated_delivery_date }}

No filler emails in between — only the real steps.

[Text - Reassurance]
If anything about your order looks wrong, reply to this email today and I'll fix it before production starts.

Vincent
Founder, Hair Solutions Co.

[Button - Primary CTA]
View your order →

[List - Support strip]
Questions about your order? Reply to this email — it comes straight to me.

[Footer - Preference centre]
Build Status: Needs building in HubSpot
CTA: View your order →
Email Channel: Marketing
Hubspot Matched: No
Module Stack: (Header - Centered logo) (Hero - Text-led) (Text - Opening) (Commerce - Order summary) (List - Questions: what happens next timeline) (Text - Reassurance) (Button - Primary CTA: view your order) (List - Support strip) (Footer - Preference centre)
Modules Used: Header - Centered logo - Light (https://app.notion.com/p/Header-Centered-logo-Light-586f4e0d84e0821a960b015f18443fb8?pvs=21), Hero - Text-led - Light (https://app.notion.com/p/Hero-Text-led-Light-963f4e0d84e08227a47b8102d3cfa40c?pvs=21), Text - Opening - Light (https://app.notion.com/p/Text-Opening-Light-09af4e0d84e08274be7e01b5ade1e13c?pvs=21), Commerce - Order summary - Light (https://app.notion.com/p/Commerce-Order-summary-Light-d9ef4e0d84e082baa296018240d67098?pvs=21), List - Questions - Light (https://app.notion.com/p/List-Questions-Light-190f4e0d84e083418a230178ca6196ec?pvs=21), Text - Reassurance - Light (https://app.notion.com/p/Text-Reassurance-Light-5d3f4e0d84e082fe98ef010e47535c71?pvs=21), Button - Primary CTA - Light (https://app.notion.com/p/Button-Primary-CTA-Light-5cef4e0d84e08240b53a0126a9c9667a?pvs=21), List - Support strip - Light (https://app.notion.com/p/List-Support-strip-Light-9e5f4e0d84e0829299b3811647c638e6?pvs=21), Footer - Preference centre - Light (https://app.notion.com/p/Footer-Preference-centre-Light-fa4f4e0d84e082819ba601163ca05b5a?pvs=21)
Position: 1
Preview Text: Here's exactly what happens between now and the day it arrives.
Series: J1 · Post-Purchase · Master
Series Total: 7
Subject: Your order is confirmed, {{ firstname }}
Subscription Type: Order & Shipping Updates
Workflow IDs: Journey · Post-Purchase · Master

<aside>
✉️ Subject: Your order is confirmed, {{ firstname }}
Preview: Here's exactly what happens between now and the day it arrives.

</aside>

### Body

Hi {{ firstname }},

Your order is in. Thank you — genuinely.

Here's what happens now. Your system isn't sitting on a shelf waiting to be boxed; it gets made for you. That takes time, and I'd rather tell you that up front than have you wondering where it is.

Order number: {{ order_number }}
What you ordered: {{ product_summary }}
Estimated dispatch: {{ estimated_ship_date }}

I'll email you at each real step — when it goes into production, when it ships, and when it should be at your door. No filler in between.

If anything about your order looks wrong, reply to this email today and I'll fix it before production starts.

Vincent
Founder, Hair Solutions Co.

### CTA

View your order →

---

### Build notes

Timing: Day 0 · immediately on order. Replaces New Customer 1of4 — Order Confirmation (rewrite content, keep HubSpot record; confirm ID in portal) plus two archived duplicates. Why: the original promised nothing specific — setting the production expectation here prevents the 'where is my order' ticket on day six.

Journey: Journey · Post-Purchase · Master · Subscription: Order & Shipping Updates · Module stack: (Header - Centered logo) (Layout - Plain-text founder wrapper) (Commerce - Order summary) (Footer - Preference centre)