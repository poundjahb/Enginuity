type MetricCardProps = {
  label: string;
  value: string;
  hint?: string;
};

export default function MetricCard({ label, value, hint }: MetricCardProps) {
  return (
    <article className="rounded-2xl border border-sky-400/20 bg-slate-950/60 p-5 shadow-card backdrop-blur">
      <p className="text-sm uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-3 text-5xl font-semibold text-slate-100">{value}</p>
      {hint ? <p className="mt-2 text-sm text-slate-400">{hint}</p> : null}
    </article>
  );
}
