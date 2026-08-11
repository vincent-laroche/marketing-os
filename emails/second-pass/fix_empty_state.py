"""Make modules collapse gracefully when an optional field is left empty.

Two artifacts showed up as soon as real emails were composed:
  * an empty `button_label` still rendered the coral pill — a floating blob
  * an empty `label_N`/`value_N` still rendered its ruled table row — blank rules

Both mean a module can only be used with every field filled, which is wrong: a
commerce block often needs no second CTA, and a spec table often has two rows, not
five. Guard each on its own field.
"""
import os, re, shutil

SRC, OUT = "live2", "staging-empty/email_modules"

# a CTA pill: its own <table>, one <tr><td background:{{ c.bb }} … border-radius:999px
BUTTON = re.compile(
    r'<table(?:(?!</table>).)*?<td style="background:\{\{ c\.bb \}\};border-radius:999px;'
    r'(?:(?!</table>).)*?\{\{ module\.(\w*label) \}\}(?:(?!</table>).)*?</table>', re.S)

# a label/value row in a two-column spec table
ROW = re.compile(
    r'<tr>(?:(?!</tr>).)*?\{\{ module\.(\w+_\d)\s*\}\}(?:(?!</tr>).)*?</tr>', re.S)

ROW_MODULES = {"commerce_quote_spec_table", "billing_payment_details", "comparison"}


def guard_buttons(html):
    n = 0

    def sub(m):
        nonlocal n
        if m.group(0).lstrip().startswith("{%"):
            return m.group(0)
        n += 1
        return "{%% if module.%s %%}%s{%% endif %%}" % (m.group(1), m.group(0))

    return BUTTON.sub(sub, html), n


def guard_rows(html):
    n = 0

    def sub(m):
        nonlocal n
        field = m.group(1)
        n += 1
        return "{%% if module.%s %%}%s{%% endif %%}" % (field, m.group(0))

    return ROW.sub(sub, html), n


if __name__ == "__main__":
    shutil.rmtree("staging-empty", ignore_errors=True)
    touched = 0
    for d in sorted(os.listdir(SRC)):
        if not d.endswith(".module"):
            continue
        fam = d.replace("_dark.module", "").replace(".module", "")
        p = os.path.join(SRC, d, "module.html")
        html = open(p).read()
        new, nb = guard_buttons(html)
        nr = 0
        if fam in ROW_MODULES:
            new, nr = guard_rows(new)
        if nb or nr:
            dst = os.path.join(OUT, d)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copytree(os.path.join(SRC, d), dst)
            open(os.path.join(dst, "module.html"), "w").write(new)
            touched += 1
            if not d.endswith("_dark.module"):
                print(f"  {d:44s} buttons+{nb} rows+{nr}")
    print(f"\n{touched} module folders updated")
