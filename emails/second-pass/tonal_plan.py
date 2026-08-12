"""Per-journey surface assignment. Paper / Ink / Coral only — see Global Constraints."""

REGISTER = {
    "J1 · Post-Purchase · Master": "paper",
    "J2 · Cart Recovery · Master": "paper",
    "J3 · Win-Back → Sunset":      "ink",
    "J4 · Reorder · Master":       "paper",
    "J5 · Consultation · Master":  "paper",
}

# emails that break their journey's register
EXCEPTIONS = {"PP-3": "ink", "CR-4": "ink"}

# exactly one coral block per journey, at a named email + module
CORAL_MOMENT = {
    "PP-4": "Commerce - Shipping tracking",
    "CR-4": "Signal - Promo code",
    "WB-3": "Signal - Promo code",
    "RO-6": "Signal - Promo code",
    "C-3":  "Signal - Promo code",
}

CHROME = {"Header - Centered logo", "Header", "Footer - Preference centre",
          "Footer - Standard", "Footer - Social", "Footer - Wide"}


def surface_for(email, index, family):
    code = email["code"]
    if family not in CHROME and CORAL_MOMENT.get(code) == family:
        return "coral"
    return EXCEPTIONS.get(code) or REGISTER.get(email["journey"], "paper")
