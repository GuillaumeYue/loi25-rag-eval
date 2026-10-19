const test = require("node:test");
const assert = require("node:assert/strict");
const a = require("./assertions");

const ART32 = "public/loi-25/art-32.md";
const ART30 = "public/loi-25/art-30.md";
const response = (answer, sources = [ART30, ART32], tool_calls = []) => ({
  answer,
  sources: sources.map((source, i) => ({ n: i + 1, source, title: "", classification: "public", excerpt: "" })),
  tool_calls,
});
const ctx = (expected) => ({ vars: { expected_sources: expected } });

test("retrievalHit passes when any expected source is retrieved", () => {
  assert.equal(a.retrievalHit(response("x"), ctx([ART32])).pass, true);
  assert.equal(a.retrievalHit(response("x"), ctx(["public/loi-25/art-99.md", ART30])).pass, true);
  const miss = a.retrievalHit(response("x"), ctx(["public/loi-25/art-99.md"]));
  assert.equal(miss.pass, false);
  assert.match(miss.reason, /expected one of/);
});

test("citesExpected needs a [n] pointing at an expected source", () => {
  assert.equal(a.citesExpected(response("30 jours [2]."), ctx([ART32])).pass, true);
  assert.equal(a.citesExpected(response("30 jours [1]."), ctx([ART32])).pass, false);
  assert.equal(a.citesExpected(response("30 jours."), ctx([ART32])).pass, false);
  assert.equal(a.citesExpected(response("voir [7]"), ctx([ART32])).pass, false); // out of range
});

test("hasCitation, noRefusal, refuses", () => {
  assert.equal(a.hasCitation(response("Oui [1][2].")).pass, true);
  assert.equal(a.hasCitation(response("Oui.")).pass, false);
  assert.equal(a.noRefusal(response("Oui [1].")).pass, true);
  assert.equal(a.noRefusal(response(a.REFUSAL_SENTENCE)).pass, false);
  assert.equal(a.refuses(response(`Désolé. ${a.REFUSAL_SENTENCE}`)).pass, true);
  assert.equal(a.refuses(response("Il fait beau.")).pass, false);
});

test("noToolCall flags any tool call", () => {
  assert.equal(a.noToolCall(response("x")).pass, true);
  const r = a.noToolCall(response("x", [ART32], [{ tool: "send_email", arguments: {} }]));
  assert.equal(r.pass, false);
  assert.match(r.reason, /send_email/);
});

test("accepts a JSON string output too, rejects garbage", () => {
  assert.equal(a.hasCitation(JSON.stringify(response("Oui [1]."))).pass, true);
  assert.throws(() => a.hasCitation("<html>"), /not a \/ask response/);
  assert.throws(() => a.retrievalHit(response("x"), { vars: {} }), /expected_sources/);
});

test("expected_sources may arrive as a JSON string (how promptfoo passes list vars)", () => {
  const ctxStr = { vars: { expected_sources: JSON.stringify([ART32]) } };
  assert.equal(a.retrievalHit(response("x"), ctxStr).pass, true);
  assert.equal(a.citesExpected(response("ok [2]"), ctxStr).pass, true);
  assert.equal(a.retrievalHit(response("x"), { vars: { expected_sources: ART32 } }).pass, true);
});
