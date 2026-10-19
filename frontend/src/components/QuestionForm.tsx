import { useState, type FormEvent } from "react";
import type { Role } from "../api";

interface Props {
  role: Role;
  onRoleChange: (role: Role) => void;
  onSubmit: (question: string) => void;
  loading: boolean;
}

export function QuestionForm({ role, onRoleChange, onSubmit, loading }: Props) {
  const [question, setQuestion] = useState("");

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (trimmed) onSubmit(trimmed);
  }

  return (
    <form className="question-form" onSubmit={handleSubmit}>
      <fieldset className="role">
        <legend>Je suis</legend>
        <label>
          <input
            type="radio"
            name="role"
            value="public"
            checked={role === "public"}
            onChange={() => onRoleChange("public")}
          />
          Public
        </label>
        <label>
          <input
            type="radio"
            name="role"
            value="employe"
            checked={role === "employe"}
            onChange={() => onRoleChange("employe")}
          />
          Employé
        </label>
      </fieldset>

      <label className="question-label" htmlFor="question">
        Question
      </label>
      <textarea
        id="question"
        rows={3}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ex. : Dans quel délai l'entreprise doit-elle répondre à une demande d'accès ?"
      />
      <button type="submit" disabled={loading || !question.trim()}>
        {loading ? "Recherche en cours…" : "Demander"}
      </button>
    </form>
  );
}
