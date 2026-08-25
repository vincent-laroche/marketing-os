export const templates = [
  {
    id: "hero-brand-post",
    title: "Hero brand post",
    category: "feed",
    frames: [
      {
        format: "square",
        tone: "paper",
        markup: `
          <span class="folio">01</span>
          <div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div>
          <div class="hero-copy">
            <p class="eyebrow">Brand or founder thesis</p>
            <h1>[One clear brand idea]<span class="terminal">.</span></h1>
            <p class="lede">One short supporting line. Keep the graphic and caption complementary.</p>
          </div>
          <p class="micro-footer">HAIR SOLUTIONS CO. · REVIEW TEMPLATE</p>`
      }
    ]
  },
  {
    id: "single-product-post",
    title: "Single product post",
    category: "feed",
    frames: [
      {
        format: "portrait",
        tone: "canvas",
        markup: `
          <div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div>
          <div class="product-grid">
            <div class="media-hold"><strong>Approved product photograph</strong><span>Preserve construction, color, density, and scale</span></div>
            <div class="product-copy">
              <p class="eyebrow">Verified product study</p>
              <h1>[Product name]<span class="terminal">.</span></h1>
              <p class="lede">[One verified material detail and the practical tradeoff it changes.]</p>
              <span class="action-pill">[One next step]</span>
            </div>
          </div>`
      }
    ]
  },
  {
    id: "collection-post",
    title: "Collection post",
    category: "feed",
    frames: [
      {
        format: "square",
        tone: "ink",
        markup: `
          <div class="brand-mark light" role="img" aria-label="Hair Solutions Co."></div>
          <div class="collection-copy">
            <p class="eyebrow coral">Verified category</p>
            <h1>Choose by routine<span class="terminal">.</span></h1>
            <p class="lede">One category, three useful distinctions.</p>
          </div>
          <div class="plate-row">
            <div class="plate"><span>Approved plate 01</span></div>
            <div class="plate"><span>Approved plate 02</span></div>
            <div class="plate"><span>Approved plate 03</span></div>
          </div>`
      }
    ]
  },
  {
    id: "quote-testimonial-post",
    title: "Quote or testimonial post",
    category: "feed",
    frames: [
      {
        format: "square",
        tone: "raised",
        blocked: true,
        markup: `
          <div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div>
          <div class="quote-copy">
            <span class="coral-rule"></span>
            <h1>[Approved customer quote]<span class="terminal">.</span></h1>
            <p class="lede">Exact quote, exact channel consent, and source record required.</p>
          </div>
          <p class="proof-label">PRODUCTION HOLD · DO NOT INVENT PROOF</p>`
      }
    ]
  },
  {
    id: "blog-article-post",
    title: "Blog or article post",
    category: "feed",
    frames: [
      {
        format: "square",
        tone: "paper",
        markup: `
          <span class="folio">GUIDE · 01</span>
          <div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div>
          <div class="editorial-copy">
            <p class="eyebrow">Education</p>
            <h1>[Useful guide headline]<span class="terminal">.</span></h1>
            <p class="lede">Name the decision or tradeoff. Keep supporting facts in the caption or carousel.</p>
          </div>
          <span class="secondary-pill">Read the guide</span>`
      }
    ]
  },
  {
    id: "sale-promo-post",
    title: "Sale or promotion post",
    category: "feed",
    frames: [
      {
        format: "square",
        tone: "ink",
        blocked: true,
        markup: `
          <div class="brand-mark light" role="img" aria-label="Hair Solutions Co."></div>
          <div class="offer-copy">
            <p class="eyebrow coral">Verified offer only</p>
            <h1>[Offer]<span class="terminal">.</span></h1>
            <p class="lede">[Verified scope, dates, exclusions, and owner.]</p>
            <span class="action-pill">[One next step]</span>
          </div>
          <p class="proof-label light-text">PRODUCTION HOLD · LIVE OFFER CHECK REQUIRED</p>`
      }
    ]
  },
  {
    id: "announcement-post",
    title: "Announcement post",
    category: "feed",
    frames: [
      {
        format: "square",
        tone: "paper",
        blocked: true,
        markup: `
          <span class="folio">NOTICE · VERIFIED BEFORE USE</span>
          <div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div>
          <div class="announcement-copy">
            <p class="eyebrow">Announcement</p>
            <h1>[What changed]<span class="terminal">.</span></h1>
            <p class="lede">[Who it affects, when it applies, and one clear next step.]</p>
          </div>`
      }
    ]
  },
  {
    id: "story-product",
    title: "Product Story",
    category: "stories",
    frames: [
      {
        format: "story",
        tone: "canvas",
        markup: `
          <div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div>
          <div class="story-stack">
            <div class="media-hold story-media"><strong>Approved product media</strong><span>9:16 source or deliberate crop</span></div>
            <div>
              <p class="eyebrow">Verified product</p>
              <h1>[Product name]<span class="terminal">.</span></h1>
              <p class="lede">[One verified material detail.]</p>
            </div>
            <span class="action-pill">[Link sticker label]</span>
          </div>`
      }
    ]
  },
  {
    id: "story-quote",
    title: "Quote Story",
    category: "stories",
    frames: [
      {
        format: "story",
        tone: "ink",
        blocked: true,
        markup: `
          <div class="brand-mark light" role="img" aria-label="Hair Solutions Co."></div>
          <div class="story-center">
            <span class="coral-rule"></span>
            <h1>[Approved customer quote]<span class="terminal">.</span></h1>
            <p class="lede">Exact channel consent and source record required.</p>
          </div>
          <p class="proof-label light-text">PRODUCTION HOLD · DO NOT INVENT PROOF</p>`
      }
    ]
  },
  {
    id: "story-sale",
    title: "Promotion Story",
    category: "stories",
    frames: [
      {
        format: "story",
        tone: "paper",
        blocked: true,
        markup: `
          <div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div>
          <div class="story-center">
            <p class="eyebrow">Verified offer only</p>
            <h1>[Offer]<span class="terminal">.</span></h1>
            <p class="lede">[Verified dates, scope, and exclusions.]</p>
            <span class="action-pill">[Link sticker label]</span>
          </div>
          <p class="proof-label">PRODUCTION HOLD · LIVE OFFER CHECK REQUIRED</p>`
      }
    ]
  },
  {
    id: "how-it-works",
    title: "How it works carousel",
    category: "carousels",
    frames: [
      { format: "square", tone: "paper", markup: `<span class="folio">01 / 05</span><div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div><div class="hero-copy"><p class="eyebrow">Useful guide</p><h1>[How it works]<span class="terminal">.</span></h1><p class="lede">The first slide must work on its own.</p></div>` },
      { format: "square", tone: "wash", markup: `<span class="sequence">01</span><div class="step-copy"><p class="eyebrow">Verified step</p><h1>[Step one]<span class="terminal">.</span></h1><p class="lede">One practical decision or action.</p></div>` },
      { format: "square", tone: "wash", markup: `<span class="sequence">02</span><div class="step-copy"><p class="eyebrow">Verified step</p><h1>[Step two]<span class="terminal">.</span></h1><p class="lede">One practical decision or action.</p></div>` },
      { format: "square", tone: "wash", markup: `<span class="sequence">03</span><div class="step-copy"><p class="eyebrow">Verified step</p><h1>[Step three]<span class="terminal">.</span></h1><p class="lede">One practical decision or action.</p></div>` },
      { format: "square", tone: "paper", markup: `<span class="folio">05 / 05</span><div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div><div class="hero-copy"><p class="eyebrow">Next step</p><h1>[One clear action]<span class="terminal">.</span></h1><span class="action-pill">[CTA]</span></div>` }
    ]
  },
  {
    id: "before-after",
    title: "Before and after carousel",
    category: "carousels",
    frames: [
      { format: "square", tone: "paper", blocked: true, markup: `<span class="folio">01 / 03 · BEFORE</span><div class="media-hold full-media"><strong>Consented before image</strong><span>Match crop, light, scale, and grade</span></div><p class="proof-label">EXACT-USE CONSENT REQUIRED</p>` },
      { format: "square", tone: "ink", blocked: true, markup: `<span class="folio light-text">02 / 03 · PROCESS</span><div class="step-copy"><p class="eyebrow coral">Verified process</p><h1>[What changed]<span class="terminal">.</span></h1><p class="lede">State the relevant choices and tradeoffs without a universal outcome claim.</p></div>` },
      { format: "square", tone: "paper", blocked: true, markup: `<span class="folio">03 / 03 · AFTER</span><div class="media-hold full-media"><strong>Consented after image</strong><span>Preserve truthful result and matched conditions</span></div><p class="proof-label">EXACT-USE CONSENT REQUIRED</p>` }
    ]
  },
  {
    id: "drop-reveal",
    title: "Drop reveal carousel",
    category: "carousels",
    frames: [
      { format: "square", tone: "paper", blocked: true, markup: `<span class="folio">01 / 04</span><div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div><div class="hero-copy"><p class="eyebrow">Verified release</p><h1>[A useful tease]<span class="terminal">.</span></h1><p class="lede">Do not imply scarcity unless it is verified.</p></div>` },
      { format: "square", tone: "wash", blocked: true, markup: `<span class="sequence">01</span><div class="step-copy"><p class="eyebrow">Verified detail</p><h1>[Detail one]<span class="terminal">.</span></h1></div>` },
      { format: "square", tone: "wash", blocked: true, markup: `<span class="sequence">02</span><div class="step-copy"><p class="eyebrow">Verified detail</p><h1>[Detail two]<span class="terminal">.</span></h1></div>` },
      { format: "square", tone: "paper", blocked: true, markup: `<span class="folio">04 / 04</span><div class="media-hold full-media"><strong>Approved release media</strong><span>Product identity and availability verified</span></div><span class="action-pill">[One next step]</span>` }
    ]
  },
  {
    id: "testimonial-set",
    title: "Testimonial set carousel",
    category: "carousels",
    frames: [1, 2, 3].map((number) => ({
      format: "square",
      tone: number === 2 ? "wash" : "raised",
      blocked: true,
      markup: `<span class="folio">0${number} / 03</span><div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div><div class="quote-copy"><span class="coral-rule"></span><h1>[Approved quote ${number}]<span class="terminal">.</span></h1><p class="lede">Exact quote and exact-use consent required.</p></div><p class="proof-label">PRODUCTION HOLD · SOURCE REQUIRED</p>`
    }))
  },
  {
    id: "reel-cover",
    title: "Reel cover",
    category: "reels",
    frames: [
      {
        format: "portrait",
        tone: "paper",
        markup: `
          <div class="brand-mark" role="img" aria-label="Hair Solutions Co."></div>
          <div class="reel-cover-copy">
            <p class="eyebrow">Reel cover · feed-safe crop</p>
            <h1>[Useful hook]<span class="terminal">.</span></h1>
            <p class="lede">Readable at 320px wide. Keep the promise accurate.</p>
          </div>
          <p class="micro-footer">1080 × 1350 COVER · PAIR WITH 1080 × 1920 VIDEO</p>`
      }
    ]
  },
  {
    id: "reel-storyboard",
    title: "Reel storyboard",
    category: "reels",
    frames: [
      { format: "story", tone: "paper", markup: `<span class="folio">BEAT 01 · HOOK</span><div class="story-center"><h1>[Useful opening line]<span class="terminal">.</span></h1><p class="lede">No clickbait. Captions burned in.</p></div>` },
      { format: "story", tone: "canvas", blocked: true, markup: `<span class="folio">BEAT 02 · EVIDENCE</span><div class="media-hold story-media"><strong>Approved source footage</strong><span>Show the material or action that supports the hook</span></div>` },
      { format: "story", tone: "wash", markup: `<span class="folio">BEAT 03 · EXPLAIN</span><div class="story-center"><h1>[One practical detail]<span class="terminal">.</span></h1><p class="lede">Keep the sentence short enough to read while muted.</p></div>` },
      { format: "story", tone: "ink", markup: `<span class="folio light-text">BEAT 04 · TRADEOFF</span><div class="story-center"><h1>[What changes the choice]<span class="terminal">.</span></h1><p class="lede">Clarity is more credible than certainty.</p></div>` },
      { format: "story", tone: "paper", markup: `<span class="folio">BEAT 05 · NEXT STEP</span><div class="story-center"><h1>[One clear action]<span class="terminal">.</span></h1><span class="action-pill">[CTA]</span><p class="lede">Add accurate alt text and final captions before scheduling.</p></div>` }
    ]
  }
];
