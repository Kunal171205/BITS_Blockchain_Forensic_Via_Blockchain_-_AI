"use client";

import React, { useState, useEffect, useCallback } from "react";
import { AdminUploader } from "@/components/AdminUploader";
import { DocumentRegistry } from "@/components/DocumentRegistry";
import { Shield, ArrowLeft, LogOut } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getAuthData } from "@/lib/client-auth";

const API_URL = "http://127.0.0.1:5000";
// Future-proofing: dynamic config could be added here similar to dashboard

interface DocumentEntry {
  filename: string;
  hash: string;
  tx_hash: string;
  block_number: number;
  timestamp: string;
}

export default function AdminPage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<DocumentEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [userName, setUserName] = useState("");

  const fetchDocuments = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/documents`);
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error("Failed to fetch documents:", err);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    fetchDocuments();
    const authData = getAuthData();
    if (authData) {
      setUserName(authData.name);
    }
  }, [fetchDocuments]);

  const handleUploadSuccess = () => {
    fetchDocuments();
  };

  const handleLogout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/");
  };

  return (
    <main className="min-h-screen bg-[#09090b] text-zinc-100 p-8 flex flex-col items-center">
      <div className="w-full max-w-5xl space-y-8">

        {/* Header */}
        <header className="border-b border-zinc-800 pb-6 mb-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-black tracking-tighter flex items-center">
                <span className="text-violet-500 mr-3">⬡</span> ADMIN PANEL
              </h1>
              <p className="text-zinc-500 font-mono text-sm mt-2">
                Document Registration &amp; Blockchain Anchoring
                {userName && (
                  <span className="ml-3 text-violet-400">· {userName}</span>
                )}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/dashboard"
                className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-all text-zinc-400 hover:text-zinc-200 text-sm"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Analysis View</span>
              </Link>
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

        {/* Upload Section */}
        <section>
          <h2 className="text-xs uppercase tracking-widest text-zinc-500 mb-4 font-semibold flex items-center">
            <Shield className="w-4 h-4 mr-2 text-violet-500" />
            Register New Document
          </h2>
          <AdminUploader onUploadSuccess={handleUploadSuccess} />
        </section>

        {/* Registry Section */}
        <section>
          <h2 className="text-xs uppercase tracking-widest text-zinc-500 mb-4 font-semibold flex items-center">
            <Shield className="w-4 h-4 mr-2 text-emerald-500" />
            Document Registry
            <span className="ml-3 text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">
              {documents.length} ON-CHAIN
            </span>
          </h2>
          <DocumentRegistry documents={documents} isLoading={isLoading} />
        </section>

      </div>
    </main>
  );
}
