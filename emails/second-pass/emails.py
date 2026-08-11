# -*- coding: utf-8 -*-
"""The 20 journey emails, composed from Notion `emails_master`.

Copy is verbatim from Notion. Nothing here is written by hand except the module
assignment and the surface choice. Where a letter contained a label/value block or
a promo code inline, that block is MOVED into the module built for it — the labels
are the copy's own words, so this is redistribution, not invention.

Surfaces are Paper, Ink or Coral only (revised 2026-08-11). Bone, Paper Dark and Ink
Soft are supporting colours and never a section background, so an email now reads as
one continuous field rather than a stack of separately tinted cards. Each journey
commits to a register; Coral appears exactly four times across the twenty-two.
"""

P = lambda *paras: "".join("<p style='margin:0 0 16px;'>%s</p>" % p for p in paras)

HS = "https://hairsolutions.co"

# ---------------------------------------------------------------- POST-PURCHASE
PP1 = dict(
    code="PP-1", journey="Post-Purchase", pos="1 of 7",
    subject="Your order is confirmed, {{ firstname }}",
    preview="Here's exactly what happens between now and the day it arrives.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Your order is in. Thank you — genuinely.",
                "Here's what happens now. Your system isn't sitting on a shelf waiting to be "
                "boxed; it gets made for you. That takes time, and I'd rather tell you that up "
                "front than have you wondering where it is.",
                "I'll email you at each real step — when it goes into production, when it ships, "
                "and when it should be at your door. No filler in between.",
                "If anything about your order looks wrong, reply to this email today and I'll fix "
                "it before production starts."),
            signature="Vincent<br>Founder, Hair Solutions Co.",
            show_button="yes", button_label="View your order",
            button_url={"href": HS + "/account/orders"})),
        # the three label/value lines lifted out of the letter
        ("commerce_order_summary", "paper", dict(
            eyebrow="Your order", heading="What's being made",
            label_order="Order number", value_order="{{ order_number }}",
            label_spec="What you ordered", value_spec="{{ product_summary }}",
            label_status="Status", value_status="In production",
            label_eta="Estimated dispatch", value_eta="{{ estimated_ship_date }}",
            note="", button_label="", button_url={"href": "#"})),
        ("preference_opt_down", "paper", {}),
    ])

PP2 = dict(
    code="PP-2", journey="Post-Purchase", pos="2 of 7",
    subject="Getting ready for your system — a short prep guide",
    preview="Three things worth doing before it arrives. Ten minutes, total.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "While your system is being made, there are three small things worth doing. None "
                "take long, and they make the first fitting go much better.",
                "1. Clear a workspace with a good mirror and decent light. Bathroom mirrors are "
                "usually the worst light in the house.",
                "2. Check what you have. You'll want adhesive or tape, scissors you trust, and "
                "rubbing alcohol for prep. If you're missing something, order it now so it "
                "arrives before the system does.",
                "3. Watch the fitting walkthrough once, before you need it. It's twelve minutes "
                "and it will save you an hour of guessing.",
                "One more thing: your first fitting will not be your best fitting. That's true for "
                "everyone. By the third you'll have it down."),
            signature="Vincent",
            show_button="yes", button_label="Read the prep guide",
            button_url={"href": HS + "/pages/prep-guide"})),
        ("preference_opt_down", "paper", {}),
    ])

PP3 = dict(
    code="PP-3", journey="Post-Purchase", pos="3 of 7",
    subject="Your system is on the bench",
    preview="A look at what's actually happening to it right now.",
    blocks=[
        ("header_centered_logo", "ink", {}),
        ("plain_text_founder_wrapper", "ink", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Quick update: your system is in production.",
                "What that means in practice — the base is cut to your specification, and the hair "
                "is being tied into it by hand, a few strands at a time. A full unit is somewhere "
                "between twenty and thirty thousand knots. It's slow work, and it's the reason the "
                "wait exists.",
                "This is also the part that decides whether a hairline looks real or looks like a "
                "wig. There's no way to rush it without it showing.",
                "Nothing needed from you. My next email is the dispatch notice with your tracking "
                "number."),
            signature="Vincent",
            show_button="yes", button_label="See how a system is made",
            button_url={"href": HS + "/pages/how-its-made"})),
        ("preference_opt_down", "ink", {}),
    ])

PP4 = dict(
    code="PP-4", journey="Post-Purchase", pos="4 of 7",
    subject="It's shipped — tracking inside",
    preview="Plus the quick-start steps for the day it lands.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Your system is on its way.",
                "When it arrives, do these four things in order:",
                "1. Open it over a table, not a sink. The lace is fine and static-prone.<br>"
                "2. Check the colour against your own hair in daylight, not indoors.<br>"
                "3. Don't cut anything yet. Try it on untrimmed first.<br>"
                "4. Take a photo of it as it came, before any modification.",
                "That last one matters. If something isn't right, a photo of the unmodified system "
                "is what lets me sort it out for you quickly."),
            signature="Vincent",
            show_button="no", button_label="", button_url={"href": "#"})),
        # the milestone moment of the whole journey — the one coral panel
        ("commerce_shipping_tracking", "coral", dict(
            eyebrow="On its way", heading="Track your delivery",
            label_carrier="Carrier", value_carrier="{{ carrier }}",
            label_tracking="Tracking", value_tracking="{{ tracking_number }}",
            label_eta="Expected", value_eta="{{ estimated_delivery_date }}",
            note="", button_label="Track your order",
            button_url={"href": HS + "/account/orders"})),
        ("preference_opt_down", "paper", {}),
    ])

PP5 = dict(
    code="PP-5", journey="Post-Purchase", pos="5 of 7",
    subject="Your 30 / 60 / 90 day maintenance calendar",
    preview="What to do, and when, so it lasts as long as it should.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "You've had your system about a week. This is the right moment for the maintenance "
                "schedule, because the habits you set now are the ones that stick.",
                "Every 7–14 days — full removal, clean the base, clean your scalp, reapply. Don't "
                "stretch this. Adhesive left too long is the single most common cause of base damage.",
                "Every 30 days — deep clean. Solvent soak, gentle brush along the knots, air dry "
                "flat. Never wring it.",
                "Every 60 days — inspect the perimeter. Lace goes at the front edge first. Catching "
                "a small tear here is a repair; missing it is a replacement.",
                "Every 90 days — assess honestly. Most systems have a usable life of three to six "
                "months depending on wear and care. Knowing where you are in that cycle means "
                "you're never caught out.",
                "Two things shorten a system's life more than anything else: heat styling directly "
                "on the base, and sleeping in it without a wrap. Neither is forbidden. Both cost "
                "you weeks.",
                "Reply with any question at all — I answer these myself."),
            signature="Vincent",
            show_button="yes", button_label="Save the care schedule",
            button_url={"href": HS + "/pages/care-schedule"})),
        ("preference_opt_down", "paper", {}),
    ])

PP7 = dict(
    code="PP-7", journey="Post-Purchase", pos="7 of 7",
    subject="Honestly — how's it going?",
    preview="One question. Good or bad, I want the real answer.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "You've had your system about five weeks now — long enough to know how you feel "
                "about it.",
                "<b>How's it going?</b>",
                "If it's going well, the first button takes you to a review page. Reviews are how "
                "people in the same position you were in five weeks ago decide whether to trust us.",
                "If it isn't right, the second comes straight to me. Fit, colour, density, "
                "adhesion, anything. No form, no ticket queue — it's my inbox. Most issues at this "
                "stage are fixable, and the ones that aren't, I'd still rather know about."),
            signature="Vincent<br>Founder, Hair Solutions Co.",
            show_button="no", button_label="", button_url={"href": "#"})),
        # the letter explicitly says "the first button" / "the second" — it needs two
        ("cta_dual_buttons", "paper", dict(
            eyebrow="", heading="", body_text="",
            primary_label="It's going well", primary_url={"href": HS + "/pages/review"},
            secondary_label="It's not quite right",
            secondary_url={"href": "mailto:vincent@hairsolutions.co"})),
        ("footer_standard", "paper", {}),   # the one email in the set using Standard
    ])

# ------------------------------------------------------------- CART RECOVERY
CR1 = dict(
    code="CR-1", journey="Cart Recovery", pos="1 of 5",
    subject="Your cart's still here",
    preview="No pressure — just making sure nothing broke on our end.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "You were partway through an order and stopped. That's completely fine — but "
                "occasionally it's because something on our side didn't work, and I'd want to know.",
                "Still in your cart:<br>{{ cart_contents }}",
                "If it was a payment error, a shipping surprise, or the page just froze, reply and "
                "tell me. I'll sort it out.",
                "If you're still deciding, no rush at all. Your cart's saved."),
            signature="Vincent",
            show_button="yes", button_label="Finish your order",
            button_url={"href": HS + "/cart"})),
        ("preference_opt_down", "paper", {}),
    ])

CR2 = dict(
    code="CR-2", journey="Cart Recovery", pos="2 of 5",
    subject="The three things people ask before ordering",
    preview="Will it look real, will it hold, and what if it's wrong.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Most people who hesitate at checkout are stuck on one of three things. Here they "
                "are, answered straight.",
                "<b>&ldquo;Will it actually look real?&rdquo;</b><br>At conversation distance, a "
                "well-fitted lace front is not detectable. The giveaway is never the hair — it's a "
                "hairline set too low, or a density too high for your age. We set both "
                "conservatively for exactly that reason.",
                "<b>&ldquo;Will it hold?&rdquo;</b><br>With clean prep and the right adhesive, a "
                "bond holds 7 to 14 days through showering, sweating and sleeping. Prep is the "
                "variable, not the product, and we walk you through it.",
                "<b>&ldquo;What if it's not right when it arrives?&rdquo;</b><br>Then you email me "
                "and we fix it. Colour off, density wrong, base size out — those are on us to "
                "resolve, and we do.",
                "Still in your cart: {{ cart_contents }}"),
            signature="Vincent",
            show_button="yes", button_label="See what customers say",
            button_url={"href": HS + "/pages/reviews"})),
        ("preference_opt_down", "paper", {}),
    ])

CR3 = dict(
    code="CR-3", journey="Cart Recovery", pos="3 of 5",
    subject="Not sure you picked the right one?",
    preview="Tell me your situation and I'll tell you what I'd choose.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "There's one reason for stalling I haven't covered, and it's the most common: "
                "you're not certain you chose the right system.",
                "That's reasonable. Base type, density, hairline, colour — it's a lot of decisions "
                "to make from product photos.",
                "So here's an easier route. Reply to this email with:",
                "— how you currently wear your hair<br>— whether you want daily removal or a "
                "longer bond<br>— your rough age bracket",
                "That's enough for me to tell you which base and density I'd actually recommend, "
                "and whether what's in your cart is right. If it isn't, I'll say so, even if the "
                "answer is a cheaper unit.",
                "Or if you'd rather talk it through properly, book fifteen minutes with me."),
            signature="Vincent",
            show_button="yes", button_label="Book 15 minutes",
            button_url={"href": HS + "/pages/consultation"})),
        ("preference_opt_down", "paper", {}),
    ])

CR4 = dict(
    code="CR-4", journey="Cart Recovery", pos="4 of 5",
    subject="Last note about your cart",
    preview="Free shipping if it helps. Either way, this is the last one.",
    blocks=[
        ("header_centered_logo", "ink", {}),
        ("plain_text_founder_wrapper", "ink", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Last email about this — I won't keep bringing it up.",
                "If cost is the sticking point, here's free shipping on the order.",
                "{{ cart_contents }}",
                "And if the timing just isn't right, that's genuinely fine. Your cart stays saved, "
                "the code will be honoured whenever you come back, and I'll stop emailing you "
                "about it."),
            signature="Vincent<br>Founder, Hair Solutions Co.",
            show_button="no", button_label="", button_url={"href": "#"})),
        # code + validity lifted out of the letter
        ("promo_code_block", "coral", dict(
            heading="Free shipping on this order", promo_code="FREESHIP",
            terms_text="Valid for 72 hours.",
            button_label="Complete your order", button_url={"href": HS + "/cart"})),
        ("preference_opt_down", "ink", {}),
    ])

BR1 = dict(
    code="BR-1", journey="Cart Recovery", pos="5 of 5",
    subject="Still weighing up base types?",
    preview="Lace, poly, or hybrid — the two-minute version.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "You were looking at {{ last_viewed_product }}. Before you go further, the base "
                "type question is worth two minutes, because it decides more about your day-to-day "
                "than anything else.",
                "If you tell me how you live — gym, heat, hats, how often you want to remove it — "
                "I'll tell you which one I'd pick."),
            signature="Vincent",
            show_button="no", button_label="", button_url={"href": "#"})),
        ("text_base_type_guidance", "paper", dict(
            eyebrow="Base types", heading="Lace, poly, or hybrid",
            body_text=P(
                "<b>Lace</b> — most natural at the hairline, most breathable, shortest life. Best "
                "if appearance is the priority and you don't mind replacing more often.",
                "<b>Poly</b> — most durable, easiest to clean and reapply, slightly less invisible "
                "up close. Best if you want low maintenance and a long bond.",
                "<b>Hybrid</b> — lace front for the hairline, poly at the sides and back. Most "
                "people end up here."),
            show_button="yes", button_label="Compare base types",
            button_url={"href": HS + "/pages/base-types"})),
        ("preference_opt_down", "paper", {}),
    ])

# ------------------------------------------------------------------- WIN-BACK
WB1 = dict(
    code="WB-1", journey="Win-Back", pos="1 of 4",
    subject="Checking in — Vincent here",
    preview="No offer attached. Just wondering how you got on.",
    blocks=[
        ("header_centered_logo", "ink", {}),
        ("plain_text_founder_wrapper", "ink", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "It's been a while — your last order with us was {{ months_since_last_order }} "
                "months ago.",
                "No pitch in this email. I'm just curious how you got on.",
                "If you're still wearing a system and it's working, that's good to hear and you "
                "can ignore this.",
                "If you stopped, I'd honestly like to know why. Was it the maintenance? The cost? "
                "Did the fit never come right? Did you go a different route entirely?",
                "I read every reply, and the answers change what we make. The most useful feedback "
                "I've had all year came from people who stopped buying."),
            signature="Vincent<br>Founder, Hair Solutions Co.",
            show_button="no", button_label="", button_url={"href": "#"})),  # reply-only by design
        ("preference_opt_down", "ink", {}),
    ])

WB2 = dict(
    code="WB-2", journey="Win-Back", pos="2 of 4",
    subject="What's changed since you last ordered",
    preview="Three things, briefly. Some of them fix the reasons people leave.",
    blocks=[
        ("header_centered_logo", "ink", {}),
        ("plain_text_founder_wrapper", "ink", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "If it's been a while, a few things are genuinely different now.",
                "<b>Better hybrid bases.</b> The lace-front-poly-back construction we now stock "
                "lasts noticeably longer than the full-lace units most people started on. If yours "
                "never lasted long enough to feel worth it, this is the reason why.",
                "<b>Real tracking, end to end.</b> You can see your unit's status from production "
                "through to delivery. The old &ldquo;it ships when it ships&rdquo; problem is gone.",
                "<b>Maintenance plans.</b> If the every-two-weeks routine was what wore you down, "
                "supplies can arrive automatically on schedule instead of you remembering.",
                "Still no offer. If one of these solves the thing that stopped you, that's the point."),
            signature="Vincent",
            show_button="yes", button_label="See what's changed",
            button_url={"href": HS + "/pages/whats-new"})),
        ("preference_opt_down", "ink", {}),
    ])

WB3 = dict(
    code="WB-3", journey="Win-Back", pos="3 of 4",
    subject="20% off, if you want to try again",
    preview="Your previous specification is saved — reordering takes a minute.",
    blocks=[
        ("header_centered_logo", "ink", {}),
        ("plain_text_founder_wrapper", "ink", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Now the offer, since I said I'd get to it.",
                "So if you want the same again, it's about a minute. If you'd rather change base "
                "type or density based on how the last one went, reply and tell me what didn't "
                "work — I'll adjust the spec myself before it goes to production."),
            signature="Vincent",
            show_button="no", button_label="", button_url={"href": "#"})),
        ("promo_code_block", "coral", dict(
            heading="20% off your next system", promo_code="WELCOMEBACK20",
            terms_text="Valid 14 days.",
            button_label="Reorder with 20% off", button_url={"href": HS + "/collections/systems"})),
        ("commerce_quote_spec_table", "ink", dict(
            eyebrow="Still on file", heading="Your last specification",
            label_1="Specification", value_1="{{ last_order_specification }}",
            label_2="", value_2="", label_3="", value_3="",
            label_4="", value_4="", label_5="", value_5="",
            note="If this is empty we'll confirm your spec before production.",
            button_label="", button_url={"href": "#"})),
        ("preference_opt_down", "ink", {}),
    ])

WB4 = dict(
    code="WB-4", journey="Win-Back", pos="4 of 4",
    subject="Last email from us",
    preview="We'll stop here unless you tell us otherwise.",
    blocks=[
        ("header_centered_logo", "ink", {}),
        ("plain_text_founder_wrapper", "ink", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "This is the last marketing email you'll get from us.",
                "You haven't opened anything in a while, and I'd rather stop than keep arriving in "
                "an inbox where I'm not wanted. In a week I'll quietly remove you from our "
                "marketing list. You don't need to do anything.",
                "Either way, your account and order history stay intact, and you can buy from the "
                "site any time without being on a list. If you ever need help with a system — even "
                "one you didn't buy from us — my inbox is open. That doesn't expire.",
                "Thanks for having given us a go."),
            signature="Vincent<br>Founder, Hair Solutions Co.",
            show_button="no", button_label="", button_url={"href": "#"})),
        # the only email whose opt-down ask is real copy, so it fills those fields
        ("preference_opt_down", "ink", dict(
            eyebrow="If you'd like to stay",
            heading="One click keeps you on",
            # the letter already closes with "Thanks for having given us a go."
            body_text="",
            button_label="Keep me on the list",
            button_url={"href": HS + "/pages/preferences"})),
    ])

# -------------------------------------------------------------------- REORDER
RO1 = dict(
    code="RO-1", journey="Reorder", pos="1 of 6",
    subject="Six weeks in — how's it holding up?",
    preview="Two things to check, and what they tell you.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Six weeks is the point where a system starts telling you how it's going to age. "
                "Two things worth checking this week.",
                "<b>The front perimeter.</b> Hold it to the light and look along the very front "
                "edge. Fine splits there are normal wear, but they spread. Catching one now is a "
                "repair; catching it in a month is a replacement.",
                "<b>The knots at the crown.</b> If hair is shedding faster than it was, that's "
                "usually cleaning technique rather than a fault — too much friction on the base.",
                "Where you are in the cycle: most systems run three to six months. At six weeks "
                "you're roughly a third through, which means now is the time to be maintaining, "
                "not replacing.",
                "Reply with a photo if anything looks off and I'll tell you what I'm seeing."),
            signature="Vincent",
            show_button="yes", button_label="Inspection guide",
            button_url={"href": HS + "/pages/inspection-guide"})),
        ("preference_opt_down", "paper", {}),
    ])

RO3 = dict(
    code="RO-3", journey="Reorder", pos="3 of 6",
    subject="Your replacement window is opening",
    preview="Not urgent yet — but worth knowing the lead time.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Your system is about three months old, which puts you at the start of the "
                "replacement window rather than the end of it.",
                "Nothing to do today. But two things worth knowing:",
                "<b>A replacement takes {{ production_lead_time }} to make.</b> If you order the "
                "day your current one fails, you have a gap with no system. Most people order "
                "their second while the first still has a few weeks left, and rotate between them.",
                "<b>Rotating two systems roughly doubles the life of both.</b> Neither is worn "
                "continuously, adhesive gets a full cure between wears, and the bases last "
                "considerably longer."),
            signature="Vincent",
            show_button="yes", button_label="Order your next system",
            button_url={"href": HS + "/collections/systems"})),
        ("commerce_quote_spec_table", "paper", dict(
            eyebrow="On file", heading="Your saved specification",
            label_1="Specification", value_1="{{ last_order_specification }}",
            label_2="Production lead time", value_2="{{ production_lead_time }}",
            label_3="", value_3="", label_4="", value_4="", label_5="", value_5="",
            note="", button_label="", button_url={"href": "#"})),
        ("preference_opt_down", "paper", {}),
    ])

RO4 = dict(
    code="RO-4", journey="Reorder", pos="4 of 6",
    subject="Same spec, or change something?",
    preview="Now's the moment to adjust density or base type.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "If you're going to order a replacement, this is the useful moment — before you're "
                "forced into it.",
                "The question worth answering: same again, or change something?",
                "Reasons people change:",
                "<b>Density.</b> The most common regret is a first system slightly too dense. If "
                "yours reads a bit young, dropping one grade is the fix.",
                "<b>Base type.</b> If you're replacing more often than you'd like, moving from "
                "full lace to a hybrid buys you weeks.",
                "<b>Hairline.</b> If you've been wearing it a while, you may want it set slightly "
                "differently now that you know how it sits.",
                "Reply with what you'd change and I'll adjust the specification before it goes to "
                "production. That costs nothing."),
            signature="Vincent",
            show_button="no", button_label="", button_url={"href": "#"})),
        ("cta_dual_buttons", "paper", dict(
            eyebrow="", heading="", body_text="",
            primary_label="Same spec", primary_url={"href": HS + "/collections/systems"},
            secondary_label="Change my spec",
            secondary_url={"href": "mailto:vincent@hairsolutions.co"})),
        ("preference_opt_down", "paper", {}),
    ])

RO5 = dict(
    code="RO-5", journey="Reorder", pos="5 of 6",
    subject="Stop thinking about supplies entirely",
    preview="Auto-reorder on your schedule. Cancel any time.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "You've reordered supplies {{ reorder_count }} times now. That's "
                "{{ reorder_count }} occasions you had to notice you were low, and at least one "
                "where you probably cut it fine.",
                "There's a simpler version. Set your interval once and the supplies arrive before "
                "you run out.",
                "— You choose the interval; adjust or skip any delivery<br>— 10% off every order "
                "on a plan<br>— Cancel in one click, no email required",
                "Based on your history, {{ recommended_interval }} weeks looks about right, but "
                "you can change it.",
                "If you'd rather keep ordering manually, that's completely fine — I'll stop "
                "mentioning it after this."),
            signature="Vincent",
            show_button="yes", button_label="Set up auto-reorder",
            button_url={"href": HS + "/pages/auto-reorder"})),
        ("preference_opt_down", "paper", {}),
    ])

RO6 = dict(
    code="RO-6", journey="Reorder", pos="6 of 6",
    subject="A returning-customer price, while it's useful",
    preview="Last reorder note before I leave you alone.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Your system is around {{ months_since_delivery }} months old. Most are near the "
                "end of their usable life by now, so this is the last time I'll raise it.",
                "Because you've bought before, the returning-customer price applies.",
                "If you've moved on from systems altogether, no problem — and if it's because "
                "something didn't work, I'd still like to hear it. That's more useful to me than "
                "the sale."),
            signature="Vincent<br>Founder, Hair Solutions Co.",
            show_button="no", button_label="", button_url={"href": "#"})),
        ("promo_code_block", "coral", dict(
            heading="15% off your next system", promo_code="RETURNING15",
            terms_text="Valid 21 days.",
            button_label="Reorder now", button_url={"href": HS + "/collections/systems"})),
        ("commerce_quote_spec_table", "paper", dict(
            eyebrow="On file", heading="Your saved specification",
            label_1="Specification", value_1="{{ last_order_specification }}",
            label_2="", value_2="", label_3="", value_3="",
            label_4="", value_4="", label_5="", value_5="",
            note="", button_label="Talk it through first",
            button_url={"href": "mailto:vincent@hairsolutions.co"})),
        ("preference_opt_down", "paper", {}),
    ])


# `Product - Dynamic recommendations` is bracketed (recommended) in both blueprints,
# so neither email is hard-blocked. Rather than build another custom mimic of catalog
# data — which Vincent explicitly does not want — the slot renders as a clearly marked
# placeholder to be swapped for the native HubSpot/Shopify product module.
def product_placeholder(surface):
    return ("text_block_generic", surface, dict(
        eyebrow="Product recommendations",
        heading="[ Native product module goes here ]",
        heading_accent="",
        body_text="<p style='margin:0;'>Placeholder. Replace this block with the native "
                  "HubSpot or Shopify product-recommendations module so it pulls real "
                  "catalogue data — price, image, stock and link. Deliberately not built "
                  "as a custom mimic.</p>",
        show_button="no", button_label="", button_url={"href": "#"}))


PP6 = dict(
    code="PP-6", journey="Post-Purchase", pos="6 of 7",
    subject="The four products that actually matter",
    preview="Not a bundle pitch — the short list, and what to skip.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "Three weeks in, most people ask the same question: what do I actually need to "
                "buy, and what's marketing?",
                "The honest short list:",
                "<b>A dedicated adhesive remover.</b> Not acetone, not household solvent. This is "
                "the one product where the cheap option genuinely damages the base.",
                "<b>A sulphate-free shampoo.</b> Sulphates strip the knots and loosen the "
                "ventilation over time.",
                "<b>A soft-bristle looped brush.</b> Standard brushes catch the knots and pull "
                "hair through the base.",
                "<b>A scalp prep wipe.</b> Cheap, and it roughly doubles how long a bond holds.",
                "That's it. You do not need a leave-in, a serum, or a heat protectant unless you "
                "style with heat.",
                "If you already have equivalents that work, keep using them. I'd rather you had a "
                "system that lasts than a bigger order."),
            signature="Vincent",
            show_button="yes", button_label="See the four essentials",
            button_url={"href": HS + "/collections/care"})),
        product_placeholder("paper"),
        ("preference_opt_down", "paper", {}),
    ])

RO2 = dict(
    code="RO-2", journey="Reorder", pos="2 of 6",
    subject="You're about due for supplies",
    preview="Based on when you last ordered, not a guess.",
    blocks=[
        ("header_centered_logo", "paper", {}),
        ("plain_text_founder_wrapper", "paper", dict(
            greeting="Hi {{ firstname }},",
            letter_text=P(
                "You last ordered supplies {{ days_since_supply_order }} days ago.",
                "At a normal reapplication cycle, that's about when adhesive and remover run out. "
                "Not a guess — that's the maths on a two-week bond.",
                "What you'd normally need now:<br>{{ recommended_reorder_items }}",
                "The reason I flag it: running out mid-cycle is when people improvise with the "
                "wrong solvent, and that's the single most common way a good system gets ruined.",
                "If you've changed routine and need something different, reply and tell me what "
                "you're using now."),
            signature="Vincent",
            show_button="yes", button_label="Reorder supplies",
            button_url={"href": HS + "/collections/supplies"})),
        product_placeholder("paper"),
        ("preference_opt_down", "paper", {}),
    ])

EMAILS = [PP1, PP2, PP3, PP4, PP5, PP6, PP7,
          CR1, CR2, CR3, CR4, BR1,
          WB1, WB2, WB3, WB4,
          RO1, RO2, RO3, RO4, RO5, RO6]
