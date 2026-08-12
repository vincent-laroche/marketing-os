import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tonal_plan import surface_for

PP3 = {"code": "PP-3", "journey": "J1 · Post-Purchase · Master"}
PP4 = {"code": "PP-4", "journey": "J1 · Post-Purchase · Master"}
WB2 = {"code": "WB-2", "journey": "J3 · Win-Back → Sunset"}
C1 = {"code": "C-1", "journey": "J5 · Consultation · Master"}


def test_journey_registers():
    assert surface_for(PP4, 1, "Text - Opening") == "paper"
    assert surface_for(WB2, 1, "Text - Opening") == "ink"
    assert surface_for(C1, 1, "Text - Opening") == "paper"


def test_pp3_is_the_ink_exception():
    assert surface_for(PP3, 1, "Layout - Plain-text founder wrapper") == "ink"


def test_named_coral_moment_only():
    assert surface_for(PP4, 3, "Commerce - Shipping tracking") == "coral"
    assert surface_for(WB2, 3, "Commerce - Shipping tracking") == "ink"
    # a promo block outside its named email is NOT coral
    assert surface_for(PP4, 3, "Signal - Promo code") != "coral"


def test_chrome_never_coral():
    assert surface_for(PP4, 0, "Header - Centered logo") != "coral"
    assert surface_for(PP4, 9, "Footer - Preference centre") != "coral"
