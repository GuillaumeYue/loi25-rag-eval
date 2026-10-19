import type { Source } from "../api";

interface Props {
  sources: Source[];
  cited: Set<number>;
}

export function SourceList({ sources, cited }: Props) {
  if (sources.length === 0) {
    return (
      <section className="sources">
        <h2>Sources</h2>
        <p className="muted">Aucune source trouvée.</p>
      </section>
    );
  }
  return (
    <section className="sources" aria-labelledby="sources-title">
      <h2 id="sources-title">Sources</h2>
      <ol>
        {sources.map((s) => (
          <li
            key={s.n}
            id={`source-${s.n}`}
            className={`source ${cited.has(s.n) ? "cited" : "uncited"}`}
            data-testid={`source-${s.n}`}
          >
            <div className="source-head">
              <span className="source-n">[{s.n}]</span>
              <span className="source-title">{s.title}</span>
              <span className={`badge ${s.classification}`}>{s.classification}</span>
            </div>
            <div className="source-path">{s.source}</div>
            <p className="excerpt">{s.excerpt}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
