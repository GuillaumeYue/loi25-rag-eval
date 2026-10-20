import { useState } from "react";
import { ApiError, ask, type AskResponse, type Role } from "./api";
import { AnswerView } from "./components/AnswerView";
import { QuestionForm } from "./components/QuestionForm";
import { SourceList } from "./components/SourceList";
import { ToolCallList } from "./components/ToolCallList";
import { citedNumbers } from "./citations";

export default function App() {
  const [role, setRole] = useState<Role>("public");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<AskResponse | null>(null);

  async function submit(question: string) {
    setLoading(true);
    setError(null);
    try {
      setResponse(await ask(question, role));
    } catch (err) {
      setResponse(null);
      setError(err instanceof ApiError ? err.message : "Le serveur est injoignable.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header>
        <h1>Assistant Loi 25</h1>
        <p className="subtitle">
          Assistant de conformité d'Énergie Boréale (fictive). Projet de test : les documents
          et l'entreprise sont inventés.
        </p>
      </header>

      <QuestionForm role={role} onRoleChange={setRole} onSubmit={submit} loading={loading} />

      {error && (
        <div role="alert" className="error">
          {error}
        </div>
      )}

      {response && (
        <>
          {response.output_filtered && (
            <div role="status" className="notice">
              Filtre de sortie : la réponse générée a été retenue parce qu'elle contenait
              des renseignements internes.
            </div>
          )}
          <AnswerView answer={response.answer} />
          <SourceList sources={response.sources} cited={citedNumbers(response.answer)} />
          <ToolCallList toolCalls={response.tool_calls} blocked={response.blocked_tool_calls} />
        </>
      )}
    </main>
  );
}
