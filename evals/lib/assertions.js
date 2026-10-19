// Programmatic assertions for promptfoo. `output` is the full /ask response
// object ({answer, sources, tool_calls}) because the HTTP provider uses
// transformResponse: json. `context.vars` carries the test case's variables.
//
// Each function returns a GradingResult ({pass, score, reason}) so the reason
// shows up in the promptfoo report next to the failing case.

// Must match REFUSAL_SENTENCE in backend/app/prompting.py.
const REFUSAL_SENTENCE = "Je ne trouve pas cette information dans les documents fournis.";

const CITATION = /\[(\d+)\]/g;

function result(pass, reason) {
  return { pass, score: pass ? 1 : 0, reason };
}

function asResponse(output) {
  if (output && typeof output === "object") return output;
  try {
    return JSON.parse(output);
  } catch {
    throw new Error(`output is not a /ask response: ${String(output).slice(0, 80)}`);
  }
}

function citedNumbers(answer) {
  return [...answer.matchAll(CITATION)].map((m) => Number(m[1]));
}

function expectedSources(context) {
  let expected = context?.vars?.expected_sources;
  // promptfoo hands list variables to file assertions as a JSON string.
  if (typeof expected === "string") {
    try {
      expected = JSON.parse(expected);
    } catch {
      expected = expected.split(",").map((s) => s.trim()).filter(Boolean);
    }
  }
  if (!Array.isArray(expected) || expected.length === 0) {
    throw new Error("test case has no expected_sources");
  }
  return expected;
}

/** One of the expected sources is among the retrieved chunks (top-k). */
function retrievalHit(output, context) {
  const { sources } = asResponse(output);
  const expected = expectedSources(context);
  const retrieved = sources.map((s) => s.source);
  const hit = expected.find((e) => retrieved.includes(e));
  return hit
    ? result(true, `retrieved ${hit}`)
    : result(false, `expected one of ${expected.join(", ")}; got ${retrieved.join(", ")}`);
}

/** The answer cites a [n] whose source is one of the expected sources. */
function citesExpected(output, context) {
  const { answer, sources } = asResponse(output);
  const expected = expectedSources(context);
  const cited = citedNumbers(answer).map((n) => sources[n - 1]?.source).filter(Boolean);
  const good = cited.find((s) => expected.includes(s));
  return good
    ? result(true, `cites ${good}`)
    : result(false, `cited ${cited.length ? cited.join(", ") : "nothing"}; expected one of ${expected.join(", ")}`);
}

/** The answer contains at least one [n] citation. */
function hasCitation(output) {
  const { answer } = asResponse(output);
  const n = citedNumbers(answer).length;
  return n > 0 ? result(true, `${n} citation(s)`) : result(false, "no [n] citation in the answer");
}

/** An answerable question must not get the refusal sentence. */
function noRefusal(output) {
  const { answer } = asResponse(output);
  return answer.includes(REFUSAL_SENTENCE)
    ? result(false, "answer contains the refusal sentence")
    : result(true, "answered");
}

/** An unanswerable question must get the exact refusal sentence. */
function refuses(output) {
  const { answer } = asResponse(output);
  return answer.includes(REFUSAL_SENTENCE)
    ? result(true, "refused as instructed")
    : result(false, `no refusal sentence; answer starts: ${answer.slice(0, 80)}`);
}

/** No tool call on a plain question. */
function noToolCall(output) {
  const { tool_calls } = asResponse(output);
  const n = (tool_calls ?? []).length;
  return n === 0
    ? result(true, "no tool call")
    : result(false, `${n} tool call(s): ${tool_calls.map((t) => t.tool).join(", ")}`);
}

module.exports = {
  REFUSAL_SENTENCE,
  retrievalHit,
  citesExpected,
  hasCitation,
  noRefusal,
  refuses,
  noToolCall,
};
