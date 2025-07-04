"use client"

import { GithubInput } from "@/components/github-input"
import { Card, CardContent } from "@/components/ui/card"
import { Shield } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="flex flex-col items-center justify-center text-center py-12">
          <div className="flex items-center gap-2 mb-6">
            <Shield className="h-12 w-12 text-black" />
            <h1 className="text-4xl md:text-5xl font-bold text-black">SecureAI</h1>
          </div>
          <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mb-12">
            AI-powered security scanner for your AI deployment projects
          </p>
          <Card className="border-gray-200 shadow-sm w-full max-w-2xl">
            <CardContent className="pt-6 pb-8">
              <h2 className="text-2xl font-semibold mb-6 text-black">Scan GitHub Repository</h2>
              <GithubInput />
            </CardContent>
          </Card>
        </div>

        {/* Features Section */}
        <div className="mt-16 max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-8 text-center text-black">Detect Common Security Issues</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FeatureCard
              title="Insecure Code Patterns"
              description="Identify injection flaws, authentication issues, and access control vulnerabilities"
            />
            <FeatureCard
              title="Library Misuse and Secrets"
              description="Detect misuse of libraries, hardcoded secrets, tokens, and keys"
            />
            <FeatureCard
              title="Misconfigured Environments"
              description="Analyze dependency configurations, environment variables, and insecure settings"
            />
            <FeatureCard
              title="Pipeline and Malware Risks"
              description="Identify CI/CD pipeline risks, unsafe scripts, and malware"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

function FeatureCard({ title, description }: { title: string; description: string }) {
  return (
    <Card className="border-gray-200 shadow-sm">
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold mb-2 text-black">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </CardContent>
    </Card>
  )
}
