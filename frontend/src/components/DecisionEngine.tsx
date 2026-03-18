"use client";

import React from "react";
import { CheckCircle, AlertTriangle, XOctagon } from "lucide-react";

interface DecisionEngineProps {
  confidence: number;
  isTampered: boolean;
  isAnalyzed: boolean;
}

export function DecisionEngine({ confidence, isTampered, isAnalyzed }: DecisionEngineProps) {
  if (!isAnalyzed) return null;

  // Decision Logic mimicking Blue Team rules
  let decision = "APPROVE";
  let colorClass = "text-emerald-500 border-emerald-500/20 bg-emerald-500/10";
  let Icon = CheckCircle;

  if (isTampered || confidence > 80) {
    decision = "REJECT";
    colorClass = "text-rose-500 border-rose-500/20 bg-rose-500/10";
    Icon = XOctagon;
  } else if (confidence > 40 && confidence <= 80) {
    decision = "ESCALATE";
    colorClass = "text-amber-500 border-amber-500/20 bg-amber-500/10";
    Icon = AlertTriangle;
  }

  return (
    <div className={`mt-4 p-5 rounded-2xl border backdrop-blur-xl transition-colors h-[120px] flex items-center justify-between ${colorClass}`}>
      <div className="flex items-center space-x-4">
        <Icon className="w-8 h-8 opacity-80" />
        <div>
          <h3 className="text-[10px] uppercase tracking-widest opacity-70 mb-1">System Decision</h3>
          <p className="text-xl font-black tracking-wider">{decision}</p>
        </div>
      </div>
      <div className="text-right flex flex-col items-end">
        <p className="text-[10px] opacity-70 mb-1 uppercase tracking-widest">Confidence</p>
        <p className="font-mono text-2xl tracking-tighter">{confidence.toFixed(1)}%</p>
      </div>
    </div>
  );
}
