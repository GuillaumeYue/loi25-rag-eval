// Splits an answer into plain text and [n] citation markers so the view can
// render the markers as links to the numbered sources.

export type AnswerPart = { kind: "text"; value: string } | { kind: "cite"; n: number };

const CITATION = /\[(\d+)\]/g;

export function splitAnswer(answer: string): AnswerPart[] {
  const parts: AnswerPart[] = [];
  let last = 0;
  for (const match of answer.matchAll(CITATION)) {
    const start = match.index;
    if (start > last) parts.push({ kind: "text", value: answer.slice(last, start) });
    parts.push({ kind: "cite", n: Number(match[1]) });
    last = start + match[0].length;
  }
  if (last < answer.length) parts.push({ kind: "text", value: answer.slice(last) });
  return parts;
}

export function citedNumbers(answer: string): Set<number> {
  return new Set(splitAnswer(answer).flatMap((p) => (p.kind === "cite" ? [p.n] : [])));
}
