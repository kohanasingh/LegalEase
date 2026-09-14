"use client";

import { useCallback, useState } from "react";
import { useDropzone, type FileRejection } from "react-dropzone";
import { useRouter } from "next/navigation";
import { uploadDocument } from "@/lib/api";

const MAX_SIZE_BYTES = 20 * 1024 * 1024;

export default function UploadBox() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(
    async (acceptedFiles: File[], rejections: FileRejection[]) => {
      setError(null);
      if (rejections.length > 0) {
        setError(rejections[0].errors[0]?.message ?? "This file can't be uploaded.");
        return;
      }
      const file = acceptedFiles[0];
      if (!file) return;

      setIsUploading(true);
      try {
        const { doc_id } = await uploadDocument(file);
        router.push(`/analyze/${doc_id}`);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed. Please try again.");
        setIsUploading(false);
      }
    },
    [router]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxSize: MAX_SIZE_BYTES,
    maxFiles: 1,
    disabled: isUploading,
  });

  return (
    <div className="w-full max-w-xl">
      <div
        {...getRootProps()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-16 text-center shadow-sm shadow-brand-dark/5 transition-colors ${
          isDragActive
            ? "border-brand-primary bg-brand-surface"
            : "border-brand-border bg-brand-surface hover:border-brand-primary/50"
        } ${isUploading ? "cursor-not-allowed opacity-60" : ""}`}
      >
        <input {...getInputProps()} />
        {isUploading ? (
          <p className="text-brand-text">Uploading…</p>
        ) : (
          <>
            <p className="text-lg font-medium text-brand-dark">
              Drop your document here, or click to browse
            </p>
            <p className="mt-2 text-sm text-brand-text/70">PDF only, up to 20MB</p>
          </>
        )}
      </div>
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  );
}
