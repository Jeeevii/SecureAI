"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { AlertCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export function GithubInput() {
  const [repositoryUrl, setRepositoryUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const router = useRouter()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!repositoryUrl) {
      setError("Please enter a GitHub repository URL")
      return
    }

    try {
      setIsLoading(true)
      
      // Store the repository URL in sessionStorage to use it later
      sessionStorage.setItem("repositoryUrl", repositoryUrl)
      
      // Navigate to the scanning page
      router.push("/scanning")
      
    } catch (error) {
      console.error("Error submitting repository:", error)
      setError("Failed to submit the repository for scanning.")
      toast({
        title: "Error",
        description: "Failed to submit the repository for scanning.",
        variant: "destructive",
      })
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <div className="relative">
          <Input
            type="text"
            placeholder="https://github.com/username/repository"
            value={repositoryUrl}
            onChange={(e) => setRepositoryUrl(e.target.value)}
            className={`pr-10 ${error ? "border-red-500" : ""}`}
            disabled={isLoading}
          />
        </div>
        {error && (
          <div className="flex items-center text-sm text-red-500 mt-1">
            <AlertCircle className="h-4 w-4 mr-1" />
            <span>{error}</span>
          </div>
        )}
      </div>
      <Button type="submit" className="w-full bg-black hover:bg-gray-800 text-white" disabled={isLoading}>
        {isLoading ? "Processing..." : "Scan Repository"}
      </Button>
    </form>
  )
}
