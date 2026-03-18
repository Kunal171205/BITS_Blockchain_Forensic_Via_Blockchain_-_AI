"use client";

import React from "react";
import { FileText, Hash, Boxes, Clock, ShieldCheck } from "lucide-react";

interface DocumentEntry {
  filename: string;
  hash: string;
  tx_hash: string;
  block_number: number;
  timestamp: string;
}

interface DocumentRegistryProps {
  documents: DocumentEntry[];
  isLoading: boolean;
}

export function DocumentRegistry({ documents, isLoading }: DocumentRegistryProps) {
  if (isLoading) {
    return (
      <div className="border border-zinc-800 rounded-xl bg-zinc-950 p-8 flex items-center justify-center">
        <span className="text-zinc-500 font-mono text-sm animate-pulse uppercase tracking-widest">
          Loading registry...
        </span>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="border border-zinc-800 rounded-xl bg-zinc-950 p-8 flex flex-col items-center justify-center space-y-3">
        <Boxes className="w-10 h-10 text-zinc-700" />
        <p className="text-zinc-500 font-mono text-sm">No documents registered yet</p>
        <p className="text-zinc-600 text-xs">Upload a document above to anchor it on the blockchain</p>
      </div>
    );
  }

  return (
    <div className="border border-zinc-800 rounded-xl bg-zinc-950 overflow-hidden">
      {/* Table Header */}
      <div className="grid grid-cols-12 gap-2 px-5 py-3 bg-zinc-900/50 border-b border-zinc-800 text-xs text-zinc-500 font-mono uppercase tracking-widest">
        <div className="col-span-3 flex items-center space-x-1">
          <FileText className="w-3 h-3" />
          <span>Filename</span>
        </div>
        <div className="col-span-4 flex items-center space-x-1">
          <Hash className="w-3 h-3" />
          <span>Document Hash</span>
        </div>
        <div className="col-span-2 flex items-center space-x-1">
          <Boxes className="w-3 h-3" />
          <span>Block</span>
        </div>
        <div className="col-span-3 flex items-center space-x-1">
          <Clock className="w-3 h-3" />
          <span>Registered</span>
        </div>
      </div>

      {/* Table Body */}
      <div className="divide-y divide-zinc-800/50">
        {documents.map((doc, index) => (
          <div
            key={doc.hash + index}
            className="grid grid-cols-12 gap-2 px-5 py-3.5 hover:bg-zinc-900/30 transition-colors group"
          >
            <div className="col-span-3 flex items-center space-x-2 min-w-0">
              <ShieldCheck className="w-4 h-4 text-emerald-500 flex-shrink-0" />
              <span className="text-zinc-300 text-sm truncate" title={doc.filename}>
                {doc.filename}
              </span>
            </div>
            <div className="col-span-4 flex items-center min-w-0">
              <span
                className="text-cyan-400/80 text-xs font-mono truncate group-hover:text-cyan-400 transition-colors"
                title={doc.hash}
              >
                {doc.hash.substring(0, 12)}...{doc.hash.substring(doc.hash.length - 8)}
              </span>
            </div>
            <div className="col-span-2 flex items-center">
              <span className="text-violet-400 text-sm font-mono">
                #{doc.block_number}
              </span>
            </div>
            <div className="col-span-3 flex items-center">
              <span className="text-zinc-500 text-xs font-mono">
                {formatTimestamp(doc.timestamp)}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="px-5 py-2.5 bg-zinc-900/30 border-t border-zinc-800 flex justify-between items-center">
        <span className="text-xs text-zinc-600 font-mono">
          {documents.length} document{documents.length !== 1 ? "s" : ""} anchored
        </span>
        <span className="text-[10px] text-emerald-500/50 font-mono uppercase tracking-widest">
          Blockchain Verified
        </span>
      </div>
    </div>
  );
}

function formatTimestamp(isoString: string): string {
  try {
    const date = new Date(isoString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return isoString;
  }
}
