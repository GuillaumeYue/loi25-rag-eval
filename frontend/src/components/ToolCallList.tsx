import type { BlockedToolCall, ToolCall } from "../api";

interface Props {
  toolCalls: ToolCall[];
  blocked?: BlockedToolCall[];
}

// Shown only when the model called a tool. Nothing is ever sent: the backend
// logs executed calls, and TOOL_GUARD refusals are listed with their reason,
// so misuse (and what stopped it) is visible at a glance.
export function ToolCallList({ toolCalls, blocked = [] }: Props) {
  if (toolCalls.length === 0 && blocked.length === 0) return null;
  return (
    <section className="tool-calls" aria-labelledby="tools-title">
      <h2 id="tools-title">Appels d'outils (simulés)</h2>
      <p className="muted">Aucun envoi réel : ces appels sont seulement journalisés.</p>
      <ul>
        {toolCalls.map((call, i) => (
          <li key={`ok-${i}`} className="tool-call">
            <span className="tool-name">{call.tool}</span>
            <pre>{JSON.stringify(call.arguments, null, 2)}</pre>
          </li>
        ))}
        {blocked.map((call, i) => (
          <li key={`blocked-${i}`} className="tool-call blocked">
            <span className="tool-name">{call.tool}</span>
            <span className="blocked-label">bloqué : {call.reason}</span>
            <pre>{JSON.stringify(call.arguments, null, 2)}</pre>
          </li>
        ))}
      </ul>
    </section>
  );
}
