import Link from "next/link";
import UploadBox from "@/components/UploadBox";

export default function LandingPage() {
  return (
    <main className="flex flex-1 flex-col items-center px-4 py-20 sm:py-24">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold tracking-tight text-brand-dark sm:text-5xl">
          Demystify legal documents with the click of a button
        </h1>
        <p className="mt-5 text-lg leading-relaxed text-brand-text">
          Upload a contract, rental agreement, or notice, and LegalEase breaks it down
          in plain language — what it says, highlights any risky clauses and answers to any
          follow-up questions you have. It&apos;s informational, not a replacement for a
          lawyer.
        </p>
      </div>

      <div className="mt-12">
        <UploadBox />
      </div>

      <p className="mt-5 text-xs text-brand-text/70">
        Informational only, not a substitute for professional legal advice. See{" "}
        <Link href="/about" className="underline hover:text-brand-primary">
          more about LegalEase
        </Link>
        .
      </p>

      <section className="mt-24 grid max-w-4xl gap-6 sm:grid-cols-3">
        <Feature
          title="Plain-language summary"
          description="A clear explanation of what the document says and what it means for you."
        />
        <Feature
          title="Risk-flagged clauses"
          description="Unusual or one-sided terms are flagged safe, ambiguous, or risky, with reasoning."
        />
        <Feature
          title="Grounded follow-up Q&A"
          description="Ask questions and get answers grounded in your document and Indian law — not guesses."
        />
      </section>
    </main>
  );
}

function Feature({ title, description }: { title: string; description: string }) {
  return (
    <div className="rounded-2xl bg-brand-surface p-6 shadow-sm shadow-brand-dark/5">
      <h3 className="font-semibold text-brand-dark">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-brand-text">{description}</p>
    </div>
  );
}
