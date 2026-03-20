"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, File as FileIcon } from "lucide-react";

interface FileUploaderProps {
  onFileUpload: (file: File) => void;
}

export function FileUploader({ onFileUpload }: FileUploaderProps) {
  const [activeFile, setActiveFile] = useState<File | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        setActiveFile(acceptedFiles[0]);
        onFileUpload(acceptedFiles[0]);
      }
    },
    [onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".png", ".jpg", ".jpeg"], "application/pdf": [".pdf"] },
    maxFiles: 1,
  });

  return (
    <div className="w-full h-full min-h-[400px] border border-dashed border-zinc-700/50 bg-zinc-950/40 hover:bg-zinc-900/40 hover:border-zinc-500/50 transition-all rounded-2xl flex flex-col items-center justify-center p-6 text-zinc-400 group">
      <div
        {...getRootProps()}
        className="w-full h-full flex flex-col items-center justify-center cursor-pointer"
      >
        <input {...getInputProps()} />
        {activeFile ? (
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="p-4 bg-cyan-950/30 rounded-full border border-cyan-900/50 group-hover:bg-cyan-900/30 transition-colors">
               <FileIcon className="w-10 h-10 text-cyan-400" />
            </div>
            <div>
              <p className="font-mono text-cyan-400 text-sm mb-1 max-w-[200px] truncate px-4">{activeFile.name}</p>
              <p className="text-[10px] text-zinc-500 font-mono">{(activeFile.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <span className="text-[10px] mt-4 uppercase tracking-widest border border-zinc-800 px-3 py-1 rounded-full bg-zinc-900/80">Click to replace</span>
          </div>
        ) : (
          <div className="flex flex-col items-center space-y-4">
            <div className={`p-4 rounded-full border transition-all duration-300 ${isDragActive ? "bg-cyan-950/40 border-cyan-500/50" : "bg-black border-zinc-800 group-hover:border-zinc-700 group-hover:bg-zinc-900/50"}`}>
               <UploadCloud className={`w-8 h-8 transition-colors ${isDragActive ? "text-cyan-400" : "text-zinc-500"}`} />
            </div>
            <p className="text-center text-sm px-4">
              {isDragActive
                ? <span className="text-cyan-400 font-medium">Drop document here</span>
                : <span>Drag & drop document here<br/><span className="text-xs text-zinc-500 mt-1 block">or click to browse</span></span>}
            </p>
            <span className="text-[9px] text-zinc-600 uppercase tracking-widest mt-6 bg-zinc-900/50 px-3 py-1 rounded-lg border border-zinc-800">
              PNG, JPG, PDF (Max 10MB)
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
