import type { FlaggedClause, RiskLevel } from "@/lib/types";

const RISK_STYLES: Record<RiskLevel, { badge: string; border: string }> = {
  safe: { badge: "bg-green-100 text-green-800", border: "border-green-200" },
  ambiguous: { badge: "bg-amber-100 text-amber-800", border: "border-amber-200" },
  risky: { badge: "bg-red-100 text-red-800", border: "border-red-200" },
};

interface ClauseHighlightListProps {
  clauses: FlaggedClause[];
}

export default function ClauseHighlightList({ clauses }: ClauseHighlightListProps) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6">
      <h2 className="text-lg font-semibold text-slate-900">Key clauses</h2>
      <ul className="mt-4 space-y-4">
        {clauses.map((clause) => {
          const style = RISK_STYLES[clause.risk_level] ?? RISK_STYLES.ambiguous;
          return (
            <li key={clause.clause_id} className={`rounded-lg border p-4 ${style.border}`}>
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold uppercase tracking-wide ${style.badge}`}
                >
                  {clause.risk_level}
                </span>
                <span className="text-xs text-slate-500">{clause.clause_type}</span>
              </div>
              <p className="mt-2 text-sm text-slate-800">{clause.text}</p>
              <p className="mt-2 text-sm text-slate-600 italic">{clause.reasoning}</p>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
