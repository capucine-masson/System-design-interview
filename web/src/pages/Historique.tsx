import ManagerHistory from "../components/ManagerHistory";
import SdSessionList from "../components/SdSessionList";

export default function Historique() {
  return (
    <section>
      <h1>Historique</h1>
      <ManagerHistory />
      <SdSessionList
        title="System Design"
        emptyHint="Tes sessions de System Design apparaîtront ici, avec ton schéma."
      />
    </section>
  );
}
