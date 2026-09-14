// Persistent, non-dismissible disclaimer. Shown on every analysis page —
// do not add a close/dismiss control here (CLAUDE.md non-negotiable #7).
export default function DisclaimerBanner() {
  return (
    <div className="border-b border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      <p className="mx-auto max-w-4xl">
        <span className="font-semibold">Informational only, not legal advice.</span>{" "}
        LegalEase explains documents in plain language but cannot replace a qualified
        legal professional. Always consult a lawyer before acting on anything here.
      </p>
    </div>
  );
}
