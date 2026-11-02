import EmptyState from "../components/EmptyState";

export default function Historique() {
  return (
    <section>
      <h1>Historique</h1>
      <EmptyState
        title="Rien à revoir pour l'instant"
        hint="Tes réponses et sessions passées apparaîtront ici."
      />
    </section>
  );
}
