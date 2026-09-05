import { useState } from "react";
import { api } from "../api/client";
export function LoginNameScreen({ onReady }: { onReady: () => void }) {
  const [name, setName] = useState("");
  const [schoolStatus, setSchoolStatus] = useState("skipped");
  const [grade, setGrade] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api("/auth/name", {
        method: "POST",
        body: JSON.stringify({
          name,
          school_status: schoolStatus,
          grade_level: schoolStatus === "student" ? grade : null,
        }),
      });
      onReady();
    } catch {
      setError("Cadence could not save your player details. Try again.");
    } finally {
      setBusy(false);
    }
  };
  return (
    <main className="form-screen">
      <form onSubmit={submit}>
        <p className="eyebrow">Player setup</p>
        <h1>What’s your name?</h1>
        <p>Cadence saves this to your passkey account for future sign-ins.</p>
        <label>
          Player name
          <input
            autoFocus
            value={name}
            maxLength={40}
            placeholder="MCP"
            onChange={(event) => setName(event.target.value)}
          />
        </label>
        <label>
          School status
          <select
            value={schoolStatus}
            onChange={(event) => setSchoolStatus(event.target.value)}
          >
            <option value="skipped">Prefer not to say</option>
            <option value="student">Student</option>
            <option value="not_student">Not currently a student</option>
          </select>
        </label>
        {schoolStatus === "student" && (
          <label>
            Grade
            <input
              value={grade}
              maxLength={20}
              onChange={(event) => setGrade(event.target.value)}
            />
          </label>
        )}
        <button disabled={busy}>{busy ? "Saving player…" : "Continue"}</button>
        <p className="notice">Leave the name blank to use MCP.</p>
        {error && (
          <p className="warning" role="alert">
            {error}
          </p>
        )}
      </form>
    </main>
  );
}
