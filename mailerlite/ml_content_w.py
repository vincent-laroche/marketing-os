# -*- coding: utf-8 -*-
"""W · Newsletter Welcome — 5 emails. Copy: Email Reference File/…/W-*.md (verbatim).

Prospect-facing lead nurture. Carries NO order/customer tokens — this audience has
never purchased. Only {$name} plus {$unsubscribe}/{$url} in the footer.

Blocks omitted where their source data does not exist, following the same convention
already applied across the 22 lifecycle emails:
  - every [Testimonial] / [Quote] / [Stat bars] / [Review stars] -> Proof Bank is empty
  - W-1 offer + promo modules -> master says drop both unless an incentive was promised
    at signup; none was
  - W-1 FAQ -> the master names the three questions but supplies no answers
"""
import json
import os
from ml_components import *

HI = "Hi {$name},"

# CTA destinations use the URL vocabulary already established by the 22 built emails.
URL_BASICS  = "https://hairsolutions.co/pages/what-we-do"
URL_GUIDE   = "https://hairsolutions.co/pages/help-center"      # TODO: dedicated base-types page
URL_STYLES  = "https://hairsolutions.co/collections/all"        # TODO: dedicated style gallery
URL_REVIEWS = "https://hairsolutions.co/pages/what-we-do"       # TODO: review page URL
URL_CONSULT = "https://hairsolutions.co/pages/contact-us"


def _systems():
    """The three real Shopify systems that carry the styles in W-3 / W-5."""
    path = os.path.join(os.path.dirname(__file__), "products.json")
    return [{"name": p["name"], "price": p["price"], "url": p["url"], "img": p["img"]}
            for p in json.load(open(path))]


def w1():
    body = (
        masthead()
        + p(f"{HI}<br><br>Welcome to the Hair Solutions list. Before anything else, here's the deal — "
            "what you'll get from us, and what you never will.", pad_top=20)
        + p("<strong style=\"color:#15140F;\">What you'll get:</strong>", pad_top=18)
        + dashlist([
            "Practical content about hair systems — how they work, what they cost, how to maintain them",
            "Real customer stories — actual experiences, not stock-photo marketing",
            "Product and material updates when we launch something worth knowing about"])
        + p("<strong style=\"color:#15140F;\">What you'll never get:</strong>", pad_top=18)
        + dashlist([
            "Pressure to buy before you're ready",
            "Medical claims or miracle promises",
            "Spam — we email 2–4 times a month, maximum"])
        + p("If you ever have a question — even a basic one — reply to any email and I'll answer it personally.",
            pad_top=18)
        # [Text - Offer discount] + [Signal - Promo code] omitted: master drops both when no
        # incentive was promised at signup. [FAQ] omitted: no answers exist in the master.
        + cta("Start with the basics →", URL_BASICS)
        + footer("social"))
    return ("W-1-welcome-expectations", "You're in — here's what to expect",
            "You're in — here's what to expect",
            "What you'll get, what you'll never get, and how often.", body)


def w2():
    body = (
        hero("The 3-minute version of how this actually works.")
        + p(f"{HI}<br><br>If you've been curious about hair systems but never quite understood them, "
            "here's the simple version — no jargon, no sales angle. There are only four parts that matter: "
            "the base, the hair, the attachment, and the routine. Everything else is detail.")
        + p("I explain this to someone new nearly every day. The base is the biggest decision — it determines "
            "how natural the system looks, how breathable it feels, and how long it lasts. Get that right and "
            "the rest follows.<br>"
            '<span style="font-style:italic;color:#15140F;">— Vincent</span>', pad_top=18)
        + qa([
            ("Lace", "Most natural at the hairline, most breathable, shortest life."),
            ("Poly (skin)", "Most durable, easiest to clean and reattach, slightly less invisible up close."),
            ("Hybrid", "Lace front for the hairline, poly at the sides and back. Most people end up here.")])
        + numlist([
            "The hair — hand-tied into the base, matched to your colour, density and length. The goal is "
            "proportional and natural for your age, not \"too perfect\"",
            "The attachment — tape or adhesive; properly done, it holds through workouts, swimming, wind and sleep",
            "Daily — wash and style like natural hair (5 minutes)",
            "Every 2–4 weeks — remove, clean scalp and base, reattach (30–45 minutes)",
            "Every 3–6 months — replace the system"])
        + p("No surgery, no chemicals, no downtime.", pad_top=16)
        + cta("Explore base types →", URL_GUIDE)
        + footer("social"))
    return ("W-2-how-systems-work", "How a hair system actually works (the 3-minute version)",
            "How a hair system actually works (the 3-minute version)",
            "Base, hair, attachment, routine — no jargon, no sales angle.", body)


def w3():
    body = (
        masthead()
        + photo_slot("One of the best things about a system: you style it exactly how you want.",
                     "customer style shot — textured crop, natural daylight, no staging")
        + p("Five looks our customers are wearing right now:", pad_top=20)
        + numlist([
            "The textured crop — short sides, textured top. 80% density with slight wave. Low maintenance.",
            "The classic slick-back — straight hair, 100% density, 6\"+ length. Clean and professional.",
            "The natural curl — body wave or curly, 80–100% density. Very natural movement.",
            "The fade blend — system hair blended into a skin fade. Needs a barber who can cut in a system "
            "(we can help you find one).",
            "The grey blend — 10–30% grey mixed into the base colour. Adds realism for men 35+."])
        + p("The rule behind all five: density matched to age. A 25-year-old can pull off 100% density; "
            "a 45-year-old looks more natural at 70–80%. It's one of the most important decisions we help "
            "with during spec building.", pad_top=18)
        + product_grid(_systems(), title="Systems that carry these styles")
        # [Testimonial] omitted — Proof Bank empty.
        + cta("See the style gallery →", URL_STYLES)
        + footer("social"))
    return ("W-3-style-inspiration", "5 styles our customers are wearing right now",
            "5 styles our customers are wearing right now",
            "Real wearers, real cuts — and the density rule that makes them work.", body)


def w4():
    body = (
        hero("What customers say once they've lived with it.")
        + p(f"{HI}<br><br>I can tell you a system looks natural. It lands differently coming from the people "
            "wearing one. Everything below is real, consented, and unedited — that's a hard rule here.")
        # [Testimonial] [Quote - Accent bar] [Stat bars] [Review stars] ALL omitted — Proof Bank
        # is empty and the review-stars module hardcodes five stars regardless of rating.
        # This email is a shell until real proof copy exists. See BUILD-LEDGER.
        # [Text - Offer discount: reminder] omitted — W-1 carried no incentive.
        + cta("Read the reviews →", URL_REVIEWS)
        + footer("social"))
    return ("W-4-social-proof-wall", "Don't take my word for it",
            "Don't take my word for it",
            "What customers say after the first month — unedited.", body)


def w5():
    body = (
        masthead()
        + p(f"{HI}<br><br>Over the past few weeks you've had a decent picture of how systems work — the bases, "
            "the styles, the maintenance. If you're still in research mode, that's completely fine. Take your "
            "time; you'll keep getting our best content either way.<br><br>"
            "If you're starting to feel ready, here's exactly how it works.", pad_top=20)
        + numlist([
            "We talk — email, WhatsApp or phone, whatever you prefer. Most first consultations take 10–15 minutes",
            "I recommend one system — not a catalogue of options, one specific recommendation tailored to you",
            "You decide — no pressure, no time limits. If the quote makes sense, we build it. If not, no hard feelings"])
        + product_grid(_systems(), title="Where most people start")
        + p("Worth thinking about before a call:", pad_top=20)
        + dashlist([
            "How you currently wear your hair",
            "Whether you want daily removal or a longer bond",
            "Which matters more — the most natural hairline, or the least maintenance"])
        # [Testimonial] omitted — Proof Bank empty.
        + p("Every consultation is with me, not a sales team. If a system isn't right for your situation, "
            "I'll tell you that too.<br>"
            '<span style="font-style:italic;color:#15140F;">— Vincent</span>', pad_top=18)
        + cta("Start a consultation →", URL_CONSULT)
        + footer("social"))
    return ("W-5-soft-consult-invite", "Whenever you're ready",
            "Whenever you're ready",
            "How the process works when you are — and no pressure while you're not.", body)


W_EMAILS = [w1, w2, w3, w4, w5]
