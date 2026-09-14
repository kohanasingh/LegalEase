export default function AboutPage() {
  return (
    <main className="mx-auto max-w-2xl flex-1 px-4 py-16">
      <h1 className="text-3xl font-bold text-slate-900">About LegalEase</h1>
      <p className="mt-4 text-slate-700">
        LegalEase is an International Hackathon winning project demonstrating a real, working agentic RAG
        system for legal document analysis — built for the average Indian person
        handed a rental agreement, employment contract, or loan document with no easy
        way to understand what they&apos;re signing.
      </p>
      <p className="mt-4 text-slate-700">
        Upload a document and LegalEase parses it, cross-references its clauses
        against a corpus of Indian bare acts and regulations, flags risky or
        ambiguous terms, and lets you ask grounded follow-up questions.
      </p>

      <div className="mt-8 rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900">
        <p className="font-semibold">This is not a substitute for legal advice.</p>
        <p className="mt-1">
          Every analysis and chat answer is informational only. Questions or clauses
          that need a qualified professional&apos;s judgment are flagged as such,
          rather than answered speculatively. Always consult a lawyer before acting on
          anything LegalEase tells you.
        </p>
      </div>

      <h2 className="mt-10 text-xl font-semibold text-slate-900">What LegalEase doesn&apos;t do</h2>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-slate-700">
        <li>No user accounts, payments, or multi-tenant infrastructure.</li>
        <li>Doesn&apos;t cover the entirety of Indian law — corpus coverage is intentionally scoped and documented, not silently incomplete.</li>
        <li>Doesn&apos;t monitor for real-time changes in law, yet.</li>
        <li>Not a licensed legal service.</li>
      </ul>
    </main>
  );
}
