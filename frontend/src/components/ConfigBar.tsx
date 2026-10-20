import type { Health } from "../api";

// Shows which configuration answers: model and active mitigation flags, read
// from GET /health. Placed under the title so screenshots and the demo GIF
// always show it.
export function ConfigBar({ health }: { health: Health | null }) {
  if (!health) return null;
  const active = Object.entries(health.flags)
    .filter(([, on]) => on)
    .map(([name]) => name);
  return (
    <div className="config" role="note" aria-label="Configuration">
      <span>
        Modèle : <code>{health.model ?? health.llm_provider}</code>
      </span>
      <span>
        {active.length === 0 ? (
          <>Mitigations : aucune (configuration de référence)</>
        ) : (
          <>
            Mitigations actives :{" "}
            {active.map((name) => (
              <code key={name} className="flag">
                {name}
              </code>
            ))}
          </>
        )}
      </span>
    </div>
  );
}
