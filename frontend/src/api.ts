// Mirrors backend/app/schemas.py. If the contract changes there, change it here.

export type Role = "public" | "employe";

export interface Source {
  n: number;
  title: string;
  source: string;
  classification: "public" | "interne";
  excerpt: string;
}

export interface ToolCall {
  tool: string;
  arguments: Record<string, unknown>;
}

export interface BlockedToolCall extends ToolCall {
  reason: string;
}

export interface AskResponse {
  answer: string;
  sources: Source[];
  tool_calls: ToolCall[];
  // Added with the mitigations; absent or empty in the baseline.
  blocked_tool_calls?: BlockedToolCall[];
  output_filtered?: boolean;
}

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export interface Health {
  status: string;
  llm_provider: string;
  model: string | null;
  flags: Record<string, boolean>;
}

/** The backend's configuration (provider, model, mitigation flags), or null if unavailable. */
export async function getHealth(): Promise<Health | null> {
  try {
    const response = await fetch("/health");
    if (!response.ok) return null;
    const body = (await response.json()) as Partial<Health>;
    return body && typeof body.flags === "object" ? (body as Health) : null;
  } catch {
    return null;
  }
}

export async function ask(question: string, role: Role): Promise<AskResponse> {
  const response = await fetch("/ask", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ question, role }),
  });
  if (!response.ok) {
    throw new ApiError(response.status, await errorDetail(response));
  }
  return (await response.json()) as AskResponse;
}

// FastAPI puts the reason in `detail`: a string for our 502s, a list for 422s.
async function errorDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((d) => (d as { msg?: string }).msg ?? JSON.stringify(d))
        .join("; ");
    }
  } catch {
    // not JSON; fall through
  }
  return `Erreur ${response.status}`;
}
