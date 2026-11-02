interface EmptyStateProps {
  title: string;
  hint: string;
}

export default function EmptyState({ title, hint }: EmptyStateProps) {
  return (
    <div className="card empty">
      <h2>{title}</h2>
      <p className="muted">{hint}</p>
    </div>
  );
}
