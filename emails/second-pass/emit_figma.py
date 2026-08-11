"""Emit the use_figma JS for a slice of the spec. Run: python3 emit_figma.py 0 2"""
import json, sys

SPEC = json.load(open("figma_spec.json"))
a, b = int(sys.argv[1]), int(sys.argv[2])
DROP = ("bg", "tx", "mu", "dv", "bb", "bt", "ac", "logoTone", "journey", "preview")
sl = []
for e in SPEC[a:b]:
    e = {k: v for k, v in e.items() if k not in DROP}
    e["modules"] = [{k: v for k, v in m.items() if k not in DROP} for m in e["modules"]]
    sl.append(e)

JS = """
const SPEC = %(spec)s;
const START = %(start)d;
const PAGE = "291:724", LOGO = "284:8864", COL = 700;
const SURF = {
 bone:      {bg:"#F7F1DE",tx:"#15140F",mu:"#5A5448",dv:"#DDD2B6",bb:"#ED6F5C",bt:"#15140F",ac:"#ED6F5C"},
 paper:     {bg:"#EFE7D2",tx:"#15140F",mu:"#5A5448",dv:"#DDD2B6",bb:"#ED6F5C",bt:"#15140F",ac:"#ED6F5C"},
 paper_dark:{bg:"#DDD2B6",tx:"#15140F",mu:"#5A5448",dv:"#5A5448",bb:"#ED6F5C",bt:"#15140F",ac:"#ED6F5C"},
 ink:       {bg:"#15140F",tx:"#F7F1DE",mu:"#DDD2B6",dv:"#2A2620",bb:"#ED6F5C",bt:"#15140F",ac:"#ED6F5C"},
 ink_soft:  {bg:"#2A2620",tx:"#F7F1DE",mu:"#DDD2B6",dv:"#15140F",bb:"#ED6F5C",bt:"#15140F",ac:"#ED6F5C"},
 coral:     {bg:"#ED6F5C",tx:"#15140F",mu:"#15140F",dv:"#F08E7C",bb:"#15140F",bt:"#F7F1DE",ac:"#15140F"}
};

const page = figma.root.children.find(p => p.id === PAGE);
await figma.setCurrentPageAsync(page);

// idempotent: clear whatever this builder produced before re-running
if (START === 0) {
  const need = new Set();
  for (const t of page.query("TEXT").toArray()) {
    for (const sg of t.getStyledTextSegments(["fontName"]))
      need.add(sg.fontName.family + "||" + sg.fontName.style);
  }
  for (const k of need) {
    const [family, style] = k.split("||");
    await figma.loadFontAsync({ family, style });
  }
  for (const c of page.children.slice()) c.remove();
}

const F = {
  mono:   { family: "JetBrains Mono",  style: "Regular" },
  h:      { family: "Inter Tight",     style: "Bold" },
  hs:     { family: "Inter Tight",     style: "SemiBold" },
  body:   { family: "Inter",           style: "Regular" },
  bodyB:  { family: "Inter",           style: "Semi Bold" },
  ital:   { family: "Inter",           style: "Italic" },
  serif:  { family: "Playfair Display", style: "Italic" }
};
for (const k in F) await figma.loadFontAsync(F[k]);

const hex = h => ({ r: parseInt(h.slice(1,3),16)/255,
                    g: parseInt(h.slice(3,5),16)/255,
                    b: parseInt(h.slice(5,7),16)/255 });
const solid = h => [{ type: "SOLID", color: hex(h) }];
const CORAL = ["#ED6F5C","#EA6452","#F08E7C"];

function txt(s, font, size, color, lh, ls) {
  const t = figma.createText();
  t.fontName = font;
  t.characters = s || " ";
  t.fontSize = size;
  t.fills = solid(color);
  if (lh) t.lineHeight = { unit: "PERCENT", value: lh };
  if (ls) t.letterSpacing = { unit: "PIXELS", value: ls };
  t.textAutoResize = "HEIGHT";
  return t;
}
function add(parent, node, fill) {
  parent.appendChild(node);
  if (fill !== false) node.layoutSizingHorizontal = "FILL";
  return node;
}
async function wordmark(parent, tone, tx, w) {
  const src = await figma.getNodeByIdAsync(LOGO);
  const g = src.clone();
  for (const n of g.findAll(n => Array.isArray(n.fills) && n.fills.length)) {
    const f = n.fills[0];
    if (!f || f.type !== "SOLID") continue;
    const h = "#" + [f.color.r,f.color.g,f.color.b]
      .map(v => ("0"+Math.round(v*255).toString(16)).slice(-2)).join("").toUpperCase();
    if (CORAL.indexOf(h) === -1) n.fills = solid(tx);   // keep the coral "co"
  }
  const holder = figma.createAutoLayout("HORIZONTAL", { name: "Wordmark" });
  holder.fills = [];
  holder.primaryAxisAlignItems = tone === "center" ? "CENTER" : "MIN";
  parent.appendChild(holder);
  holder.layoutSizingHorizontal = "FILL";
  holder.layoutSizingVertical = "HUG";
  holder.appendChild(g);
  g.rescale(w / g.width);
  return g;
}

const created = [];
for (let i = 0; i < SPEC.length; i++) {
  const e = SPEC[i];
  const frame = figma.createAutoLayout("VERTICAL",
    { name: e.code + " · " + e.subject, itemSpacing: 12 });
  frame.paddingLeft = frame.paddingRight = 24;
  frame.paddingTop = frame.paddingBottom = 28;
  frame.fills = solid("#EFE7D2");
  frame.x = (START + i) * COL; frame.y = 0;
  page.appendChild(frame);
  frame.resize(648, 100);
  frame.layoutSizingVertical = "HUG";

  const title = add(frame, txt(e.code + " · " + e.pos + "  —  " + e.subject,
                               F.mono, 11, "#5A5448", 140, 1.2));
  title.name = "Label";

  for (const m0 of e.modules) {
    const m = Object.assign({}, m0, SURF[m0.surface]);
    const card = figma.createAutoLayout("VERTICAL", { name: m.name + " / " + m.surface,
                                                      itemSpacing: 14 });
    card.paddingLeft = card.paddingRight = card.paddingTop = card.paddingBottom = 32;
    card.fills = solid(m.bg);
    card.cornerRadius = 16;
    frame.appendChild(card);
    card.layoutSizingHorizontal = "FILL";
    card.layoutSizingVertical = "HUG";

    for (const it of m.items) {
      if (it.t === "logo") {
        await wordmark(card, it.align === "center" ? "center" : "left", m.tx, 132);
      } else if (it.t === "eyebrow") {
        const row = figma.createAutoLayout("HORIZONTAL", { name: "Ruled eyebrow", itemSpacing: 10 });
        row.fills = []; row.counterAxisAlignItems = "CENTER";
        card.appendChild(row); row.layoutSizingHorizontal = "FILL"; row.layoutSizingVertical = "HUG";
        const rule = figma.createRectangle();
        rule.resize(22, 1); rule.fills = solid(m.ac); rule.name = "Rule";
        row.appendChild(rule);
        const lab = txt(it.s.toUpperCase(), F.mono, 11, m.tx, 140, 1.5);
        row.appendChild(lab); lab.layoutSizingHorizontal = "FILL";
      } else if (it.t === "h") {
        const t = add(card, txt(it.s + (it.accent ? " " + it.accent : ""), F.h, 24, m.tx, 125, -0.3));
        if (it.accent) {
          const st = it.s.length + 1;
          t.setRangeFontName(st, t.characters.length, F.serif);
          t.setRangeFontSize(st, t.characters.length, 24);
        }
      } else if (it.t === "p") {
        const t = add(card, txt(it.s, F.body, 15, m.mu, 155));
        if (it.bold) t.setRangeFontName(0, Math.min(it.bold.length, t.characters.length), F.bodyB);
      } else if (it.t === "sig") {
        add(card, txt(it.s, F.ital, 15, m.mu, 155));
      } else if (it.t === "small") {
        add(card, txt(it.s, it.strong ? F.bodyB : F.body, 12, it.strong ? m.tx : m.mu, 160));
      } else if (it.t === "meta") {
        add(card, txt(it.s.toUpperCase(), F.mono, 11, m.tx, 140, 1.5));
      } else if (it.t === "code") {
        const box = figma.createAutoLayout("HORIZONTAL", { name: "Promo code" });
        box.fills = []; box.strokes = solid(m.tx); box.strokeWeight = 1;
        box.dashPattern = [4, 3]; box.cornerRadius = 8;
        box.paddingLeft = box.paddingRight = 18; box.paddingTop = box.paddingBottom = 14;
        box.primaryAxisAlignItems = "CENTER";
        card.appendChild(box); box.layoutSizingHorizontal = "FILL"; box.layoutSizingVertical = "HUG";
        const c = txt(it.s, F.mono, 20, m.tx, 130, 3);
        c.textAlignHorizontal = "CENTER";
        box.appendChild(c); c.layoutSizingHorizontal = "FILL";
      } else if (it.t === "kv") {
        const row = figma.createAutoLayout("HORIZONTAL", { name: "Row", itemSpacing: 16 });
        row.fills = []; row.paddingTop = row.paddingBottom = 10;
        row.strokes = solid(m.dv); row.strokeTopWeight = 1;
        row.strokeBottomWeight = row.strokeLeftWeight = row.strokeRightWeight = 0;
        card.appendChild(row); row.layoutSizingHorizontal = "FILL"; row.layoutSizingVertical = "HUG";
        const k = txt(it.k, F.body, 13, m.mu, 150);
        row.appendChild(k); k.layoutSizingHorizontal = "FILL";
        const v = txt(it.v, F.bodyB, 13, m.tx, 150);
        v.textAlignHorizontal = "RIGHT";
        row.appendChild(v); v.layoutSizingHorizontal = "FILL";
      } else if (it.t === "rule") {
        const r = figma.createRectangle();
        r.name = "Divider"; r.fills = solid(m.dv);
        card.appendChild(r); r.layoutSizingHorizontal = "FILL"; r.resize(r.width, 1);
      } else if (it.t === "btn" || it.t === "btnrow") {
        const row = figma.createAutoLayout("HORIZONTAL", { name: "CTA", itemSpacing: 10 });
        row.fills = [];
        card.appendChild(row); row.layoutSizingHorizontal = "FILL"; row.layoutSizingVertical = "HUG";
        const mk = (label, solidFill) => {
          const p = figma.createAutoLayout("HORIZONTAL", { name: "Button" });
          p.paddingLeft = p.paddingRight = 24; p.paddingTop = p.paddingBottom = 13;
          p.cornerRadius = 999;
          if (solidFill) { p.fills = solid(m.bb); p.strokes = []; }
          else { p.fills = []; p.strokes = solid(m.tx); p.strokeWeight = 1; }
          row.appendChild(p); p.layoutSizingHorizontal = "HUG"; p.layoutSizingVertical = "HUG";
          const l = txt(label, F.hs, 13, solidFill ? m.bt : m.tx, 130, 0.5);
          p.appendChild(l); l.layoutSizingHorizontal = "HUG";
          return p;
        };
        if (it.t === "btn") mk(it.s, true);
        else { mk(it.primary, true); if (it.secondary) mk(it.secondary, false); }
      }
    }
  }
  created.push({ code: e.code, id: frame.id, h: Math.round(frame.height) });
}
return { created };
"""

print(JS % {"spec": json.dumps(sl, ensure_ascii=False, separators=(",", ":")), "start": a})
