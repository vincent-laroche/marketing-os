const buildNoteLine = /^\s*<!-- BUILD NOTE:.*-->\s*$/;

function partition(source: string): { buildNotes: string[]; live: string[] } {
  const buildNotes: string[] = [];
  const live: string[] = [];
  for (const line of source.split(/\r?\n/)) {
    (buildNoteLine.test(line) ? buildNotes : live).push(line);
  }
  return { buildNotes, live };
}

export function isBuildNoteOnlyChange(before: string, after: string): boolean {
  if (before === after) return false;
  const base = partition(before);
  const head = partition(after);
  return (
    base.live.join("\n") === head.live.join("\n") &&
    base.buildNotes.join("\n") !== head.buildNotes.join("\n")
  );
}
