import type { ToolCall } from "../api";

// Shown only when the model called a tool. Nothing is ever sent: the backend
// logs the call and reports it here so misuse is visible at a glance.
export function ToolCallList({ toolCalls }: { toolCalls: ToolCall[] }) {
  if (toolCalls.length === 0) return null;
  return (
    <section className="tool-calls" aria-labelledby="tools-title">
      <h2 id="tools-title">Appels d'outils (simulés)</h2>
      <p className="muted">Aucun envoi réel : ces appels sont seulement journalisés.</p>
      <ul>
        {toolCalls.map((call, i) => (
          <li key={i} className="tool-call">
            <span className="tool-name">{call.tool}</span>
            <pre>{JSON.stringify(call.arguments, null, 2)}</pre>
          </li>
        ))}
      </ul>
    </section>
  );
}
