"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FileUploader } from "@/components/FileUploader";
import { AnalysisView } from "@/components/AnalysisView";
import { DecisionEngine } from "@/components/DecisionEngine";
import { LogOut } from "lucide-react";
import { getAuthData } from "@/lib/client-auth";

const API_URL = "http://127.0.0.1:5000";
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

export default function DashboardPage() {
  const router = useRouter();
  const [userName, setUserName] = useState("");
  const [userRole, setUserRole] = useState("");
  const [rpcUrl, setRpcUrl] = useState("http://localhost:7545");
  const [contractAddress, setContractAddress] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAnalyzed, setIsAnalyzed] = useState(false);

  const [aiScore, setAiScore] = useState(0);
  const [isTampered, setIsTampered] = useState(false);
  const [detailScores, setDetailScores] = useState<DetailScores | null>(null);
  const [maskImageUrl, setMaskImageUrl] = useState<string>("");
  const [originalImageUrl, setOriginalImageUrl] = useState<string>("");
  const [modelLoaded, setModelLoaded] = useState(false);
  const [bcStatus, setBcStatus] = useState<"PENDING" | "VERIFIED" | "UNVERIFIED" | "ERROR">("PENDING");
  const [bcError, setBcError] = useState("");

  // Read user name from a quick /api/auth/me endpoint or from cookie (parsed client-side)
  useEffect(() => {
    const authData = getAuthData();
    if (authData) {
      setUserName(authData.name);
      setUserRole(authData.role);
    }

    // Check model status and blockchain config from API
    const checkModelStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/api/health`);
        const data = await res.json();
        if (data.model_loaded !== undefined) {
          setModelLoaded(data.model_loaded);
        }
        if (data.blockchain) {
          console.log("[DASHBOARD] Received blockchain config:", data.blockchain);
          setRpcUrl(data.blockchain.rpc_url || "http://127.0.0.1:7545");
          setContractAddress(data.blockchain.contract_address || "");
        }
      } catch (err) {
        console.error("[DASHBOARD] Failed to check status:", err);
      }
    };
    checkModelStatus();
  }, []);

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/");
  };

  const handleFileUpload = async (uploadedFile: File) => {
    setFile(uploadedFile);
    setIsAnalyzing(true);
    setIsAnalyzed(false);
    setBcStatus("PENDING");
    setBcError("");
    setMaskImageUrl("");
    setOriginalImageUrl("");

    try {
      const formData = new FormData();
      formData.append("file", uploadedFile);

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`API error: ${response.statusText}`);

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      setAiScore(data.confidence_score || 0);
      setIsTampered(data.is_tampered || false);
      setDetailScores(data.details || null);
      setModelLoaded(data.model_loaded || false);

      if (data.mask_image) setMaskImageUrl(`data:image/png;base64,${data.mask_image}`);
      if (data.original_image) setOriginalImageUrl(`data:image/png;base64,${data.original_image}`);
    } catch (err) {
      console.error("ML API Error:", err);
      setAiScore(0);
      setIsTampered(false);
    }

    setIsAnalyzing(false);
    setIsAnalyzed(true);

    // Lazy-load ethers only at the point of use — keeps initial bundle small
    try {
      if (!contractAddress) throw new Error("Contract address not configured");
      const { ethers } = await import("ethers");
      const arrayBuffer = await uploadedFile.arrayBuffer();
      const hashBuffer = await crypto.subtle.digest("SHA-256", arrayBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
      const bytes32Hash = "0x" + hashHex;

      console.log(`[DASHBOARD] Connecting to RPC: ${rpcUrl} for contract: ${contractAddress}`);
      const provider = new ethers.JsonRpcProvider(rpcUrl);
      const contract = new ethers.Contract(contractAddress, CONTRACT_ABI, provider);
      const [timestamp] = await contract.verifyDocument(bytes32Hash);
      setBcStatus(timestamp > 0n ? "VERIFIED" : "UNVERIFIED");
    } catch (err: any) {
      console.error("[DASHBOARD] Blockchain Connection Error:", err);
      setBcStatus("ERROR");
      setBcError(err.message || "Unknown error");
    }
  };

  return (
    <main className="min-h-screen bg-[#09090b] text-zinc-100 p-8 flex flex-col items-center">
      <div className="w-full max-w-6xl space-y-8">
        <header className="border-b border-zinc-800 pb-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-black tracking-tighter flex items-center">
                <span className="text-cyan-500 mr-3">⬡</span> DOCUMENT FORENSICS
              </h1>
              <p className="text-zinc-500 font-mono text-sm mt-2">
                v2.1.0 - LIVE_ML_PIPELINE // NETWORK: LOCAL_GANACHE
                {userName && (
                  <span className="ml-3 text-cyan-600">· {userName}</span>
                )}
              </p>
            </div>
            <div className="flex items-center gap-3">
              {userRole === "admin" && (
                <Link
                  href="/admin"
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-all text-zinc-400 hover:text-zinc-200 text-sm"
                >
                  <span>Admin Panel</span>
                </Link>
              )}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-zinc-900 hover:bg-red-900/30 border border-zinc-800 hover:border-red-800 transition-all text-zinc-400 hover:text-red-400 text-sm"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 space-y-6 flex flex-col">
            <div className="flex-1">
              <FileUploader onFileUpload={handleFileUpload} />
            </div>
            <DecisionEngine
              confidence={aiScore}
              isTampered={isTampered}
              isAnalyzed={isAnalyzed}
              blockchainStatus={bcStatus}
              blockchainError={bcError}
            />
          </div>
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
