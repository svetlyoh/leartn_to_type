import { useState } from "react";
import { api } from "../api/client";
import { CHARACTERS } from "../components/characters/characterCatalog";
export function CreatePlayerScreen({
  onBack,
  onCreated,
}: {
  onBack: () => void;
  onCreated: () => void;
}) {
  const [name, setName] = useState("");
  const [character, setCharacter] = useState("runner_01");
  const [schoolStatus, setSchoolStatus] = useState("skipped");
  const [grade, setGrade] = useState("");
  const [error, setError] = useState("");
  const create = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api("/profiles", {
        method: "POST",
        body: JSON.stringify({
          display_name: name,
          character_id: character,
          school_status: schoolStatus,
          grade_level: schoolStatus === "student" ? grade : null,
        }),
      });
      onCreated();
    } catch {
      setError(
        "Could not create your player. Check the details and try again.",
      );
    }
  };
  return (
    <main className="form-screen create-player">
      <button className="quiet" onClick={onBack}>
        ← Main menu
      </button>
      <form onSubmit={create}>
        <p className="eyebrow">Player setup</p>
        <h1>Create player</h1>
        <label>
          Display name
          <input
            autoFocus
            value={name}
            maxLength={40}
            required
            onChange={(e) => setName(e.target.value)}
          />
        </label>
        <label>
          School status
          <select
            value={schoolStatus}
            onChange={(e) => setSchoolStatus(e.target.value)}
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
              onChange={(e) => setGrade(e.target.value)}
            />
          </label>
        )}
        <fieldset>
          <legend>Character style (cosmetic only)</legend>
          <div className="character-picker">
            {CHARACTERS.map((item) => (
              <button
                className="tooltip-card"
                type="button"
                key={item.id}
                aria-describedby={`help-${item.id}`}
                aria-pressed={character === item.id}
                onClick={() => setCharacter(item.id)}
              >
                <img src={item.image} alt="" />
                <span>
                  <b>{item.name}</b>
                  <small>{item.trait}</small>
                </span>
                <span
                  role="tooltip"
                  className="character-help"
                  id={`help-${item.id}`}
                >
                  {item.help}
                </span>
              </button>
            ))}
          </div>
        </fieldset>
        <button>Create player</button>
        {error && (
          <p className="warning" role="alert">
            {error}
          </p>
        )}
      </form>
    </main>
  );
}
