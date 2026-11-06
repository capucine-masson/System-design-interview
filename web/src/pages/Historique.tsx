import ManagerHistory from "../components/ManagerHistory";
import SdSessionList from "../components/SdSessionList";
import { useI18n } from "../i18n";

export default function Historique() {
  const { t } = useI18n();
  return (
    <section>
      <h1>{t("history.title")}</h1>
      <ManagerHistory />
      <SdSessionList
        title={t("sd.title")}
        emptyHint={t("history.sdEmpty")}
      />
    </section>
  );
}
