"use client"

import { useEffect, useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { Shield, GitBranch, GitFork, Code, FileCode, AlertTriangle } from "lucide-react"

export default function ScanningPage() {
  const router = useRouter()
  const [progress, setProgress] = useState(0)
  const [currentStatus, setCurrentStatus] = useState("")
  const statusRef = useRef<HTMLDivElement>(null)
  const scanCompleteRef = useRef(false)

  const scanningStatuses = [
    "Connecting to GitHub API...",
    "Fetching repository metadata...",
    "Analyzing repository structure...",
    "Examining package dependencies...",
    "Checking for hardcoded credentials...",
    "Scanning API endpoints for vulnerabilities...",
    "Checking input validation patterns...",
    "Analyzing prompt handling for injection risks...",
    "Generating security report...",
  ]

   useEffect(() => {
    const fetchVulnerabilities = async () => {
      try {
        const repositoryUrl = sessionStorage.getItem("repositoryUrl")
        if (!repositoryUrl) {
          router.push("/")
          return
        }
  
        const response = await fetch("http://localhost:8000/vulnerabilities", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url: repositoryUrl }),
        })
  
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
  
        const data = await response.json()
        if (!data || !data.issues) {
          throw new Error("Invalid response format")
        }
        sessionStorage.setItem("vulnerabilities", JSON.stringify(data))
        sessionStorage.setItem("packagesVulnerabilities", JSON.stringify(data.packagesVulnerabilities || {}))
        sessionStorage.setItem("malware", JSON.stringify((data.malware) || []))
  
        scanCompleteRef.current = true
        console.log("Vulnerabilities fetched successfully:", data)
        setProgress(100)
      } catch (error) {
        console.error("Error fetching vulnerabilities:", error)
      }
    }
  
    fetchVulnerabilities()
  }, [router])

  useEffect(() => {
    let currentIndex = 0
    let interval: NodeJS.Timeout

    const updateStatus = () => {
      const newIndex = Math.min(Math.floor(progress / 7), scanningStatuses.length - 1)

      if (newIndex !== currentIndex) {
        currentIndex = newIndex
        setCurrentStatus(scanningStatuses[currentIndex])

        if (statusRef.current) {
          statusRef.current.classList.add("animate-fade-in")
          setTimeout(() => {
            if (statusRef.current) {
              statusRef.current.classList.remove("animate-fade-in")
            }
          }, 500)
        }
      }
    }

    interval = setInterval(updateStatus, 100)
    return () => clearInterval(interval)
  }, [progress, scanningStatuses])

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prevProgress) => {
        if (prevProgress >= 100) {
          clearInterval(timer)
          setTimeout(() => router.push("/results"), 1000)
          return 100
        }
        
        if (scanCompleteRef.current) {
          return 100
        }
        
        const increment = prevProgress < 30 ? 0.7 : 
                          prevProgress < 60 ? 0.5 : 
                          prevProgress < 85 ? 0.3 : 0.1
        return Math.min(prevProgress + increment, 90)
      })
    }, 100)

    return () => {
      clearInterval(timer)
    }
  }, [router])

  const getCurrentIcon = () => {
    if (progress < 20) return <GitBranch className="h-6 w-6 text-gray-600" />
    if (progress < 40) return <GitFork className="h-6 w-6 text-gray-600" />
    if (progress < 60) return <Code className="h-6 w-6 text-gray-600" />
    if (progress < 80) return <FileCode className="h-6 w-6 text-gray-600" />
    if (progress < 100) return <AlertTriangle className="h-6 w-6 text-gray-600" />
    return <Shield className="h-6 w-6 text-green-600" />
  }

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-4">
      <div className="max-w-xl w-full">
        <div className="flex flex-col items-center mb-16">
          <Shield className="h-16 w-16 text-black mb-4" />
          <h1 className="text-3xl font-bold text-black mb-2">Scanning Repository</h1>
          <p className="text-gray-600 text-center">SecureAI is analyzing your code for security vulnerabilities</p>
        </div>

        <div className="w-full mb-12">
          {/* Progress percentage */}
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center">
              {getCurrentIcon()}
              <span className="ml-2 text-sm font-medium text-gray-700">{Math.round(progress)}% complete</span>
            </div>
            {progress === 100 && <span className="text-sm font-medium text-green-600">Scan complete</span>}
          </div>

          {/* Custom progress bar */}
          <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-black transition-all duration-300 ease-out rounded-full"
              style={{
                width: `${progress}%`,
                boxShadow: progress > 0 ? "0 0 8px rgba(0, 0, 0, 0.3)" : "none",
              }}
            />
          </div>

          {/* Current status with typing effect */}
          <div ref={statusRef} className="mt-6 py-4 px-6 bg-gray-50 border border-gray-200 rounded-lg text-center">
            <div className="flex items-center justify-center">
              <div className="w-3 h-3 bg-black rounded-full mr-3 animate-pulse" />
              <p className="text-gray-800 font-medium">{currentStatus || "Initializing scan..."}</p>
            </div>
          </div>
        </div>

        {/* Additional info */}
        <div className="text-center text-sm text-gray-500 max-w-md mx-auto">
          <p>
            We're analyzing your repository structure, code patterns, and configuration files to identify potential
            security vulnerabilities.
          </p>
        </div>
      </div>
    </div>
  )
}