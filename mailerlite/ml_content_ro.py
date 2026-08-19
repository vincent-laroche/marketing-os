# -*- coding: utf-8 -*-
"""J4 · Reorder — 6 emails. Copy: Email Reference File/…/RO-*.md (verbatim)."""
from ml_components import *

HI = "Hi {$name},"

def ro1():
    body = (
        p(f"{HI}<br><br>Six weeks is the point where a system starts telling you how it's going to age. "
          "Two things worth checking this week.", pad_top=28)
        + qa([
            ("The front perimeter",
             "Hold it to the light and look along the very front edge. Fine splits there are normal wear, but they spread. Catching one now is a repair; catching it in a month is a replacement."),
            ("The knots at the crown",
             "If hair is shedding faster than it was, that's usually cleaning technique rather than a fault — too much friction on the base.")])
        + p("Where you are in the cycle: most systems run three to six months. At six weeks you're roughly a third through, "
            "which means now is the time to be maintaining, not replacing.<br><br>"
            "Reply with a photo if anything looks off and I'll tell you what I'm seeing.", pad_top=14)
        + signature()
        + cta("Inspection guide →", "https://hairsolutions.co/pages/help-center")
        + footer("preference"))
    return ("RO-1-six-weeks-in", "Six weeks in — how's it holding up?",
            "Six weeks in — how's it holding up?",
            "Two things to check, and what they tell you.", body)

def ro2():
    body = (
        hero("You're about due for supplies.")
        + p(HI + "<br><br>You last ordered supplies {$days_since_supply_order} days ago.<br><br>"
            "At a normal reapplication cycle, that's about when adhesive and remover run out. Not a guess — "
            "that's the maths on a two-week bond.<br><br>"
            "The reason I flag it: running out mid-cycle is when people improvise with the wrong solvent, "
            "and that's the single most common way a good system gets ruined.")
        + kv_table([("What you'd normally need", "{$recommended_reorder_items}")])
        + p("If you've changed routine and need something different, reply and tell me what you're using now — "
            "I'll adjust the list rather than send you the default.", pad_top=14)
        + signature()
        + cta("Reorder supplies →", "https://hairsolutions.co/collections/all")
        + footer("preference"))
    return ("RO-2-due-for-supplies", "You're about due for supplies",
            "You're about due for supplies",
            "Based on when you last ordered, not a guess.", body)

def ro3():
    body = (
        hero("Your replacement window is opening.")
        + p(HI + "<br><br>Your system is about three months old, which puts you at the start of the replacement window "
            "rather than the end of it.<br><br>"
            "Nothing to do today. But two things worth knowing:<br><br>"
            "A replacement takes {$production_lead_time} to make. If you order the day your current one fails, you have a gap "
            "with no system. Most people order their second while the first still has a few weeks left, and rotate between them.<br><br>"
            "Rotating two systems roughly doubles the life of both. Neither is worn continuously, adhesive gets a full cure "
            "between wears, and the bases last considerably longer.")
        + signature()
        + kv_table([("Saved spec", "{$last_order_specification}")], title="Your saved specification")
        + cta("Order your next system →", "https://hairsolutions.co/collections/custom-hair-systems")
        + footer("preference"))
    return ("RO-3-replacement-window", "Your replacement window is opening",
            "Your replacement window is opening",
            "Not urgent yet — but worth knowing the lead time.", body)

def ro4():
    body = (
        p(f"{HI}<br><br>If you're going to order a replacement, this is the useful moment — before you're forced into it.<br><br>"
          "The question worth answering: same again, or change something?<br><br>"
          "Reasons people change:", pad_top=28)
        + qa([
            ("Density", "The most common regret is a first system slightly too dense. If yours reads a bit young, dropping one grade is the fix."),
            ("Base type", "If you're replacing more often than you'd like, moving from full lace to a hybrid buys you weeks."),
            ("Hairline", "If you've been wearing it a while, you may want it set slightly differently now that you know how it sits.")])
        + p("Reply with what you'd change and I'll adjust the specification before it goes to production. That costs nothing.", pad_top=14)
        + signature()
        + cta_dual("Same spec →", "https://hairsolutions.co/collections/custom-hair-systems",
                   "Change my spec →", "mailto:info@hairsolutions.co?subject=Change%20my%20spec")
        + footer("preference"))
    return ("RO-4-same-spec-or-change", "Same spec, or change something?",
            "Same spec, or change something?",
            "Now's the moment to adjust density or base type.", body)

def ro5():
    body = (
        hero("Stop thinking about supplies entirely.")
        + p(HI + "<br><br>You've reordered supplies {$reorder_count} times now. That's {$reorder_count} occasions you had to "
            "notice you were low, and at least one where you probably cut it fine.<br><br>"
            "There's a simpler version. Set your interval once and the supplies arrive before you run out.")
        + dashlist([
            "You choose the interval; adjust or skip any delivery",
            "10% off every order on a plan",
            "Cancel in one click, no email required"])
        + p("Based on your history, {$recommended_interval} weeks looks about right, but you can change it.<br><br>"
            "If you'd rather keep ordering manually, that's completely fine — I'll stop mentioning it after this.", pad_top=14)
        + signature()
        + cta("Set up auto-reorder →", "https://hairsolutions.co/collections/all")
        + footer("preference"))
    return ("RO-5-auto-reorder", "Stop thinking about supplies entirely",
            "Stop thinking about supplies entirely",
            "Auto-reorder on your schedule. Cancel any time.", body)

def ro6():
    body = (
        hero("A returning-customer price, while it's still useful.")
        + p(HI + "<br><br>Your system is around {$months_since_delivery} months old. Most are near the end of their usable life "
            "by now, so this is the last time I'll raise it.<br><br>"
            "Because you've bought before, the returning-customer price applies.")
        + promo("RETURNING15", "15% off your next system", "Valid 21 days")
        + kv_table([("Saved spec", "{$last_order_specification}")], title="Your saved specification")
        + p("If you've moved on from systems altogether, no problem — and if it's because something didn't work, "
            "I'd still like to hear it. That's more useful to me than the sale.", pad_top=14)
        + signature()
        + cta_dual("Reorder now →", "https://hairsolutions.co/collections/custom-hair-systems",
                   "Talk it through first →", "mailto:info@hairsolutions.co?subject=Talk%20it%20through")
        + footer("preference"))
    return ("RO-6-returning-customer-price", "A returning-customer price, while it's useful",
            "A returning-customer price, while it's useful",
            "Last reorder note before I leave you alone.", body)

RO_EMAILS = [ro1, ro2, ro3, ro4, ro5, ro6]

