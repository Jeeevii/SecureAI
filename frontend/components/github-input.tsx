"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Github, Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export function GithubInput() {
  const [repoUrl, setRepoUrl] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const { toast } = useToast()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!repoUrl) {
      toast({
        title: "Repository URL required",
        description: "Please enter a GitHub repository URL",
        variant: "destructive",
      })
      return
    }

    // Simple validation for GitHub URL format
    const githubUrlPattern = /^https:\/\/github\.com\/[\w-]+\/[\w-]+/
    if (!githubUrlPattern.test(repoUrl)) {
      toast({
        title: "Invalid GitHub URL",
        description: "Please enter a valid GitHub repository URL",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)

    // Simulate repository scanning
    setTimeout(() => {
      setIsLoading(false)
      router.push("/scanning")
    }, 1000)
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex flex-col space-y-4">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Github className="h-5 w-5 text-gray-400" />
          </div>
          <Input
            type="text"
            placeholder="https://github.com/username/repo"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            className="pl-10 border-gray-300 text-gray-900 placeholder:text-gray-400 h-14 text-lg"
          />
        </div>
        <div className="flex flex-col space-y-2">
          <Button
            type="submit"
            className="w-full py-6 bg-black hover:bg-gray-800 text-white text-lg font-medium"
            disabled={isLoading}
            size="lg"
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Scanning...
              </>
            ) : (
              "Scan Repository"
            )}
          </Button>
          <p className="text-sm text-gray-500 text-center">
            We'll analyze your repository for common security issues in AI deployments
          </p>
        </div>
      </div>
    </form>
  )
}
