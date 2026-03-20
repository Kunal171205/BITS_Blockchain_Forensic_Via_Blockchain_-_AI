"use client";

import React from "react";
import Link from "next/link";
import { Shield, Brain, FileSearch, ArrowRight, Hexagon } from "lucide-react";

export default function HomePage() {
  return (
    <main
      className="min-h-screen text-zinc-100 overflow-hidden"
      style={{
        background: "radial-gradient(ellipse 80% 60% at 20% 10%, rgba(6,182,212,0.08) 0%, transparent 60%), radial-gradient(ellipse 60% 50% at 80% 90%, rgba(139,92,246,0.08) 0%, transparent 60%), #09090b",
      }}
    >
      <div className="flex flex-col items-center">

        {/* ─── HERO ─── */}
        <section className="w-full max-w-6xl mx-auto px-6 pt-24 pb-16 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 text-xs font-mono tracking-widest mb-8 uppercase">
            <Hexagon className="w-3 h-3" />
            AI-Powered · Blockchain-Secured
          </div>

          {/* Title */}
          <h1 className="text-5xl sm:text-7xl font-black tracking-tighter leading-none mb-6">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-cyan-300 to-emerald-400">
              Document
            </span>
            <br />
            <span className="text-white">Forensics</span>
          </h1>

          <p className="text-zinc-400 text-lg sm:text-xl max-w-2xl mx-auto leading-relaxed mb-12">
            Detect document tampering with state-of-the-art AI, then cross-verify
            authenticity against an immutable blockchain ledger — in seconds.
          </p>

          {/* ─── PORTAL CARDS ─── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-2xl mx-auto mb-20">
            {/* User Portal */}
            <Link
              href="/login?role=user"
              className="group relative flex flex-col items-start p-6 rounded-2xl border border-zinc-800 bg-zinc-900/60 hover:border-cyan-500/50 hover:bg-zinc-900 transition-all duration-300 text-left overflow-hidden"
            >
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mb-4 group-hover:bg-cyan-500/20 transition-colors">
                <FileSearch className="w-6 h-6 text-cyan-400" />
              </div>
              <h2 className="text-lg font-bold text-white mb-1">User Portal</h2>
              <p className="text-zinc-400 text-sm mb-4">
                Analyze and verify documents using AI tamper detection.
              </p>
              <div className="flex items-center gap-2 text-cyan-400 text-sm font-semibold mt-auto group-hover:gap-3 transition-all">
                Enter as User <ArrowRight className="w-4 h-4" />
              </div>
            </Link>

            {/* Admin Portal */}
            <Link
              href="/login?role=admin"
              className="group relative flex flex-col items-start p-6 rounded-2xl border border-zinc-800 bg-zinc-900/60 hover:border-violet-500/50 hover:bg-zinc-900 transition-all duration-300 text-left overflow-hidden"
            >
              <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center mb-4 group-hover:bg-violet-500/20 transition-colors">
                <Shield className="w-6 h-6 text-violet-400" />
              </div>
              <h2 className="text-lg font-bold text-white mb-1">Admin Panel</h2>
              <p className="text-zinc-400 text-sm mb-4">
                Register and anchor authentic documents on the blockchain.
              </p>
              <div className="flex items-center gap-2 text-violet-400 text-sm font-semibold mt-auto group-hover:gap-3 transition-all">
                Enter as Admin <ArrowRight className="w-4 h-4" />
              </div>
            </Link>
          </div>
        </section>

        {/* ─── FEATURES ─── */}
        <section className="w-full max-w-6xl mx-auto px-6 pb-24">
          <p className="text-center text-xs uppercase tracking-widest text-zinc-500 font-mono mb-10">
            How It Works
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: Brain,
                color: "cyan" as const,
                title: "AI Detection",
                desc: "A multi-modal ML pipeline analyzes visual, textual, and frequency-domain features to detect tampered regions with pixel-level precision.",
              },
              {
                icon: Shield,
                color: "emerald" as const,
                title: "Blockchain Anchoring",
                desc: "Document hashes are stored on an Ethereum blockchain at registration time, creating an immutable ground-truth record.",
              },
              {
                icon: FileSearch,
                color: "violet" as const,
                title: "Cross-Verification",
                desc: "The AI confidence score is combined with the blockchain verification result for a definitive authenticity verdict.",
              },
            ].map(({ icon: Icon, color, title, desc }) => {
              const colors = {
                cyan: { border: "border-cyan-500/20", bg: "bg-cyan-500/10", iconColor: "text-cyan-400" },
                emerald: { border: "border-emerald-500/20", bg: "bg-emerald-500/10", iconColor: "text-emerald-400" },
                violet: { border: "border-violet-500/20", bg: "bg-violet-500/10", iconColor: "text-violet-400" },
              }[color];
              return (
                <div key={title} className="p-6 rounded-2xl border border-zinc-800 bg-zinc-900/40">
                  <div className={`w-10 h-10 rounded-lg ${colors.bg} border ${colors.border} flex items-center justify-center mb-4`}>
                    <Icon className={`w-5 h-5 ${colors.iconColor}`} />
                  </div>
                  <h3 className="font-bold text-white mb-2">{title}</h3>
                  <p className="text-zinc-400 text-sm leading-relaxed">{desc}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* ─── FOOTER ─── */}
        <footer className="w-full border-t border-zinc-800 py-8 text-center">
          <p className="text-zinc-600 text-sm font-mono">
            BITS Document Forensics · v2.1.0 · LIVE_ML_PIPELINE // NETWORK: LOCAL_GANACHE
          </p>
        </footer>
      </div>
    </main>
  );
}
