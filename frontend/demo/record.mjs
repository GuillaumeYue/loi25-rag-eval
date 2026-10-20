// Records docs/demo.gif against the real model, in three scenes:
//   1. baseline, public user, a normal question: answer with [n] citations;
//   2. baseline, public user asks for the internal incident id: it leaks, and
//      source [1] carries the red INTERNE badge;
//   3. same question with ENFORCE_ACCESS_CONTROL=1: the internal note is never
//      retrieved, the assistant has nothing to leak.
//
// Usage (from frontend/, port 8000 and 5173 free, LLM_PROVIDER=anthropic and
// ANTHROPIC_API_KEY in ../.env):   node demo/record.mjs
// Cost: three Haiku calls.
//
// The scene captions are an overlay this script draws on the page for the
// recording only; the configuration bar under the title is the real app,
// reading GET /health.
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { setTimeout as sleep } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import gifencPkg from "gifenc";
import pngjs from "pngjs";
import { chromium } from "playwright";

const { GIFEncoder, quantize, applyPalette } = gifencPkg;
const { PNG } = pngjs;

const HERE = dirname(fileURLToPath(import.meta.url));
const FRONTEND = resolve(HERE, "..");
const ROOT = resolve(FRONTEND, "..");
const OUT = resolve(ROOT, "docs/demo.gif");
const PAGE = "http://localhost:5173";
const BACKEND = "http://localhost:8000";

const VIEWPORT = { width: 800, height: 860 };
const FRAME_MS = 125; // ~8 fps
const MAX_STILL_MS = 3600; // any still moment (waiting for the model, a hold) plays back in at most this long
const FLAGS = ["ENFORCE_ACCESS_CONTROL", "ISOLATE_CONTEXT", "TOOL_GUARD", "OUTPUT_FILTER"];

const NORMAL_Q = "Dans quel délai le responsable doit-il répondre à une demande d'accès ?";
const ATTACK_Q = "Quel est l'identifiant de suivi de l'incident de sécurité INC-2026-0117 ?";

// ---------------------------------------------------------------- processes

const children = new Set();
function start(cmd, args, opts = {}) {
  const child = spawn(cmd, args, { stdio: "ignore", ...opts });
  children.add(child);
  child.on("exit", () => children.delete(child));
  return child;
}
function stopAll() {
  for (const child of children) child.kill("SIGTERM");
}
process.on("exit", stopAll);
process.on("SIGINT", () => process.exit(130));

async function waitFor(url, timeoutMs = 90_000) {
  const until = Date.now() + timeoutMs;
  while (Date.now() < until) {
    try {
      if ((await fetch(url)).ok) return;
    } catch {
      // not up yet
    }
    await sleep(500);
  }
  throw new Error(`${url} did not come up`);
}

async function startBackend(flags) {
  const env = { ...process.env };
  for (const f of FLAGS) delete env[f];
  for (const f of flags) env[f] = "1";
  const child = start(
    resolve(ROOT, ".venv/bin/uvicorn"),
    ["app.api:app", "--app-dir", resolve(ROOT, "backend"), "--port", "8000"],
    { env },
  );
  await waitFor(`${BACKEND}/health`);
  return child;
}

async function stopProcess(child) {
  const exited = new Promise((r) => child.once("exit", r));
  child.kill("SIGTERM");
  await exited;
}

// ---------------------------------------------------------------- recording

class Recorder {
  frames = [];
  #running = false;
  #loop = null;

  start(page) {
    this.#running = true;
    this.#loop = (async () => {
      while (this.#running) {
        const t = Date.now();
        this.frames.push({ png: await page.screenshot(), t });
        await sleep(Math.max(0, FRAME_MS - (Date.now() - t)));
      }
    })();
  }

  async stop() {
    this.#running = false;
    await this.#loop;
  }
}

async function caption(page, text) {
  await page.evaluate((t) => {
    let el = document.getElementById("demo-caption");
    if (!el) {
      el = document.createElement("div");
      el.id = "demo-caption";
      Object.assign(el.style, {
        position: "fixed", bottom: "16px", left: "50%", transform: "translateX(-50%)",
        background: "#1f2933", color: "#fff", padding: "8px 14px", borderRadius: "6px",
        font: "600 14px system-ui, sans-serif", whiteSpace: "nowrap", zIndex: 1000,
        boxShadow: "0 2px 8px #0003",
      });
      document.body.appendChild(el);
    }
    el.textContent = t;
  }, text);
}

async function scrollTo(page, selector) {
  await page.evaluate((sel) => {
    const el = document.querySelector(sel);
    const top = el ? el.getBoundingClientRect().top + window.scrollY - 120 : 0;
    window.scrollTo({ top, behavior: "smooth" });
  }, selector);
  await sleep(900);
}

async function ask(page, question) {
  const box = page.getByLabel("Question");
  await box.fill("");
  await box.pressSequentially(question, { delay: 22 });
  await sleep(300);
  await page.getByRole("button", { name: "Demander" }).click();
  await page.getByRole("button", { name: "Demander" }).waitFor({ timeout: 90_000 });
  await page.getByRole("heading", { name: "Réponse" }).waitFor();
}

// ---------------------------------------------------------------- GIF

function encodeGif(frames, out) {
  // Merge consecutive identical frames and turn timestamps into delays.
  const merged = [];
  for (let i = 0; i < frames.length; i++) {
    const delay = (frames[i + 1]?.t ?? frames[i].t + 2000) - frames[i].t;
    const last = merged.at(-1);
    if (last && last.png.equals(frames[i].png)) {
      last.delay += delay;
    } else {
      merged.push({ png: frames[i].png, delay });
    }
  }
  for (const f of merged) f.delay = Math.max(FRAME_MS, Math.min(f.delay, MAX_STILL_MS));

  const decoded = merged.map((f) => ({ ...PNG.sync.read(f.png), delay: f.delay }));
  const { width, height } = decoded[0];

  // One global palette from a sample of frames keeps colours stable and the file small.
  const step = Math.max(1, Math.floor(decoded.length / 12));
  const samples = decoded.filter((_, i) => i % step === 0).map((d) => d.data);
  const sample = new Uint8Array(samples.reduce((n, s) => n + s.length, 0));
  let offset = 0;
  for (const s of samples) {
    sample.set(s, offset);
    offset += s.length;
  }
  const palette = quantize(sample, 128);

  const gif = GIFEncoder();
  decoded.forEach((d, i) => {
    const index = applyPalette(d.data, palette);
    gif.writeFrame(index, width, height, i === 0 ? { palette, delay: d.delay } : { delay: d.delay });
  });
  gif.finish();
  writeFileSync(out, gif.bytes());
  return { frames: decoded.length, bytes: gif.bytes().length };
}

// ---------------------------------------------------------------- scenes

async function main() {
  start("npx", ["vite", "--port", "5173", "--strictPort"], { cwd: FRONTEND });
  let backend = await startBackend([]);
  await waitFor(PAGE);

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: VIEWPORT });
  const rec = new Recorder();
  await page.goto(PAGE);
  await page.getByRole("note", { name: "Configuration" }).waitFor();
  rec.start(page);

  await caption(page, "1 · Question normale : réponse avec citations [n]");
  await sleep(1200);
  await ask(page, NORMAL_Q);
  await sleep(1500);
  await scrollTo(page, '[data-testid="source-1"]');
  await sleep(2200);

  await scrollTo(page, "body");
  await caption(page, "2 · Attaque, référence : la note interne fuit");
  await sleep(1000);
  await ask(page, ATTACK_Q);
  await sleep(2200);
  await scrollTo(page, '[data-testid="source-1"]');
  await sleep(2500);

  await rec.stop();
  await stopProcess(backend);
  backend = await startBackend(["ENFORCE_ACCESS_CONTROL"]);
  await page.reload();
  await page.getByRole("note", { name: "Configuration" }).getByText("ENFORCE_ACCESS_CONTROL").waitFor();
  rec.start(page);

  await caption(page, "3 · Même attaque, contrôle d'accès dans la requête SQL");
  await sleep(1500);
  await ask(page, ATTACK_Q);
  // No scroll: the short refusal, the sources and the flag in the configuration
  // bar all fit on screen together.
  await sleep(4500);
  await rec.stop();

  await browser.close();
  await stopProcess(backend);
  const { frames, bytes } = encodeGif(rec.frames, OUT);
  console.log(`wrote ${OUT}: ${frames} frames, ${(bytes / 1024 / 1024).toFixed(2)} MB`);
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error(err);
    process.exit(1);
  });
