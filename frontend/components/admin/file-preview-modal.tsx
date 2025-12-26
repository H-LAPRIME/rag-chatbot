"use client"

import { X, FileText, Calendar, HardDrive, CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { API_URL } from "@/lib/utils"
interface FileItem {
  id: string
  name: string
  type: string
  size: string
  uploadedAt: string
  status: "indexed" | "pending" | "error"
}

interface FilePreviewModalProps {
  file: FileItem | null
  onClose: () => void
}

export function FilePreviewModal({ file, onClose }: FilePreviewModalProps) {
  if (!file) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-card rounded-2xl shadow-2xl max-w-lg w-full mx-4 border border-border overflow-hidden animate-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="bg-primary/5 border-b border-border px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">File Preview</h3>
              <p className="text-xs text-muted-foreground">Document details</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* File name */}
          <div className="mb-6">
            <p className="text-lg font-medium text-foreground break-all">{file.name}</p>
            <Badge variant="outline" className="mt-2 font-mono">
              {file.type}
            </Badge>
          </div>

          {/* Details grid */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-muted/50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <HardDrive className="h-4 w-4" />
                <span className="text-xs uppercase tracking-wide">Size</span>
              </div>
              <p className="text-sm font-medium text-foreground">{file.size}</p>
            </div>
            <div className="bg-muted/50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Calendar className="h-4 w-4" />
                <span className="text-xs uppercase tracking-wide">Uploaded</span>
              </div>
              <p className="text-sm font-medium text-foreground">{file.uploadedAt}</p>
            </div>
          </div>

          {/* Status */}
          <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-4 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-green-700">Indexed & Ready</p>
              <p className="text-xs text-green-600/80">This document is searchable by the chatbot</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-muted/30 border-t border-border px-6 py-4 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button
            onClick={() => {
              window.open(
                `${API_URL}/api/files/${file.name}/download`,
                "_blank"
              )
            }}
            className="bg-primary hover:bg-primary/90 cursor-pointer">Download</Button>
        </div>
      </div>
    </div>
  )
}
