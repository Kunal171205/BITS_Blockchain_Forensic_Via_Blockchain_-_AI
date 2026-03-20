"use client";

import React from "react";
import { ShieldAlert, ShieldCheck, Activity, Eye, BarChart3 } from "lucide-react";

interface DetailScores {
  visual_score: number;
  text_score: number;
  layout_score: number;
  dct_score: number;
  font_score: number;
}

interface AnalysisViewProps {
  file: File | null;
  isAnalyzing: boolean;
  isAnalyzed: boolean;
  blockchainStatus: "PENDING" | "VERIFIED" | "UNVERIFIED" | "ERROR";
  aiScore: number;
  maskImageUrl?: string;
  originalImageUrl?: string;
  detailScores?: DetailScores | null;
  modelLoaded?: boolean;
}

export function AnalysisView({
  file,
  isAnalyzing,
  isAnalyzed,
  blockchainStatus,
  aiScore,
  maskImageUrl,
  originalImageUrl,
  detailScores,
  modelLoaded,
}: AnalysisViewProps) {
  if (!file && !isAnalyzing && !isAnalyzed) {
    return (
      <div className="h-full flex items-center justify-center text-zinc-600 border border-zinc-800 rounded-xl bg-zinc-900/20 px-8 py-16">
        <p className="font-mono text-sm tracking-widest uppercase">Waiting for document ingest...</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* Top Left: Original Image (Bento Box) */}
      <div className="border border-zinc-800 rounded-2xl bg-zinc-950/80 backdrop-blur-xl p-5 flex flex-col h-[380px] hover:border-zinc-700 transition-colors">
        <h3 className="text-[10px] uppercase tracking-widest text-zinc-500 mb-3 font-semibold flex items-center justify-between">
          <span className="flex items-center"><Eye className="w-3.5 h-3.5 mr-2" /> Original Source</span>
        </h3>
        <div className="flex-1 bg-black rounded-xl border border-zinc-800/50 overflow-hidden flex items-center justify-center">
          {isAnalyzing ? (
            <div className="w-full h-full bg-cyan-900/10 animate-pulse flex items-center justify-center">
              <span className="font-mono text-cyan-500/50 text-xs">ANALYZING...</span>
            </div>
          ) : isAnalyzed && originalImageUrl ? (
            <img src={originalImageUrl} alt="Original" className="max-w-full max-h-full object-contain" />
          ) : (
            <span className="text-zinc-700 font-mono text-xs">AWAITING INPUT</span>
          )}
        </div>
      </div>

      {/* Top Right: AI Mask (Bento Box) */}
      <div className="border border-zinc-800 rounded-2xl bg-zinc-950/80 backdrop-blur-xl p-5 flex flex-col h-[380px] hover:border-zinc-700 transition-colors relative overflow-hidden">
        {/* Subtle gradient glow behind the mask box based on score */}
        {isAnalyzed && (
          <div className={`absolute -top-24 -right-24 w-48 h-48 rounded-full blur-3xl opacity-20 pointer-events-none transition-colors duration-1000 ${aiScore > 75 ? 'bg-rose-500' : 'bg-emerald-500'}`} />
        )}
        
        <h3 className="text-[10px] uppercase tracking-widest text-zinc-500 mb-3 font-semibold flex items-center justify-between relative z-10">
          <span className="flex items-center"><Eye className="w-3.5 h-3.5 mr-2" /> Forensic Mask</span>
          {modelLoaded !== undefined && (
            <span className={`text-[9px] px-1.5 py-0.5 rounded-full ${modelLoaded ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
              {modelLoaded ? 'ACTIVE' : 'OFFLINE'}
            </span>
          )}
        </h3>
        <div className="flex-1 bg-black rounded-xl border border-zinc-800/50 overflow-hidden flex items-center justify-center relative z-10">
          {isAnalyzing ? (
            <div className="w-full h-full bg-cyan-900/10 animate-pulse flex items-center justify-center">
              <span className="font-mono text-cyan-500/50 text-xs">GENERATING MASK...</span>
            </div>
          ) : isAnalyzed && maskImageUrl ? (
            <img src={maskImageUrl} alt="Mask" className="max-w-full max-h-full object-contain" />
          ) : (
            <span className="text-zinc-700 font-mono text-xs">NO MASK</span>
          )}
        </div>
      </div>

      {/* Bottom Left: Detail Scores (Bento Box) */}
      <div className="border border-zinc-800 rounded-2xl bg-zinc-950/80 backdrop-blur-xl p-5 hover:border-zinc-700 transition-colors flex flex-col">
        <h3 className="text-[10px] uppercase tracking-widest text-zinc-500 mb-4 font-semibold flex items-center">
          <BarChart3 className="w-3.5 h-3.5 mr-2" />
          Model Breakdown
        </h3>

        {isAnalyzing ? (
          <div className="flex-1 flex items-center justify-center">
            <span className="text-cyan-500/50 font-mono text-xs animate-pulse">ANALYZING ENGINE...</span>
          </div>
        ) : isAnalyzed && detailScores ? (
          <div className="space-y-3.5 mt-auto mb-auto">
            {[
              { label: "Visual (UNet)", value: detailScores.visual_score, color: "cyan" },
              { label: "Text Anomaly", value: detailScores.text_score, color: "amber" },
              { label: "DCT Analysis", value: detailScores.dct_score, color: "rose" },
              { label: "Font Anomaly", value: detailScores.font_score, color: "violet" },
              { label: "Layout Score", value: detailScores.layout_score, color: "emerald" },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between group">
                <span className="text-[11px] text-zinc-400 font-mono w-28 group-hover:text-zinc-300 transition-colors">{item.label}</span>
                <div className="flex-1 mx-3 h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-1000 ease-out`}
                    style={{ 
                      width: `${Math.min(item.value * 100, 100)}%`, 
                      backgroundColor: item.color === 'cyan' ? '#06b6d4' : item.color === 'amber' ? '#f59e0b' : item.color === 'rose' ? '#f43f5e' : item.color === 'violet' ? '#8b5cf6' : '#10b981',
                      boxShadow: `0 0 10px ${item.color === 'cyan' ? '#06b6d4' : item.color === 'amber' ? '#f59e0b' : item.color === 'rose' ? '#f43f5e' : item.color === 'violet' ? '#8b5cf6' : '#10b981'}40`
                    }}
                  />
                </div>
                <span className="text-[11px] text-zinc-300 font-mono w-10 text-right">
                  {Math.min(item.value * 100, 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <span className="text-zinc-700 font-mono text-xs">MODEL INACTIVE</span>
          </div>
        )}
      </div>

      {/* Bottom Right: Ledger Status & Overall Score (Bento Box) */}
      <div className="border border-zinc-800 rounded-2xl bg-zinc-950/80 backdrop-blur-xl p-5 hover:border-zinc-700 transition-colors flex flex-col justify-between relative overflow-hidden">
        
        <div>
          <h3 className="text-[10px] uppercase tracking-widest text-zinc-500 mb-4 font-semibold flex items-center">
            <Activity className="w-3.5 h-3.5 mr-2" />
            Ledger Integrity (Ganache)
          </h3>

          <div className="mt-2">
            {blockchainStatus === "PENDING" && (
              <div className="flex items-center text-amber-500/70 p-3 rounded-xl border border-amber-900/30 bg-amber-950/20">
                <Activity className="w-4 h-4 mr-3 animate-pulse" />
                <span className="font-mono text-xs tracking-wider">QUERYING CHAIN...</span>
              </div>
            )}
            {blockchainStatus === "VERIFIED" && (
              <div className="flex items-center text-emerald-400 bg-emerald-500/10 p-4 rounded-xl border border-emerald-500/20 relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/0 via-emerald-500/5 to-emerald-500/0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
                <ShieldCheck className="w-5 h-5 mr-3 flex-shrink-0" />
                <div>
                  <span className="block font-mono font-bold text-sm tracking-wider">AUTHORIZED</span>
                  <span className="block text-[10px] opacity-70 mt-0.5 leading-tight">Hash matches admin registry on-chain</span>
                </div>
              </div>
            )}
            {blockchainStatus === "UNVERIFIED" && (
              <div className="flex items-center text-rose-400 bg-rose-500/10 p-4 rounded-xl border border-rose-500/20">
                <ShieldAlert className="w-5 h-5 mr-3 flex-shrink-0" />
                <div>
                  <span className="block font-mono font-bold text-sm tracking-wider">NOT AUTHORIZED</span>
                  <span className="block text-[10px] opacity-70 mt-0.5 leading-tight">Hash not found in blockchain registry</span>
                </div>
              </div>
            )}
            {blockchainStatus === "ERROR" && (
              <div className="text-red-500/80 text-xs font-mono p-3 rounded-xl border border-red-900/30 bg-red-950/20">RPC ERROR: Node Disconnected</div>
            )}
          </div>
        </div>

        {/* Overall Score */}
        <div className="mt-6 p-4 bg-black rounded-xl border border-zinc-800/50 relative overflow-hidden">
           {isAnalyzed && (
            <div className={`absolute -bottom-10 -right-10 w-32 h-32 rounded-full blur-2xl opacity-20 pointer-events-none transition-colors duration-1000 ${aiScore > 75 ? 'bg-rose-500' : 'bg-emerald-500'}`} />
          )}
          <h4 className="text-[10px] text-zinc-500 mb-1 font-mono uppercase tracking-widest">Forgery Probability</h4>
          <div className="flex items-end justify-between relative z-10">
            <span className={`text-4xl font-mono tracking-tighter ${!isAnalyzed ? 'text-zinc-700' : aiScore > 75 ? 'text-rose-400 drop-shadow-[0_0_10px_rgba(244,63,94,0.4)]' : 'text-emerald-400 drop-shadow-[0_0_10px_rgba(16,185,129,0.4)]'}`}>
              {isAnalyzed ? Math.min(aiScore, 100).toFixed(1) : "--"}%
            </span>
            <span className="text-[10px] text-zinc-600 font-mono mb-1 translate-y-[-4px]">THRESHOLD: 75%</span>
          </div>
        </div>

      </div>
    </div>
  );
}
