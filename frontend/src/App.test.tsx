import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { AskResponse } from "./api";

const RESPONSE: AskResponse = {
  answer: "Le délai est de 30 jours [1]. Voir aussi [2].",
  sources: [
    {
      n: 1,
      title: "Loi 25 (P-39.1), article 32",
      source: "public/loi-25/art-32.md",
      classification: "public",
      excerpt: "32. La personne qui détient...",
    },
    {
      n: 2,
      title: "Note interne",
      source: "internal/note-interne-incident.md",
      classification: "interne",
      excerpt: "CLASSIFICATION : INTERNE",
    },
    {
      n: 3,
      title: "Politique",
      source: "public/politique-confidentialite.md",
      classification: "public",
      excerpt: "...",
    },
  ],
  tool_calls: [],
};

const BASELINE_HEALTH = {
  status: "ok",
  llm_provider: "anthropic",
  model: "claude-haiku-5-5",
  flags: { ENFORCE_ACCESS_CONTROL: false, ISOLATE_CONTEXT: false, TOOL_GUARD: false, OUTPUT_FILTER: false },
};

const json = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

// /health answers with `health` (the page asks for it on load); every other URL with `body`.
function mockFetch(status: number, body: unknown, health: unknown = BASELINE_HEALTH) {
  const fetchMock = vi.fn(async (url: string) =>
    url === "/health" ? json(200, health) : json(status, body),
  );
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

async function askQuestion(text = "Quel délai ?") {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("Question"), text);
  await user.click(screen.getByRole("button", { name: "Demander" }));
  return user;
}

afterEach(() => vi.unstubAllGlobals());

describe("App", () => {
  it("sends the question with the selected role", async () => {
    const fetchMock = mockFetch(200, RESPONSE);
    render(<App />);
    const user = userEvent.setup();
    await user.click(screen.getByLabelText("Employé"));
    await askQuestion("Quel délai ?");

    await screen.findByRole("heading", { name: "Réponse" });
    const askCall = fetchMock.mock.calls.find(([u]) => u === "/ask");
    const [url, init] = askCall as unknown as [string, RequestInit];
    expect(url).toBe("/ask");
    expect(JSON.parse(init.body as string)).toEqual({ question: "Quel délai ?", role: "employe" });
  });

  it("renders the answer with citation links and numbered sources with badges", async () => {
    mockFetch(200, RESPONSE);
    render(<App />);
    await askQuestion();

    const cite = await screen.findByRole("link", { name: "[1]" });
    expect(cite).toHaveAttribute("href", "#source-1");
    expect(screen.getByRole("link", { name: "[2]" })).toBeInTheDocument();

    expect(screen.getByTestId("source-1")).toHaveClass("cited");
    expect(screen.getByTestId("source-3")).toHaveClass("uncited");
    expect(screen.getByTestId("source-2")).toHaveTextContent("interne");
    expect(screen.getByText("internal/note-interne-incident.md")).toBeInTheDocument();
    expect(screen.queryByText("Appels d'outils (simulés)")).not.toBeInTheDocument();
  });

  it("shows tool calls when the model used a tool", async () => {
    mockFetch(200, {
      ...RESPONSE,
      tool_calls: [{ tool: "send_email", arguments: { to: "x@exemple.net" } }],
    });
    render(<App />);
    await askQuestion();

    await screen.findByText("Appels d'outils (simulés)");
    expect(screen.getByText("send_email")).toBeInTheDocument();
    expect(screen.getByText(/x@exemple\.net/)).toBeInTheDocument();
  });

  it("shows blocked tool calls with their reason and the output-filter notice", async () => {
    mockFetch(200, {
      ...RESPONSE,
      answer: "Réponse retenue : elle contenait des renseignements internes.",
      output_filtered: true,
      blocked_tool_calls: [
        {
          tool: "send_email",
          arguments: { to: "x@collecte-donnees.example.net" },
          reason: "domaine destinataire non autorisé : collecte-donnees.example.net",
        },
      ],
    });
    render(<App />);
    await askQuestion();

    expect(await screen.findByRole("status")).toHaveTextContent("Filtre de sortie");
    expect(screen.getByText(/bloqué : domaine destinataire non autorisé/)).toBeInTheDocument();
    expect(screen.getByText(/collecte-donnees\.example\.net"/)).toBeInTheDocument();
  });

  it("shows the backend error detail", async () => {
    mockFetch(502, { detail: "Claude API error 429: quota" });
    render(<App />);
    await askQuestion();

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("Claude API error 429: quota"),
    );
    expect(screen.queryByRole("heading", { name: "Réponse" })).not.toBeInTheDocument();
  });

  it("shows the configuration under test from /health", async () => {
    mockFetch(200, RESPONSE);
    render(<App />);
    const footer = await screen.findByRole("note", { name: "Configuration" });
    expect(footer).toHaveTextContent("claude-haiku-5-5");
    expect(footer).toHaveTextContent("aucune (configuration de référence)");
  });

  it("lists the active mitigation flags", async () => {
    mockFetch(200, RESPONSE, {
      ...BASELINE_HEALTH,
      flags: { ...BASELINE_HEALTH.flags, ENFORCE_ACCESS_CONTROL: true, OUTPUT_FILTER: true },
    });
    render(<App />);
    const footer = await screen.findByRole("note", { name: "Configuration" });
    expect(footer).toHaveTextContent("Mitigations actives");
    expect(footer).toHaveTextContent("ENFORCE_ACCESS_CONTROL");
    expect(footer).toHaveTextContent("OUTPUT_FILTER");
    expect(footer).not.toHaveTextContent("TOOL_GUARD");
  });

  it("hides the configuration when /health is unavailable", async () => {
    const fetchMock = mockFetch(200, RESPONSE, { detail: "not a health payload" });
    render(<App />);
    // Wait until the /health response has been read, then let React settle.
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith("/health"));
    const healthResponse = fetchMock.mock.results[0].value as Promise<Response>;
    await healthResponse;
    await new Promise((resolve) => setTimeout(resolve, 0));
    expect(screen.queryByRole("note", { name: "Configuration" })).not.toBeInTheDocument();
  });

  it("disables the button while the question is empty", () => {
    render(<App />);
    expect(screen.getByRole("button", { name: "Demander" })).toBeDisabled();
  });
});
