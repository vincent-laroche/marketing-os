# -*- coding: utf-8 -*-
"""J3 · Win-Back → Sunset — 4 emails. Copy: Email Reference File/…/WB-*.md (verbatim)."""
import json
import os
from ml_components import *

HI = "Hi {$name},"

def _hybrid_products():
    path = os.path.join(os.path.dirname(__file__), "products.json")
    items = json.load(open(path))
    grid = [{"name": p["name"], "price": p["price"], "url": p["url"], "img": p["img"]} for p in items]
    grid.append({"name": "Maintenance plan", "price": "Auto-delivery, your interval",
                 "url": "https://hairsolutions.co/collections/all", "note": "Plan product pending"})
    return grid

def wb1():
    body = (
        p(HI + "<br><br>It's been a while — your last order with us was {$months_since_last_order} months ago.<br><br>"
          "No pitch in this email. I'm just curious how you got on.<br><br>"
          "If you're still wearing a system and it's working, that's good to hear and you can ignore this.<br><br>"
          "If you stopped, I'd honestly like to know why. Was it the maintenance? The cost? Did the fit never come right? "
          "Did you go a different route entirely?<br><br>"
          "I read every reply, and the answers change what we make. The most useful feedback I've had all year "
          "came from people who stopped buying.", pad_top=28)
        + signature()
        # No CTA — reply-only by design (master WB-1 build note).
        + footer("preference"))
    return ("WB-1-checking-in", "Checking in — Vincent here",
            "Checking in — Vincent here",
            "No offer attached. Just wondering how you got on.", body)

def wb2():
    body = (
        hero("Three things that are genuinely different now.")
        + p(f"{HI}<br><br>If it's been a while, a few things are genuinely different now.")
        + qa([
            ("Better hybrid bases",
             "The lace-front-poly-back construction we now stock lasts noticeably longer than the full-lace units most people started on. If yours never lasted long enough to feel worth it, this is the reason why."),
            ("Real tracking, end to end",
             "You can see your unit's status from production through to delivery. The old “it ships when it ships” problem is gone."),
            ("Maintenance plans",
             "If the every-two-weeks routine was what wore you down, supplies can arrive automatically on schedule instead of you remembering.")])
        + p("Still no offer. If one of these solves the thing that stopped you, that's the point.", pad_top=14)
        + signature()
        + photo_slot("The lace-front-poly-back build — the single biggest change since you last ordered.",
                     "current hybrid base construction, up close — lace front seam visible")
        + product_grid(_hybrid_products(), title="Current hybrid systems")
        + cta("See what's changed →", "https://hairsolutions.co/collections/hybrid-hair-systems")
        + footer("social"))
    return ("WB-2-whats-changed", "What's changed since you last ordered",
            "What's changed since you last ordered",
            "Three things, briefly. Some of them fix the reasons people leave.", body)

def wb3():
    body = (
        hero("20% off, if you want to try again.")
        + p(f"{HI}<br><br>Now the offer, since I said I'd get to it.<br><br>"
            "20% off your next system. If you want the same again, it's about a minute. If you'd rather change base type "
            "or density based on how the last one went, reply and tell me what didn't work — "
            "I'll adjust the spec myself before it goes to production.")
        + signature()
        + promo("WELCOMEBACK20", "20% off your next system", "Valid 14 days")
        + kv_table([("Saved spec", "{$last_order_specification}")], title="Your last specification, still on file")
        + cta("Reorder with 20% off →", "https://hairsolutions.co/collections/all")
        + footer("preference"))
    return ("WB-3-20-welcome-back", "20% off, if you want to try again",
            "20% off, if you want to try again",
            "Your previous specification is saved — reordering takes a minute.", body)

def wb4():
    body = (
        p(f"{HI}<br><br>This is the last marketing email you'll get from us.<br><br>"
          "You haven't opened anything in a while, and I'd rather stop than keep arriving in an inbox where I'm not wanted. "
          "In a week I'll quietly remove you from our marketing list. You don't need to do anything.<br><br>"
          "If you'd like to stay, one click keeps you on.<br><br>"
          "Either way, your account and order history stay intact, and you can buy from the site any time without being on a list. "
          "If you ever need help with a system — even one you didn't buy from us — my inbox is open. That doesn't expire.<br><br>"
          "Thanks for having given us a go.", pad_top=28)
        + signature()
        + cta("Keep me on the list →", "https://hairsolutions.co/?stay=subscribed")
        + footer("preference"))
    return ("WB-4-last-email-from-us", "Last email from us",
            "Last email from us",
            "We'll stop here unless you tell us otherwise.", body)

WB_EMAILS = [wb1, wb2, wb3, wb4]
