import React from "react";
import { Hexagon } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="min-h-screen text-zinc-100 flex flex-col items-center justify-center p-4"
      style={{
        background: "radial-gradient(ellipse 70% 50% at 30% 20%, rgba(6,182,212,0.07) 0%, transparent 60%), radial-gradient(ellipse 60% 50% at 70% 80%, rgba(139,92,246,0.07) 0%, transparent 60%), #09090b",
      }}
    >
      {/* Brand */}
      <div className="mb-8 flex items-center gap-2 text-zinc-400">
        <Hexagon className="w-5 h-5 text-cyan-500" />
        <span className="font-mono text-sm tracking-widest uppercase">Document Forensics</span>
      </div>

      {/* Card — no backdrop-blur, plain bg instead */}
      <div className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-2xl">
        {children}
      </div>

      <p className="mt-6 text-zinc-600 text-xs font-mono">
        v2.1.0 · BITS Document Forensics
      </p>
    </div>
  );
}
