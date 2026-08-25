# -*- coding: utf-8 -*-
"""J2 · Cart Recovery — 4 emails. Copy: Email Reference File/…/CR-*.md (verbatim)."""
from ml_components import *

HI = "Hi {$name},"

def cr1():
    body = (
        p(f"{HI}<br><br>You were partway through an order and stopped. That's completely fine — but occasionally "
          "it's because something on our side didn't work, and I'd want to know.<br><br>"
          "If it was a payment error, a shipping surprise, or the page just froze, reply and tell me. I'll sort it out.<br><br>"
          "If you're still deciding, no rush at all. Your cart's saved.", pad_top=28)
        + p("<span style='font-style:italic;color:#15140F;'>Vincent</span>", pad_top=14)
        + p("Still in your cart:", pad_top=14)
        + cart_placeholder()
        + cta("Finish your order →", "https://hairsolutions.co/cart")
        + footer("preference"))
    return ("CR-1-your-carts-still-here", "Your cart's still here",
            "Your cart's still here",
            "No pressure — just making sure nothing broke on our end.", body)

def cr2():
    body = (
        p(f"{HI}<br><br>Most people who hesitate at checkout are stuck on one of three things. "
          "Here they are, answered straight.", pad_top=28)
        + qa([
            ("“Will it actually look real?”",
             "At conversation distance, a well-fitted lace front is not detectable. The giveaway is never the hair — it's a hairline set too low, or a density too high for your age. We set both conservatively for exactly that reason."),
            ("“Will it hold?”",
             "With clean prep and the right adhesive, a bond holds 7 to 14 days through showering, sweating and sleeping. Prep is the variable, not the product, and we walk you through it."),
            ("“What if it's not right when it arrives?”",
             "Then you email me and we fix it. Colour off, density wrong, base size out — those are on us to resolve, and we do.")])
        + p("Still in your cart:", pad_top=16)
        + cart_placeholder()
        + trust_strip()
        + cta("Finish your order →", "https://hairsolutions.co/cart")
        + p("<span style='font-style:italic;color:#15140F;'>Vincent</span>", pad_top=14)
        + footer("preference"))
    return ("CR-2-three-questions-answered", "The three things people ask before ordering",
            "The three things people ask before ordering",
            "Will it look real, will it hold, and what if it's wrong.", body)

def cr3():
    body = (
        p(f"{HI}<br><br>There's one reason for stalling I haven't covered, and it's the most common: "
          "you're not certain you chose the right system.<br><br>"
          "That's reasonable. Base type, density, hairline, colour — it's a lot of decisions to make from product photos.<br><br>"
          "So here's an easier route. Reply to this email with:", pad_top=28)
        + dashlist([
            "how you currently wear your hair",
            "whether you want daily removal or a longer bond",
            "your rough age bracket"])
        + p("That's enough for me to tell you which base and density I'd actually recommend, and whether what's in your cart is right. "
            "If it isn't, I'll say so, even if the answer is a cheaper unit.<br><br>"
            "Or if you'd rather talk it through properly, book fifteen minutes with me.", pad_top=12)
        + p("<span style='font-style:italic;color:#15140F;'>Vincent</span>", pad_top=14)
        + p("<strong>The two-minute version while you're deciding:</strong> lace is the most natural at the hairline and the least durable. "
            "Poly is the toughest and the easiest to clean and reattach. Hybrid takes the front from one and the back from the other — "
            "which is why most people end up there. Density should sit slightly under what feels safe; "
            "it's the difference between natural and obviously new.", pad_top=14)
        + kv_table([("You were looking at", '<a href="{$last_viewed_product_url}" style="color:#15140F;text-decoration:underline;">{$last_viewed_product}</a>')])
        + p("Nothing expires here. Your cart stays saved, and a spec question before you order costs you nothing — it's what I'm here for.", pad_top=14)
        + trust_strip()
        + cta("Book 15 minutes →", "https://hairsolutions.co/pages/contact-us")
        + footer("preference"))
    return ("CR-3-not-sure-you-picked-right", "Not sure you picked the right one?",
            "Not sure you picked the right one?",
            "Tell me your situation and I'll tell you what I'd choose.", body)

def cr4():
    body = (
        p(f"{HI}<br><br>Last email about this — I won't keep bringing it up.<br><br>"
          "If cost is the sticking point, here's free shipping on the order:", pad_top=28)
        + promo("FREESHIP", "Free shipping on this order", "Valid for 72 hours")
        + cart_placeholder()
        + p("And if the timing just isn't right, that's genuinely fine. Your cart stays saved, the code will be honoured "
            "whenever you come back, and I'll stop emailing you about it.", pad_top=16)
        + signature()
        + cta("Complete your order →", "https://hairsolutions.co/cart")
        + footer("preference"))
    return ("CR-4-last-note-free-shipping", "Last note about your cart",
            "Last note about your cart",
            "Free shipping if it helps. Either way, this is the last one.", body)

CR_EMAILS = [cr1, cr2, cr3, cr4]
