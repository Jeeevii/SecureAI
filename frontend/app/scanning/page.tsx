"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Shield, CheckCircle } from "lucide-react"
import { Progress } from "@/components/ui/progress"

export default function ScanningPage() {
  const router = useRouter()
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)

  const scanSteps = [
    "Cloning repository...",
    "Analyzing project structure...",
    "Scanning for hardcoded API keys...",
    "Checking Docker configurations...",
    "Identifying prompt injection vulnerabilities...",
    "Examining API endpoints for security issues...",
    "Validating input sanitization...",
    "Checking for rate limiting implementations...",
    "Analyzing authentication mechanisms...",
    "Generating security report...",
  ]

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prevProgress) => {
        if (prevProgress >= 100) {
          clearInterval(timer)
          setTimeout(() => router.push("/results"), 1000)
          return 100
        }

        // Update current step based on progress
        const newStep = Math.min(Math.floor(prevProgress / (100 / scanSteps.length)), scanSteps.length - 1)
        if (newStep !== currentStep) {
          setCurrentStep(newStep)
        }

        return prevProgress + 1
      })
    }, 100)

    return () => {
      clearInterval(timer)
    }
  }, [router, currentStep, scanSteps.length])

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        <div className="flex flex-col items-center mb-12">
          <Shield className="h-16 w-16 text-black mb-4" />
          <h1 className="text-3xl font-bold text-black mb-2">Scanning Your Project</h1>
          <p className="text-gray-600 text-center">
            SecureGPT is analyzing your GitHub repository for security vulnerabilities
          </p>
        </div>

        <div className="w-full mb-8">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">{progress}% complete</span>
            {progress === 100 && (
              <span className="text-sm font-medium text-green-600 flex items-center">
                <CheckCircle className="h-4 w-4 mr-1" /> Scan complete
              </span>
            )}
          </div>
          <Progress value={progress} className="h-2 bg-gray-200" indicatorClassName="bg-black" />
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-black mb-4">Scan Progress</h2>
          <div className="space-y-4">
            {scanSteps.map((step, index) => (
              <div key={index} className="flex items-center">
                <div
                  className={`h-4 w-4 rounded-full mr-3 flex-shrink-0 ${
                    index < currentStep
                      ? "bg-green-500"
                      : index === currentStep
                        ? "bg-black animate-pulse"
                        : "bg-gray-300"
                  }`}
                />
                <span
                  className={`text-sm ${
                    index < currentStep
                      ? "text-gray-500"
                      : index === currentStep
                        ? "text-black font-medium"
                        : "text-gray-400"
                  }`}
                >
                  {step}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8 text-center text-sm text-gray-500">
          This may take a few moments depending on the size of your project
        </div>
      </div>
    </div>
  )
}
