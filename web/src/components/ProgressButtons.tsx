import type { ReactNode } from "react";
import type { Statut } from "../types";

interface ProgressButtonsProps {
  statut: Statut | null;
  disabled: boolean;
  onChange: (statut: Statut | null) => void;
}

const ICON_PROPS = {
  width: 14,
  height: 14,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2.5,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
} as const;

const OPTIONS: { value: Statut; label: string; icon: ReactNode }[] = [
  {
    value: "maitrisee",
    label: "Maîtrisée",
    icon: (
      <svg {...ICON_PROPS}>
        <path d="M5 12.5l4.5 4.5L19 7.5" />
      </svg>
    ),
  },
  {
    value: "a_revoir",
    label: "À revoir",
    icon: (
      <svg {...ICON_PROPS}>
        <path d="M20 12a8 8 0 1 1-2.4-5.7" />
        <path d="M20 4v5h-5" />
      </svg>
    ),
  },
];

export default function ProgressButtons({ statut, disabled, onChange }: ProgressButtonsProps) {
  return (
    <div className="progress-buttons" role="group" aria-label="Suivi de la carte">
      {OPTIONS.map((option) => {
        const active = statut === option.value;
        return (
          <button
            key={option.value}
            type="button"
            className={`icon-btn icon-btn-${option.value}${active ? " is-active" : ""}`}
            aria-label={option.label}
            title={option.label}
            aria-pressed={active}
            disabled={disabled}
            onClick={() => onChange(active ? null : option.value)}
          >
            {option.icon}
          </button>
        );
      })}
    </div>
  );
}
