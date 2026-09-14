"use client";

import { useEffect, useState } from "react";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import UploadProgress from "@/components/UploadProgress";
import DocumentSummaryPanel from "@/components/DocumentSummaryPanel";
import ClauseHighlightList from "@/components/ClauseHighlightList";
import ChatPanel from "@/components/ChatPanel";
import { getDocumentAnalysis, getDocumentStatus } from "@/lib/api";
import { suggestExampleQuestion } from "@/lib/suggestQuestion";
import type { AnalysisResult } from "@/lib/types";

type ViewState =
  | { stage: "processing" }
  | { stage: "ready"; analysis: AnalysisResult }
  | { stage: "error"; message: string };

export default function AnalysisView({ docId }: { docId: string }) {
  const [state, setState] = useState<ViewState>({ stage: "processing" });

  const loadAnalysis = async () => {
    try {
      const analysis = await getDocumentAnalysis(docId);
      setState({ stage: "ready", analysis });
    } catch (err) {
      setState({
        stage: "error",
        message: err instanceof Error ? err.message : "Could not load the analysis.",
      });
    }
  };

  // If this page is opened directly for an already-complete doc_id, skip
  // straight to fetching the analysis instead of waiting on status polling
  // (which would otherwise never start, since UploadProgress mounts fresh
  // and has no way to know processing already finished before this page
  // loaded — e.g. a bookmarked or reloaded /analyze/[docId] URL).
  useEffect(() => {
    (async () => {
      try {
        const status = await getDocumentStatus(docId);
        if (status.status === "complete") {
          await loadAnalysis();
        } else if (status.status === "failed") {
          setState({ stage: "error", message: status.error ?? "Analysis failed." });
        }
        // otherwise leave state as "processing" — UploadProgress will poll and
        // call onComplete/onError itself.
      } catch (err) {
        setState({
          stage: "error",
          message: err instanceof Error ? err.message : "Could not load this document.",
        });
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [docId]);

  return (
    <div className="flex flex-1 flex-col">
      <DisclaimerBanner />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-10">
        {state.stage === "processing" && (
          <UploadProgress
            docId={docId}
            onComplete={loadAnalysis}
            onError={(message) => setState({ stage: "error", message })}
          />
        )}

        {state.stage === "error" && (
          <p className="mt-10 text-center text-red-600">{state.message}</p>
        )}

        {state.stage === "ready" && (
          <div className="space-y-6">
            <DocumentSummaryPanel summary={state.analysis.summary} />
            <ClauseHighlightList clauses={state.analysis.flagged_clauses} />
            {(state.analysis.consult_professional_notes.length > 0 ||
              state.analysis.out_of_scope_notes.length > 0) && (
              <section className="rounded-xl border border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
                {state.analysis.consult_professional_notes.length > 0 && (
                  <>
                    <h3 className="font-semibold text-slate-800">
                      Worth confirming with a lawyer
                    </h3>
                    <ul className="mt-1 list-disc pl-5">
                      {state.analysis.consult_professional_notes.map((note, i) => (
                        <li key={i}>{note}</li>
                      ))}
                    </ul>
                  </>
                )}
                {state.analysis.out_of_scope_notes.length > 0 && (
                  <>
                    <h3 className="mt-3 font-semibold text-slate-800">Outside this tool&apos;s scope</h3>
                    <ul className="mt-1 list-disc pl-5">
                      {state.analysis.out_of_scope_notes.map((note, i) => (
                        <li key={i}>{note}</li>
                      ))}
                    </ul>
                  </>
                )}
              </section>
            )}
            <ChatPanel docId={docId} exampleQuestion={suggestExampleQuestion(state.analysis.flagged_clauses)} />
          </div>
        )}
      </main>
    </div>
  );
}
