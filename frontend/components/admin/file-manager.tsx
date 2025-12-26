"use client"

import type React from "react"

import { useState, useCallback, useRef, useEffect } from "react"
import { Upload, FileText, Trash2, Eye, Search, Filter, FolderOpen, Plus, CheckSquare, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { IndexingOverlay } from "./indexing-overlay"
import { FilePreviewModal } from "./file-preview-modal"
import axios from "axios"
import { API_URL } from "@/lib/utils"
import { toast } from "sonner"

interface FileItem {
  id: string
  name: string
  type: string
  size: string
  uploadedAt: string
  status: "indexed" | "pending" | "error"
}

const initialFiles: FileItem[] = []

export function FileManager() {
  const [files, setFiles] = useState<FileItem[]>(initialFiles)
  const [searchQuery, setSearchQuery] = useState("")
  const [isIndexing, setIsIndexing] = useState(false)
  const [indexingMessage, setIndexingMessage] = useState("")
  const [indexingTitle, setIndexingTitle] = useState("")
  const [indexingProg, setIndexingProg] = useState("")
  const [indexingType, setIndexingType] = useState<"upload" | "delete" | "update">("upload")
  const [selectedFile, setSelectedFile] = useState<FileItem | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const fileInputRef = useRef<HTMLInputElement>(null)

  const filteredFiles = files.filter((file) => file.name.toLowerCase().includes(searchQuery.toLowerCase()))

  const bringFiles = useCallback(async () => {
    try {
      const res = await axios.get(`${API_URL}/api/files`);
      const data = res.data;
      setFiles(data);
    } catch (err) {

    }
  }, [])



  useEffect(() => {
    bringFiles();
  }, [])


  const toggleSelectAll = () => {
    if (selectedIds.size === filteredFiles.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(filteredFiles.map((f) => f.id)))
    }
  }

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedIds(newSelected)
  }




  // const fileCount = selectedFiles.length
  // const newFiles: FileItem[] = Array.from(selectedFiles).map((file, index) => ({
  //   id: `${Date.now()}-${index}`,
  //   name: file.name,
  //   type: file.name.split(".").pop()?.toUpperCase() || "FILE",
  //   size: formatFileSize(file.size),
  //   uploadedAt: new Date().toISOString().split("T")[0],
  //   status: "pending" as const,
  // }))

  // setFiles((prev) => [...newFiles, ...prev])
  // startIndexing("upload", `Indexing ${fileCount} file${fileCount > 1 ? "s" : ""}...`, {
  //   current: 0,
  //   total: fileCount,
  // })

  // Simulate indexing completion
  // setTimeout(() => {
  //   setFiles((prev) =>
  //     prev.map((f) => (newFiles.some((nf) => nf.id === f.id) ? { ...f, status: "indexed" as const } : f)),
  //   )
  //   setIsIndexing(false)
  //   setIndexingCount({ current: 0, total: 0 })
  // }, 4000)

  // Reset file input
  //   if (fileInputRef.current) fileInputRef.current.value = ""
  // }

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files
    if (!selectedFiles || selectedFiles.length === 0) return
    const formData = new FormData()

    Array.from(selectedFiles).forEach(file => {
      formData.append("files", file)
    })

    try {
      setIsIndexing(true);
      setIndexingTitle("Feeding New Files")
      setIndexingMessage("Wait until the building process finish")
      setIndexingProg("Uploading / indexing files is in progress");
      const res = await axios.post(`${API_URL}/api/files`, formData);
      bringFiles()
    } catch (err) {
      console.log(err);  // ERROR HANDLING HERE
    }

    setIsIndexing(false)
    // Reset file input
    if (fileInputRef.current) fileInputRef.current.value = ""
  }

  const handleUpload = () => {
    fileInputRef.current?.click()
  }

  const handleDeleteSelected = async () => {
    if (selectedIds.size === 0) return
    setIsIndexing(true)
    setIndexingTitle("Deleting file")
    setIndexingMessage("We are deleting your selected files")
    setIndexingProg("Deleting and Building is in progress")

    for (const id of selectedIds) {
      const deletedFile = files.find(file => file.id === id)
      if (!deletedFile) continue

      try {
        await axios.delete(`${API_URL}/api/files/${deletedFile.name}`)
      } catch (err) {
        console.log(err)
      }
    }
    bringFiles();
    setIsIndexing(false);
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFiles = e.dataTransfer.files
    if (!droppedFiles || droppedFiles.length === 0) return

    const formData = new FormData()

    Array.from(droppedFiles).forEach(file => {
      formData.append("files", file)
    })

    try {
      setIsIndexing(true);
      setIndexingTitle("Feeding New Files")
      setIndexingMessage("Wait until the building process finish")
      setIndexingProg("Uploading / indexing files is in progress");
      const res = await axios.post(`${API_URL}/api/files`, formData);
      bringFiles()
    } catch (err) {
      console.log(err);  // ERROR HANDLING HERE
    }
    setIsIndexing(false)
  }, [])

  const getStatusBadge = (status: FileItem["status"]) => {
    switch (status) {
      case "indexed":
        return (
          <Badge className="bg-green-500/10 text-green-600 border-green-500/30 hover:bg-green-500/20">Indexed</Badge>
        )
      case "pending":
        return (
          <Badge className="bg-amber-500/10 text-amber-600 border-amber-500/30 hover:bg-amber-500/20">Pending</Badge>
        )
      case "error":
        return <Badge variant="destructive">Error</Badge>
    }
  }

  const allSelected = filteredFiles.length > 0 && selectedIds.size === filteredFiles.length

  return (
    <>
      {/* Hidden file input for multiple file selection */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.docx,.doc,.txt"
        className="hidden"
        onChange={handleFileSelect}
      />

      <Card className="border-0 shadow-xl overflow-hidden">
        <CardHeader className="bg-card border-b border-border pb-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <FolderOpen className="h-5 w-5 text-primary" />
              </div>
              <div>
                <CardTitle className="text-lg md:text-xl text-foreground">Knowledge Base Files</CardTitle>
                <p className="text-sm text-muted-foreground mt-0.5">
                  {files.length} documents | {files.filter((f) => f.status === "indexed").length} indexed
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="relative flex-1 md:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 bg-muted/50 border-border"
                />
              </div>
              <Button variant="outline" size="icon" className="shrink-0 bg-transparent">
                <Filter className="h-4 w-4" />
              </Button>
              <Button onClick={handleUpload} className="bg-primary hover:bg-primary/90 shrink-0">
                <Plus className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Upload Files</span>
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-0">
          {selectedIds.size > 0 && (
            <div className="mx-4 md:mx-6 mt-4 p-3 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CheckSquare className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium text-foreground">
                  {selectedIds.size} file{selectedIds.size > 1 ? "s" : ""} selected
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedIds(new Set())}
                  className="text-muted-foreground"
                >
                  <X className="h-4 w-4 mr-1" />
                  Clear
                </Button>
                <Button variant="destructive" size="sm" onClick={handleDeleteSelected}>
                  <Trash2 className="h-4 w-4 mr-1" />
                  Delete Selected
                </Button>
              </div>
            </div>
          )}

          <div className="px-4 md:px-6 pt-4">
            <div className="bg-muted/50 rounded-xl overflow-hidden">
              {/* Table header */}
              <div className="hidden md:grid md:grid-cols-12 gap-4 px-4 py-3 bg-muted/80 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                <div className="col-span-1 flex items-center">
                  <Checkbox
                    checked={allSelected}
                    onCheckedChange={toggleSelectAll}
                    className="border-muted-foreground/50"
                  />
                </div>
                <div className="col-span-4">File Name</div>
                <div className="col-span-2">Type</div>
                <div className="col-span-2">Size</div>
                <div className="col-span-2">Status</div>
                <div className="col-span-1">Actions</div>
              </div>

              <div className="divide-y divide-border max-h-[400px] overflow-y-auto">
                {filteredFiles.map((file) => (
                  <div
                    key={file.id}
                    className={`grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 px-4 py-4 hover:bg-muted/40 transition-colors group ${selectedIds.has(file.id) ? "bg-primary/5" : ""
                      }`}
                  >
                    <div className="hidden md:flex md:col-span-1 items-center">
                      <Checkbox
                        checked={selectedIds.has(file.id)}
                        onCheckedChange={() => toggleSelect(file.id)}
                        className="border-muted-foreground/50 cursor-pointer"
                      />
                    </div>

                    <div className="md:col-span-4 flex items-center gap-3">
                      {/* Mobile checkbox */}
                      <Checkbox
                        checked={selectedIds.has(file.id)}
                        onCheckedChange={() => toggleSelect(file.id)}
                        className="md:hidden cursor-pointer border-muted-foreground/50"
                      />
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                        <FileText className="h-5 w-5 text-primary" />
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-sm text-foreground truncate">{file.name}</p>
                        <p className="text-xs text-muted-foreground md:hidden">
                          {file.type} | {file.size}
                        </p>
                      </div>
                    </div>

                    <div className="hidden md:flex md:col-span-2 items-center">
                      <Badge variant="outline" className="font-mono text-xs">
                        {file.type}
                      </Badge>
                    </div>

                    <div className="hidden md:flex md:col-span-2 items-center text-sm text-muted-foreground">
                      {file.size}
                    </div>

                    <div className="md:col-span-2 flex items-center">{getStatusBadge(file.status)}</div>

                    <div className="md:col-span-1 flex items-center justify-center">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 cursor-pointer w-8 text-muted-foreground hover:text-primary"
                        onClick={() => setSelectedFile(file)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>

                    </div>
                  </div>
                ))}

                {filteredFiles.length === 0 && (
                  <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                    <FolderOpen className="h-12 w-12 mb-3 opacity-50" />
                    <p className="text-sm">No files found</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`m-4 md:m-6 border-2 border-dashed rounded-xl transition-all duration-300 cursor-pointer ${isDragging
              ? "border-primary bg-primary/5 scale-[1.02]"
              : "border-border bg-muted/30 hover:border-primary/50 hover:bg-muted/50"
              }`}
            onClick={handleUpload}
          >
            <div className="flex flex-col items-center justify-center py-8 md:py-10 px-4">
              <div
                className={`w-14 h-14 rounded-full flex items-center justify-center mb-3 transition-all duration-300 ${isDragging ? "bg-primary/20 scale-110" : "bg-secondary/20"
                  }`}
              >
                <Upload className={`h-6 w-6 transition-colors ${isDragging ? "text-primary" : "text-secondary"}`} />
              </div>
              <p className="text-sm font-medium text-foreground mb-1">Drop files here or click to upload</p>
              <p className="text-xs text-muted-foreground">Supports multiple PDF, DOCX, TXT files up to 50MB each</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Indexing overlay with count support */}
      <IndexingOverlay
        isOpen={isIndexing}
        message={indexingMessage}
        title={indexingTitle}
        prog={indexingProg}
      />

      {/* File preview modal */}
      <FilePreviewModal file={selectedFile} onClose={() => setSelectedFile(null)} />
    </>
  )
}
