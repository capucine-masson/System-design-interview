import { useI18n } from "../i18n";

interface StarIconProps {
  className: string;
}

export default function StarIcon({ className }: StarIconProps) {
  const { t } = useI18n();
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
      role="img"
      aria-label={t("card.essentialLabel")}
    >
      <title>{t("card.essentialTitle")}</title>
      <path d="M12 2.5l2.9 6.1 6.6.9-4.8 4.6 1.2 6.6L12 17.5l-5.9 3.2 1.2-6.6L2.5 9.5l6.6-.9z" />
    </svg>
  );
}
