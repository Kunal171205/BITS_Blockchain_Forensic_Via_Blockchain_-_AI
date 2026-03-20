"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, File as FileIcon, Loader2, CheckCircle, XCircle, AlertTriangle } from "lucide-react";

const API_URL = "http://localhost:5000";

interface UploadResult {
  success: boolean;
  status: string;
  hash: string;
  tx_hash?: string;
  block_number?: number;
  filename?: string;
  timestamp?: string;
  reason?: string;
  error?: string;
}

interface AdminUploaderProps {
  onUploadSuccess: () => void;
}

export function AdminUploader({ onUploadSuccess }: AdminUploaderProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;

      const file = acceptedFiles[0];
      setIsUploading(true);
      setResult(null);

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_URL}/api/admin/upload`, {
          method: "POST",
          body: formData,
        });

        const data: UploadResult = await response.json();
        setResult(data);

        if (data.success) {
          onUploadSuccess();
        }
      } catch (err) {
        setResult({
          success: false,
          status: "error",
          hash: "",
          reason: `Network error: ${err instanceof Error ? err.message : "Unknown error"}`,
        });
      }

      setIsUploading(false);
    },
    [onUploadSuccess]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".png", ".jpg", ".jpeg"],
      "application/pdf": [".pdf"],
    },
    maxFiles: 1,
    disabled: isUploading,
  });

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <div
        className={`w-full border-2 border-dashed rounded-xl flex flex-col items-center justify-center p-8 transition-all duration-300 cursor-pointer
          ${isUploading
            ? "border-amber-500/40 bg-amber-900/10"
            : isDragActive
              ? "border-cyan-400 bg-cyan-900/20"
              : "border-zinc-700 bg-zinc-950/50 hover:bg-zinc-900/50 hover:border-zinc-600"
          }
        `}
      >
        <div
          {...getRootProps()}
          className="w-full flex flex-col items-center justify-center min-h-[200px]"
        >
          <input {...getInputProps()} />
          {isUploading ? (
            <div className="flex flex-col items-center space-y-4">
              <Loader2 className="w-14 h-14 text-amber-400 animate-spin" />
              <p className="font-mono text-amber-400 text-sm tracking-wider uppercase">
                Anchoring to blockchain...
              </p>
            </div>
          ) : (
            <div className="flex flex-col items-center space-y-4">
              <UploadCloud
                className={`w-14 h-14 ${isDragActive ? "text-cyan-400" : "text-zinc-500"} transition-colors`}
              />
              <p className="text-center text-zinc-400">
                {isDragActive
                  ? "Drop the document here..."
                  : "Drag & drop a document to register on blockchain"}
              </p>
              <span className="text-xs text-zinc-600 uppercase tracking-widest">
                Supported: Images (PNG/JPG), PDF
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Result Feedback */}
      {result && (
        <div
          className={`rounded-xl border p-5 transition-all duration-500 animate-in fade-in ${
            result.success
              ? "border-emerald-500/30 bg-emerald-900/10"
              : result.status === "duplicate"
                ? "border-amber-500/30 bg-amber-900/10"
                : "border-rose-500/30 bg-rose-900/10"
          }`}
        >
          {/* Header */}
          <div className="flex items-center space-x-3 mb-4">
            {result.success ? (
              <>
                <CheckCircle className="w-6 h-6 text-emerald-400" />
                <span className="font-mono font-bold text-emerald-400 uppercase tracking-wider text-sm">
                  Document Anchored Successfully
                </span>
              </>
            ) : result.status === "duplicate" ? (
              <>
                <AlertTriangle className="w-6 h-6 text-amber-400" />
                <span className="font-mono font-bold text-amber-400 uppercase tracking-wider text-sm">
                  Already Registered
                </span>
              </>
            ) : (
              <>
                <XCircle className="w-6 h-6 text-rose-400" />
                <span className="font-mono font-bold text-rose-400 uppercase tracking-wider text-sm">
                  Registration Failed
                </span>
              </>
            )}
          </div>

          {/* Details */}
          <div className="space-y-2 text-sm font-mono">
            {result.filename && (
              <div className="flex justify-between">
                <span className="text-zinc-500">File</span>
                <span className="text-zinc-300 truncate max-w-[300px]">{result.filename}</span>
              </div>
            )}
            {result.hash && (
              <div className="flex justify-between">
                <span className="text-zinc-500">SHA-256</span>
                <span className="text-cyan-400 truncate max-w-[300px]" title={result.hash}>
                  {result.hash.substring(0, 16)}...{result.hash.substring(result.hash.length - 8)}
                </span>
              </div>
            )}
            {result.tx_hash && (
              <div className="flex justify-between">
                <span className="text-zinc-500">TX Hash</span>
                <span className="text-violet-400 truncate max-w-[300px]" title={result.tx_hash}>
                  {result.tx_hash.substring(0, 16)}...{result.tx_hash.substring(result.tx_hash.length - 8)}
                </span>
              </div>
            )}
            {result.block_number !== undefined && result.block_number > 0 && (
              <div className="flex justify-between">
                <span className="text-zinc-500">Block #</span>
                <span className="text-emerald-400">{result.block_number}</span>
              </div>
            )}
            {result.reason && !result.success && (
              <div className="flex justify-between">
                <span className="text-zinc-500">Reason</span>
                <span className="text-rose-400">{result.reason}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
