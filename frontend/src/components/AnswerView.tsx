import { splitAnswer } from "../citations";

export function AnswerView({ answer }: { answer: string }) {
  return (
    <section className="answer" aria-labelledby="answer-title">
      <h2 id="answer-title">Réponse</h2>
      <p className="answer-text">
        {splitAnswer(answer).map((part, i) =>
          part.kind === "text" ? (
            <span key={i}>{part.value}</span>
          ) : (
            <a key={i} className="cite" href={`#source-${part.n}`} title={`Source ${part.n}`}>
              [{part.n}]
            </a>
          ),
        )}
      </p>
    </section>
  );
}
