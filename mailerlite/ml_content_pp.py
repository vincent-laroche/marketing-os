# -*- coding: utf-8 -*-
"""J1 · Post-Purchase — 8 emails. Copy: Email Reference File/…/PP-*.md (verbatim)."""
from ml_components import *

HI = "Hi {$name},"

def pp1():
    body = (
        hero("Your order is confirmed, {$name}.")
        + p(f"{HI}<br><br>Your order is in. Thank you — genuinely.<br><br>"
            "Here's what happens now. Your system isn't sitting on a shelf waiting to be boxed; it gets made for you. "
            "That takes time, and I'd rather tell you that up front than have you wondering where it is.")
        + kv_table([("Order number", "{$order_number}"),
                    ("What you ordered", "{$product_summary}"),
                    ("Estimated dispatch", "{$estimated_ship_date}")])
        + numlist([
            "Production starts — the base is cut and the hair is hand-tied to your spec",
            "I email you when it goes into production",
            "I email you when it ships, with tracking",
            "It should be at your door around {$estimated_delivery_date}"])
        + p("No filler emails in between — only the real steps.", pad_top=12)
        + p("If anything about your order looks wrong, reply to this email today and I'll fix it before production starts.")
        + signature()
        + cta("View your order →", "{$order_status_url}")
        + support("Questions about your order? Reply to this email — it comes straight to me.")
        + footer("preference"))
    return ("PP-1-order-confirmation", "Your order is confirmed",
            "Your order is confirmed, {$name}",
            "Here's exactly what happens between now and the day it arrives.", body)

def pp2():
    body = (
        hero("Three small things before it arrives.")
        + p(f"{HI}<br><br>While your system is being made, there are three small things worth doing. "
            "None take long, and they make the first fitting go much better.")
        + numlist([
            "Clear a workspace with a good mirror and decent light. Bathroom mirrors are usually the worst light in the house.",
            "Check what you have. You'll want adhesive or tape, scissors you trust, and rubbing alcohol for prep. "
            "If you're missing something, order it now so it arrives before the system does.",
            "Watch the fitting walkthrough once, before you need it. It's twelve minutes and it will save you an hour of guessing."])
        + p("One more thing: your first fitting will not be your best fitting. That's true for everyone. By the third you'll have it down.", pad_top=12)
        + signature()
        + cta("Read the prep guide →", "https://hairsolutions.co/pages/help-center")
        + support("Missing something from the checklist? Reply and I'll point you to the right product.")
        + footer("preference"))
    return ("PP-2-prep-guide", "Getting ready for your system",
            "Getting ready for your system — a short prep guide",
            "Three things worth doing before it arrives. Ten minutes, total.", body)

def pp3():
    body = (
        p(f"{HI}<br><br>Quick update: your system is in production.<br><br>"
          "What that means in practice — the base is cut to your specification, and the hair is being tied into it by hand, "
          "a few strands at a time. A full unit is somewhere between twenty and thirty thousand knots. "
          "It's slow work, and it's the reason the wait exists.<br><br>"
          "This is also the part that decides whether a hairline looks real or looks like a wig. "
          "There's no way to rush it without it showing.<br><br>"
          "Nothing needed from you. My next email is the dispatch notice with your tracking number.", pad_top=28)
        + signature()
        + photo_slot("This is what the middle of your wait looks like.",
                     "workshop bench — a unit mid-ventilation, natural light, no staging")
        + cta("See how a system is made →", "https://hairsolutions.co/pages/what-we-do")
        + footer("preference"))
    return ("PP-3-on-the-bench", "Your system is on the bench",
            "Your system is on the bench",
            "A look at what's actually happening to it right now.", body)

def pp4():
    body = (
        hero("It's shipped.")
        + p(f"{HI}<br><br>Your system is on its way. When it arrives, do these four things in order:")
        + numlist([
            "Open it over a table, not a sink. The lace is fine and static-prone.",
            "Check the colour against your own hair in daylight, not indoors.",
            "Don't cut anything yet. Try it on untrimmed first.",
            "Take a photo of it as it came, before any modification."])
        + p("That last one matters. If something isn't right, a photo of the unmodified system is what lets me sort it out for you quickly.", pad_top=12)
        + signature()
        + kv_table([("Tracking", "{$tracking_number}"),
                    ("Carrier", "{$carrier}"),
                    ("Expected", "{$estimated_delivery_date}")])
        + cta("Track your order →", "{$tracking_url}")
        + support("Delivery problem or damaged box? Reply with a photo and I'll take it from there.")
        + footer("preference"))
    return ("PP-4-shipped-tracking", "It's shipped — tracking inside",
            "It's shipped — tracking inside",
            "Plus the quick-start steps for the day it lands.", body)

# Care products do NOT exist in the Shopify catalog yet (verified 2026-08-18:
# 44 products, all hair systems). Placeholder slots until catalog ships;
# then swap for MailerLite's dynamic Product block.
CARE_PLACEHOLDERS = [
    {"name": "Adhesive remover",  "price": "Care essential", "url": "https://hairsolutions.co/collections/all", "note": "Product pending"},
    {"name": "Sulphate-free shampoo", "price": "Care essential", "url": "https://hairsolutions.co/collections/all", "note": "Product pending"},
    {"name": "Soft-bristle looped brush", "price": "Care essential", "url": "https://hairsolutions.co/collections/all", "note": "Product pending"},
    {"name": "Scalp prep wipe",   "price": "Care essential", "url": "https://hairsolutions.co/collections/all", "note": "Product pending"},
]

def pp5():
    body = (
        hero("Your 30 / 60 / 90 day maintenance calendar.")
        + p(f"{HI}<br><br>You've had your system about a week. This is the right moment for the maintenance schedule, "
            "because the habits you set now are the ones that stick.")
        + qa([
            ("Every 7–14 days", "Full removal, clean the base, clean your scalp, reapply. Don't stretch this. Adhesive left too long is the single most common cause of base damage."),
            ("Every 30 days", "Deep clean. Solvent soak, gentle brush along the knots, air dry flat. Never wring it."),
            ("Every 60 days", "Inspect the perimeter. Lace goes at the front edge first. Catching a small tear here is a repair; missing it is a replacement."),
            ("Every 90 days", "Assess honestly. Most systems have a usable life of three to six months depending on wear and care. Knowing where you are in that cycle means you're never caught out.")])
        + p("Two things shorten a system's life more than anything else: heat styling directly on the base, and sleeping in it without a wrap. "
            "Neither is forbidden. Both cost you weeks.", pad_top=14)
        + product_grid(CARE_PLACEHOLDERS, title="The care essentials")
        + cta("Save the care schedule →", "https://hairsolutions.co/pages/help-center")
        + support("Reply with any question at all — I answer these myself.")
        + signature()
        + footer("preference"))
    return ("PP-5-maintenance-calendar", "Your 30 / 60 / 90 day maintenance calendar",
            "Your 30 / 60 / 90 day maintenance calendar",
            "What to do, and when, so it lasts as long as it should.", body)

def pp6():
    body = (
        hero("The four products that actually matter.")
        + p(f"{HI}<br><br>Three weeks in, most people ask the same question: what do I actually need to buy, and what's marketing?<br><br>"
            "The honest short list:")
        + qa([
            ("A dedicated adhesive remover", "Not acetone, not household solvent. This is the one product where the cheap option genuinely damages the base."),
            ("A sulphate-free shampoo", "Sulphates strip the knots and loosen the ventilation over time."),
            ("A soft-bristle looped brush", "Standard brushes catch the knots and pull hair through the base."),
            ("A scalp prep wipe", "Cheap, and it roughly doubles how long a bond holds.")])
        + p("That's it. You do not need a leave-in, a serum, or a heat protectant unless you style with heat.<br><br>"
            "If you already have equivalents that work, keep using them. I'd rather you had a system that lasts than a bigger order.", pad_top=14)
        + signature()
        + product_grid(CARE_PLACEHOLDERS, title="The four essentials")
        + cta("See the four essentials →", "https://hairsolutions.co/collections/all")
        + footer("social"))
    return ("PP-6-four-products", "The four products that actually matter",
            "The four products that actually matter",
            "Not a bundle pitch — the short list, and what to skip.", body)


def pp7():
    # NOTE: review-page URL unknown — positive CTA target is a TODO (see BUILD-LEDGER).
    body = (
        p(f"{HI}<br><br>You've had your system about five weeks now — long enough to know how you feel about it.<br><br>"
          "How's it going?<br><br>"
          "If it's going well, the first button takes you to a review page. Reviews are how people in the same position "
          "you were in five weeks ago decide whether to trust us.<br><br>"
          "If it isn't right, the second comes straight to me. Fit, colour, density, adhesion, anything. No form, no ticket queue — "
          "it's my inbox. Most issues at this stage are fixable, and the ones that aren't, I'd still rather know about.", pad_top=28)
        + signature()
        + cta_dual("It's going well →", "https://hairsolutions.co/pages/contact-us",
                   "It's not quite right →", "mailto:info@hairsolutions.co?subject=Not%20quite%20right%20—%20my%20system")
        + footer("standard"))
    return ("PP-7-hows-it-going", "Honestly — how's it going?",
            "Honestly — how's it going?",
            "One question. Good or bad, I want the real answer.", body)

def pp7b():
    body = (
        hero("The photo that convinces the next person.")
        + p("Hi {$name},<br><br>Thanks for the feedback last week — it genuinely helps.<br><br>"
            "One more ask, and this one's bigger: would you be willing to let us show your result?<br><br>"
            "Here's why I'm asking. The single thing that stops people ordering is the fear it will look obvious. "
            "No amount of copy from me fixes that. One photo from someone who was in their position does.")
        + kv_table([("Your order", "{$product_summary}"),
                    ("Ordered", "{$estimated_ship_date}")], title="Your result")
        + photo_slot("A good one is simple: natural daylight, straight on and slightly angled, no filter.",
                     "example of a good customer submission")
        + p("Front hairline is what people want to see. You don't need to show your face — plenty of people don't, and it still works.", pad_top=12)
        # OFFER BLOCK — master says "confirm before send". Omitted until the UGC incentive is confirmed.
        + dashlist([
            "What did you look like before, if you're comfortable sharing?",
            "What convinced you to finally order?",
            "What would you tell someone still deciding?"])
        + p("You control exactly how it's used. Nothing gets published without your written say-so, we'll never use your full name "
            "unless you want us to, and you can ask us to pull it at any point, permanently, no questions.", pad_top=14)
        + cta("Share my photo →", "mailto:info@hairsolutions.co?subject=My%20result%20photo")
        + support("Rather not? Completely fine — reply and I'll take you off this ask.")
        + footer("social"))
    return ("PP-7b-ugc-photo-request", "Would you let us show your result?",
            "Would you let us show your result?",
            "One photo from you does what no copy of mine can.", body)

PP_EMAILS = [pp1, pp2, pp3, pp4, pp5, pp6, pp7, pp7b]

