# Journey · Cart Recovery · Master

## Spec

| Field | Value |
| --- | --- |
| **Object** | Contact |
| **Trigger** | order_cart_abandon_count > 0 — **verify Shopify writes it first** |
| **Branch** | Reached checkout → CR-1…4 · Browsed only, no cart → BR-1 alone |
| **Re-enrolment** | On, with a **7-day cooloff** |
| **Hard exit** | Order placed → exit immediately, hand to Post-Purchase Master |
| **Subscription** | Move off News & Offers → **Order & Shipping Updates** |

---

## Before — The Collision (5 workflows + stock template → 9 slots → 4 archived)

**The core problem:** Site, Browse, Cart and Checkout are four names for one funnel, and as defined they are not mutually exclusive. A person who browses, adds to cart, then drops at payment satisfies all four conditions and would enrol in all four flows.

**The live flow cannot fire** because its trigger property (order_cart_abandon_count) is never written by Shopify.

**The four finished Checkout Abandonment emails are wired to nothing at all** — the best-written cart copy in the portal is currently unreachable.

| Workflow | State | Emails | Problem |
| --- | --- | --- | --- |
| Abandoned Cart — Current | On | 3 · all **Draft** | Only live cart flow. Trigger never fires — property not written. Points at three unpublished drafts. |
| Abandoned Cart — Legacy | Off | 4 · all **Archived** | All four carry the *identical subject line*. Delete the workflow. |
| Abandoned Cart | Off | 0 | Empty shell, zero actions. |
| Checkout Abandonment | Off | 0 | Empty shell — but 4 finished emails exist and are attached to nothing. |
| Site Abandonment | Off | 0 | Empty shell, zero actions. |
| Browse Abandonment | Off | 2 · both **Draft** | Named "1 of 4" and "2 of 4" — the other two were never built. |
| Send abandoned cart emails | Off | Stock | HubSpot template on the CART object. Delete. |

---

## Replacement — 5 Emails

### CR-1 · Abandon + 4 hours · Order & Shipping Updates

**Subject:** Your cart's still here

**Preview:** No pressure — just making sure nothing broke on our end.

**Keep record:** Abandoned Cart 1of3 (214989746959) — *must be published; currently a draft.*

**Timing change:** +4h instead of +0d — an immediate send reads as surveillance.

---

### CR-2 · Abandon + 1 day · Order & Shipping Updates

**Subject:** The three things people ask before ordering

**Preview:** Will it look real, will it hold, and what if it's wrong.

**Replaces:** Abandoned Cart 2of3 (214987971489) + Checkout Abandonment 2of4 (Trust + Social Proof).

**Why rewritten:** the original was a generic trust-badge list. Naming the actual objections is what moves a considered, high-price purchase.

---

### CR-3 · Abandon + 2 days · Order & Shipping Updates

**Subject:** Not sure you picked the right one?

**Preview:** Tell me your situation and I'll tell you what I'd choose.

**New email — no existing record.**

**Gap filled:** the old ladder jumped from social proof straight to a discount. For a considered purchase, uncertainty is a bigger blocker than price. Only cart email that can generate a consultation booking.

---

### CR-4 · Abandon + 4 days · Order & Shipping Updates

**Subject:** Last note about your cart

**Preview:** Free shipping if it helps. Either way, this is the last one.

**Keep record:** Abandoned Cart 3of3 (214987971492) — *publish it.*

**Deliberate choice:** free shipping (FREESHIP) rather than 10% off. A percentage discount on a considered purchase trains people to wait for the next one; shipping does not devalue the product.

---

### BR-1 · Browse + 1 day · branch, no cart · Order & Shipping Updates

**Subject:** Still weighing up base types?

**Preview:** Lace, poly, or hybrid — the two-minute version.

**Replaces:** Browse Abandonment 1of4 and 2of4 (both drafts) — collapsed into one email.

**Rule:** browse-only gets a single educational touch, never a four-part ladder. Anyone who adds to cart exits here and enters CR-1.