# PP-7b · UGC Photo Request — PP-7 positive +7d

Body: [Hero - Text-led]
The photo that convinces the next person.

[Text - Opening]
Hi {{ personalization_token('contact.firstname', 'there') }},

Thanks for the feedback last week — it genuinely helps.

One more ask, and this one's bigger: would you be willing to let us show your result?

Here's why I'm asking. The single thing that stops people ordering is the fear it will look obvious. No amount of copy from me fixes that. One photo from someone who was in their position does.

[Text - Customer snapshot]
{{ dynamic: product ordered — name, base type, order date }}

[Photo - Feature story: example UGC]
{{ image: example of a good customer submission }}

[Testimonial: what a good one looks like]
[PULL: one consented customer photo + quote from the approved library, shown as the example]

A good one is simple: natural daylight, straight on and slightly angled, no filter. Front hairline is what people want to see. You don't need to show your face — plenty of people don't, and it still works.

[Text - Offer discount: incentive]
[OFFER — confirm before send: UGC incentive, e.g. store credit or discount on next order]

[List - Questions] (optional)
· What did you look like before, if you're comfortable sharing?
· What convinced you to finally order?
· What would you tell someone still deciding?

[Text - Reassurance]
You control exactly how it's used. Nothing gets published without your written say-so, we'll never use your full name unless you want us to, and you can ask us to pull it at any point, permanently, no questions.

[Button - Primary CTA]
Share my photo →

[M10 Support strip] (optional)
Rather not? Completely fine — reply and I'll take you off this ask.

[Footer - Social]
Build Status: Needs workflow wiring
Email Channel: Service
HubSpot Email ID: 214987971586
Hubspot Matched: Yes
Module Stack: (Header) → (Hero - Text-led) → (Text - Opening) → (Text - Customer snapshot) → (Photo - Feature story: example UGC) → (Testimonial: what a good one looks like) → (Text - Offer discount: incentive) → [List - Questions] → [Text - Reassurance] → (Button - Primary CTA) → [M10 Support strip] → (Footer - Social)
Modules Used: Header - Centered logo - Light (https://app.notion.com/p/Header-Centered-logo-Light-586f4e0d84e0821a960b015f18443fb8?pvs=21), Hero - Text-led - Light (https://app.notion.com/p/Hero-Text-led-Light-963f4e0d84e08227a47b8102d3cfa40c?pvs=21), Text - Opening - Light (https://app.notion.com/p/Text-Opening-Light-09af4e0d84e08274be7e01b5ade1e13c?pvs=21), Text - Customer snapshot - Light (https://app.notion.com/p/Text-Customer-snapshot-Light-02bf4e0d84e0820fbfcf816d63fe68ae?pvs=21), Photo - Feature story - Light (https://app.notion.com/p/Photo-Feature-story-Light-fd5f4e0d84e0833bb12d0192e338778d?pvs=21), Testimonial - Light (https://app.notion.com/p/Testimonial-Light-955f4e0d84e083e1a17501a482a51f91?pvs=21), Text - Offer discount - Light (https://app.notion.com/p/Text-Offer-discount-Light-a36f4e0d84e083db94f501d582855339?pvs=21), List - Questions - Light (https://app.notion.com/p/List-Questions-Light-190f4e0d84e083418a230178ca6196ec?pvs=21), Text - Reassurance - Light (https://app.notion.com/p/Text-Reassurance-Light-5d3f4e0d84e082fe98ef010e47535c71?pvs=21), Button - Primary CTA - Light (https://app.notion.com/p/Button-Primary-CTA-Light-5cef4e0d84e08240b53a0126a9c9667a?pvs=21), List - Support strip - Light (https://app.notion.com/p/List-Support-strip-Light-9e5f4e0d84e0829299b3811647c638e6?pvs=21), Footer - Social - Light (https://app.notion.com/p/Footer-Social-Light-746f4e0d84e083999c1d815025958c68?pvs=21)
Position: 8
Series: J1 · Post-Purchase · Master
Series Total: 7
Subject: Would you let us show your result?
Subscription Type: Customer Service Communication
Workflow IDs: Journey · Post-Purchase · Master

## Legacy HubSpot body (pre-Atelier Zero)

*Migrated from module_usage_master — legacy Email ID 214987971586 (WF-Review-02-UGC-Photo-Request).*

```html
<p>Hi {{ personalization_token("contact.firstname", "there") }},</p>

<p>I have a small request — and there's something in it for you.</p>

<p>We're building a gallery of real customers wearing our hair systems, and I'd love to feature <strong>your look</strong>.</p>

<p><strong>Here's how it works:</strong></p>
<ol>
<li>Take a photo of yourself wearing your system (selfie works great!)</li>
<li>Reply to this email with the photo, or upload it through our form</li>
<li>We'll feature you on our website (with your permission)</li>
</ol>

<p><strong>What's in it for you:</strong></p>
<ul>
<li>🎉 Featured on our website's customer gallery</li>
<li>💰 <strong>10% off your next order</strong> as a thank you</li>
<li>🤝 Help other guys see that real people get real results</li>
</ul>

<p><a href="https://hairsolutions.co/pages/share-your-look?utm_source=hubspot&utm_medium=email&utm_campaign=review-flow&utm_content=wf-review-02&utm_term=hero-cta" style="background-color:#1a1a2e;color:#ffffff;padding:12px 24px;text-decoration:none;border-radius:4px;display:inline-block;font-weight:bold;">Share Your Photo →</a></p>

<p>No professional photography needed — just a natural shot that shows your system in action.</p>

<p>Thanks,<br>
Vincent</p>
```