"use client";

import React, { useState } from "react";
import Link from "next/link";
import { FileUploader } from "@/components/FileUploader";
import { AnalysisView } from "@/components/AnalysisView";
import { DecisionEngine } from "@/components/DecisionEngine";
import { ethers } from "ethers";
import { Settings } from "lucide-react";

const API_URL = "http://localhost:5000";
const RPC_URL = "http://127.0.0.1:7545";
const CONTRACT_ADDRESS = "0x5b1869D9A4C187F2EAa108f3062412ecf0526b24";
const CONTRACT_ABI = [
  "function verifyDocument(bytes32 docHash) view returns (uint256 timestamp, address issuerAddress, bool isAuthentic)"
];

interface DetailScores {
  visual_score: number;
  text_score: number;
  layout_score: number;
  dct_score: number;
  font_score: number;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAnalyzed, setIsAnalyzed] = useState(false);

  // Real ML Data
  const [aiScore, setAiScore] = useState(0);
  const [isTampered, setIsTampered] = useState(false);
  const [detailScores, setDetailScores] = useState<DetailScores | null>(null);
  const [maskImageUrl, setMaskImageUrl] = useState<string>("");
  const [originalImageUrl, setOriginalImageUrl] = useState<string>("");
  const [modelLoaded, setModelLoaded] = useState(false);

  // Blockchain State
  const [bcStatus, setBcStatus] = useState<"PENDING" | "VERIFIED" | "UNVERIFIED" | "ERROR">("PENDING");

  const handleFileUpload = async (uploadedFile: File) => {
    setFile(uploadedFile);
    setIsAnalyzing(true);
    setIsAnalyzed(false);
    setBcStatus("PENDING");
    setMaskImageUrl("");
    setOriginalImageUrl("");

    try {
      // 1. Call real ML API
      const formData = new FormData();
      formData.append("file", uploadedFile);

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      // Set real ML results
      setAiScore(data.confidence_score || 0);
      setIsTampered(data.is_tampered || false);
      setDetailScores(data.details || null);
      setModelLoaded(data.model_loaded || false);

      // Set images
      if (data.mask_image) {
        setMaskImageUrl(`data:image/png;base64,${data.mask_image}`);
      }
      if (data.original_image) {
        setOriginalImageUrl(`data:image/png;base64,${data.original_image}`);
      }

    } catch (err) {
      console.error("ML API Error:", err);
      // Fallback: show error state
      setAiScore(0);
      setIsTampered(false);
    }

    setIsAnalyzing(false);
    setIsAnalyzed(true);

    // 2. Cross-check Blockchain via ethers.js
    try {
      const arrayBuffer = await uploadedFile.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest("SHA-256", arrayBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
      const bytes32Hash = "0x" + hashHex;

      const provider = new ethers.JsonRpcProvider(RPC_URL);
      const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);

      console.log("Checking hash on Ganache:", bytes32Hash);
      const [timestamp] = await contract.verifyDocument(bytes32Hash);

      if (timestamp > 0n) {
        setBcStatus("VERIFIED");
      } else {
        setBcStatus("UNVERIFIED");
      }
    } catch (err) {
      console.error("Blockchain Connection Error:", err);
      setBcStatus("ERROR");
    }
  };

  return (
    <main className="min-h-screen bg-[#09090b] text-zinc-100 p-8 flex flex-col items-center">
      <div className="w-full max-w-6xl space-y-8">

        {/* Header */}
        <header className="border-b border-zinc-800 pb-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-black tracking-tighter flex items-center">
                <span className="text-cyan-500 mr-3">⬡</span> DOCUMENT FORENSICS
              </h1>
              <p className="text-zinc-500 font-mono text-sm mt-2">v2.1.0 - LIVE_ML_PIPELINE // NETWORK: LOCAL_GANACHE</p>
            </div>
            <Link
              href="/admin"
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-all text-zinc-400 hover:text-zinc-200 text-sm"
            >
              <Settings className="w-4 h-4" />
              <span>Admin Panel</span>
            </Link>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Input & Decision */}
          <div className="lg:col-span-1 space-y-6 flex flex-col">
            <div className="flex-1">
              <FileUploader onFileUpload={handleFileUpload} />
            </div>

            <DecisionEngine
              confidence={aiScore}
              isTampered={isTampered}
              isAnalyzed={isAnalyzed}
            />
          </div>

          {/* Right Column: Visualization & Ledger */}
          <div className="lg:col-span-2">
            <AnalysisView
              file={file}
              isAnalyzing={isAnalyzing}
              isAnalyzed={isAnalyzed}
              blockchainStatus={bcStatus}
              aiScore={aiScore}
              maskImageUrl={maskImageUrl}
              originalImageUrl={originalImageUrl}
              detailScores={detailScores}
              modelLoaded={modelLoaded}
            />
          </div>
        </div>

      </div>
    </main>
  );
}
