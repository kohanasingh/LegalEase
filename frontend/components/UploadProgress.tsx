"use client";

import { useEffect, useRef, useState } from "react";
import { getDocumentStatus } from "@/lib/api";
import type { DocumentStatus } from "@/lib/types";

const POLL_INTERVAL_MS = 2000;
// Rough midpoint of observed end-to-end Analysis Crew runtime (varies with
// document length and LLM rate-limit pacing — see CHANGES.md). This is an
// expectation-setting estimate, not a promise, which is why it's paired
// with a live elapsed counter below rather than a countdown that could run
// past zero and look broken.
const ESTIMATED_WAIT_SECONDS = 150;

function formatDuration(totalSeconds: number): string {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}

// backend/api/document_routes.py only reports one "analyzing" status for the
// whole Analysis Crew run (it doesn't expose per-agent progress), so this
// groups statuses into three user-facing stages rather than the finer
// "Identifying clauses -> Cross-checking law -> Finalizing" breakdown
// ARCHITECTURE.md sketches — that would need per-agent status callbacks we
// don't have yet.
const STEPS: { label: string; matches: DocumentStatus[] }[] = [
  { label: "Reading your document", matches: ["uploaded", "parsing", "chunking", "embedding"] },
  { label: "Identifying clauses and cross-checking Indian law", matches: ["analyzing"] },
  { label: "Finalizing", matches: ["complete"] },
];

interface UploadProgressProps {
  docId: string;
  onComplete: () => void;
  onError: (message: string) => void;
}

export default function UploadProgress({ docId, onComplete, onError }: UploadProgressProps) {
  const [status, setStatus] = useState<DocumentStatus>("uploaded");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);
  useEffect(() => {
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
  }, [onComplete, onError]);

  useEffect(() => {
    const interval = setInterval(() => setElapsedSeconds((s) => s + 1), 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let cancelled = false;
    const poll = async () => {
      try {
        const result = await getDocumentStatus(docId);
        if (cancelled) return;
        setStatus(result.status);
        if (result.status === "complete") {
          onCompleteRef.current();
          return;
        }
        if (result.status === "failed") {
          onErrorRef.current(result.error ?? "Analysis failed. Please try again.");
          return;
        }
        setTimeout(poll, POLL_INTERVAL_MS);
      } catch {
        if (!cancelled) setTimeout(poll, POLL_INTERVAL_MS);
      }
    };
    poll();
    return () => {
      cancelled = true;
    };
  }, [docId]);

  const activeIndex = STEPS.findIndex((step) => step.matches.includes(status));

  return (
    <div className="mx-auto max-w-md py-16">
      <ul className="space-y-4">
        {STEPS.map((step, index) => {
          const isDone = activeIndex > index;
          const isActive = activeIndex === index;
          return (
            <li key={step.label} className="flex items-center gap-3">
              <span
                className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
                  isDone
                    ? "bg-green-600 text-white"
                    : isActive
                      ? "animate-pulse bg-blue-600 text-white"
                      : "bg-slate-200 text-slate-500"
                }`}
              >
                {isDone ? "✓" : index + 1}
              </span>
              <span className={isActive ? "font-medium text-slate-900" : "text-slate-500"}>
                {step.label}
              </span>
            </li>
          );
        })}
      </ul>
      <p className="mt-6 text-center text-sm text-slate-500">
        Usually takes about {formatDuration(ESTIMATED_WAIT_SECONDS)} · elapsed{" "}
        {formatDuration(elapsedSeconds)}
      </p>
    </div>
  );
}
