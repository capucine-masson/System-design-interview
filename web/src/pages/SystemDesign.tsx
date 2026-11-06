import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createSdSession, drawCase, generateCase, listCaseTypes } from "../api";
import SdSessionList from "../components/SdSessionList";
import { type TKey, useI18n } from "../i18n";
import type { CaseFamily, CaseType, SdCase } from "../types";

type Action = "generate" | "draw";
const RANDOM = "random";

const FAMILIES: { value: CaseFamily; label: TKey }[] = [
  { value: "ml", label: "sd.familyMl" },
  { value: "classique", label: "sd.familyClassic" },
];

interface CaseOptionProps {
  value: string;
  title: string;
  description: string;
  selected: string;
  disabled: boolean;
  onSelect: (value: string) => void;
}

function CaseOption({ value, title, description, selected, disabled, onSelect }: CaseOptionProps) {
  return (
    <label className={`case-type${selected === value ? " is-selected" : ""}`}>
      <input
        type="radio"
        name="case-type"
        checked={selected === value}
        disabled={disabled}
        onChange={() => onSelect(value)}
      />
      <strong>{title}</strong>
      <span className="muted">{description}</span>
    </label>
  );
}

export default function SystemDesign() {
  const { lang, t } = useI18n();
  const navigate = useNavigate();
  const [types, setTypes] = useState<CaseType[] | null>(null);
  const [selected, setSelected] = useState<string>(RANDOM);
  const [busy, setBusy] = useState<Action | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listCaseTypes()
      .then(setTypes)
      .catch((err: Error) => setError(err.message));
  }, [lang]);

  const start = async (action: Action): Promise<void> => {
    if (!types) return;
    setBusy(action);
    setError(null);
    try {
      const slug =
        selected === RANDOM ? types[Math.floor(Math.random() * types.length)].slug : selected;
      const found: SdCase =
        action === "generate"
          ? await generateCase(slug)
          : await drawCase(selected === RANDOM ? undefined : slug);
      const session = await createSdSession(found.id);
      navigate(`/system-design/sessions/${session.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("sd.startFailed"));
      setBusy(null);
    }
  };

  const disabled = busy !== null || types === null;
  return (
    <section>
      <h1>{t("sd.title")}</h1>
      <div className="card setup">
        <p className="muted">{t("sd.intro")}</p>
        {!types && !error && <p className="muted">{t("sd.loadingCases")}</p>}
        {types && (
          <div className="case-groups">
            <fieldset className="case-types">
              <legend>{t("sd.randomLegend")}</legend>
              <CaseOption
                value={RANDOM}
                title={t("sd.randomTitle")}
                description={t("sd.randomDesc")}
                selected={selected}
                disabled={disabled}
                onSelect={setSelected}
              />
            </fieldset>
            {FAMILIES.map((family) => (
              <fieldset key={family.value} className="case-types">
                <legend>{t(family.label)}</legend>
                {types
                  .filter((type) => type.famille === family.value)
                  .map((type) => (
                    <CaseOption
                      key={type.slug}
                      value={type.slug}
                      title={type.titre}
                      description={type.description}
                      selected={selected}
                      disabled={disabled}
                      onSelect={setSelected}
                    />
                  ))}
              </fieldset>
            ))}
          </div>
        )}
        <div className="setup-actions">
          <button
            type="button"
            className="btn btn-primary"
            disabled={disabled}
            onClick={() => void start("generate")}
          >
            {busy === "generate" ? t("sd.generating") : t("sd.generate")}
          </button>
          <button type="button" className="btn" disabled={disabled} onClick={() => void start("draw")}>
            {busy === "draw" ? t("common.drawing") : t("common.draw")}
          </button>
        </div>
        {error && <div className="notice notice-error">{error}</div>}
      </div>
      <SdSessionList
        title={t("sd.resume")}
        emptyHint={t("sd.resumeEmpty")}
      />
    </section>
  );
}
