"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Upload, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export function FileUpload() {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const router = useRouter()
  const { toast } = useToast()

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = () => {
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.type === "application/zip" || droppedFile.type === "application/x-zip-compressed") {
        setFile(droppedFile)
      } else {
        toast({
          title: "Invalid file format",
          description: "Please upload a ZIP file containing your project",
          variant: "destructive",
        })
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0]
      if (selectedFile.type === "application/zip" || selectedFile.type === "application/x-zip-compressed") {
        setFile(selectedFile)
      } else {
        toast({
          title: "Invalid file format",
          description: "Please upload a ZIP file containing your project",
          variant: "destructive",
        })
      }
    }
  }

  const handleUpload = () => {
    if (!file) {
      toast({
        title: "No file selected",
        description: "Please select a ZIP file to upload",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)

    // Simulate file upload and processing
    setTimeout(() => {
      setIsUploading(false)
      router.push("/scanning")
    }, 1000)
  }

  return (
    <div className="w-full">
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragging ? "border-black bg-gray-50" : "border-gray-300 hover:border-gray-400"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => document.getElementById("file-upload")?.click()}
      >
        <Upload className="h-10 w-10 mx-auto mb-4 text-gray-400" />
        <p className="mb-2 text-sm text-gray-600">
          <span className="font-semibold">Click to upload</span> or drag and drop
        </p>
        <p className="text-xs text-gray-400">ZIP file (max 20MB)</p>
        <input id="file-upload" type="file" accept=".zip" className="hidden" onChange={handleFileChange} />
      </div>

      {file && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg flex items-center justify-between">
          <span className="text-sm truncate text-gray-700">{file.name}</span>
          <span className="text-xs text-gray-500">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
        </div>
      )}

      <Button
        className="w-full mt-4 bg-black hover:bg-gray-800 text-white"
        onClick={handleUpload}
        disabled={!file || isUploading}
      >
        {isUploading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Scanning...
          </>
        ) : (
          "Upload & Scan"
        )}
      </Button>
    </div>
  )
}
