import EmptyState from "../components/EmptyState";

export default function EntretienManager() {
  return (
    <section>
      <h1>Entretien manager</h1>
      <EmptyState
        title="Aucune question générée"
        hint="Les questions et cas, avec réponse à l'oral, arriveront dans une prochaine étape."
      />
    </section>
  );
}
