interface DocumentSummaryPanelProps {
  summary: string;
}

export default function DocumentSummaryPanel({ summary }: DocumentSummaryPanelProps) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Summary</h2>
      <p className="mt-3 whitespace-pre-line text-slate-700">{summary}</p>
    </section>
  );
}
