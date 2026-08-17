"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { ImagePlus, Loader2, X } from "lucide-react";
import { cn } from "@/lib/cn";
import type { Attachment } from "@/lib/types";

interface ImageDropzoneProps {
  attachments: Attachment[];
  onUpload: (files: File[]) => void | Promise<void>;
  onRemove: (attachmentId: string) => void | Promise<void>;
  uploading?: boolean;
  getPreviewUrl: (attachment: Attachment) => string;
}

export function ImageDropzone({
  attachments,
  onUpload,
  onRemove,
  uploading,
  getPreviewUrl,
}: ImageDropzoneProps) {
  const [removing, setRemoving] = useState<string | null>(null);

  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted.length) onUpload(accepted);
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [] },
    multiple: true,
  });

  async function handleRemove(id: string) {
    setRemoving(id);
    try {
      await onRemove(id);
    } finally {
      setRemoving(null);
    }
  }

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed p-6 text-center transition",
          isDragActive
            ? "border-brand-500 bg-brand-50"
            : "border-slate-300 hover:border-brand-400 hover:bg-slate-50"
        )}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <Loader2 className="h-6 w-6 animate-spin text-brand-500" />
        ) : (
          <ImagePlus className="h-6 w-6 text-slate-400" />
        )}
        <p className="text-sm text-slate-500">
          تصاویر چارت را اینجا بکشید یا کلیک کنید تا انتخاب شوند
        </p>
      </div>

      {attachments.length > 0 && (
        <div className="grid grid-cols-3 gap-3 sm:grid-cols-4">
          {attachments.map((att) => (
            <div
              key={att.id}
              className="group relative aspect-square overflow-hidden rounded-lg border border-slate-200 bg-slate-50"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={getPreviewUrl(att)}
                alt={att.caption ?? att.file_name}
                className="h-full w-full object-cover"
              />
              <button
                type="button"
                onClick={() => handleRemove(att.id)}
                disabled={removing === att.id}
                className="absolute top-1 left-1 rounded-full bg-slate-900/60 p-1 text-white opacity-0 transition group-hover:opacity-100"
              >
                {removing === att.id ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <X className="h-3.5 w-3.5" />
                )}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
