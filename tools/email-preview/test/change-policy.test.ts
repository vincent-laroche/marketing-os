import assert from "node:assert/strict";
import test from "node:test";
import { isBuildNoteOnlyChange } from "../src/change-policy.js";

const before = `<body>
<!-- BUILD NOTE: Hi {{ firstname }}, -->
<p>Live copy</p>
</body>`;

test("accepts a change confined to one-line build-note comments", () => {
  const after = before.replace("{{ firstname }}", '{{ customer.first_name | default: "there" }}');

  assert.equal(isBuildNoteOnlyChange(before, after), true);
});

test("rejects unchanged sources and any live-copy change", () => {
  assert.equal(isBuildNoteOnlyChange(before, before), false);
  assert.equal(isBuildNoteOnlyChange(before, before.replace("Live copy", "Changed live copy")), false);
  assert.equal(
    isBuildNoteOnlyChange(
      before,
      before
        .replace("{{ firstname }}", '{{ customer.first_name | default: "there" }}')
        .replace("Live copy", "Changed live copy"),
    ),
    false,
  );
});
