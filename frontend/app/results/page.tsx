"use client"

import { Button } from "@/components/ui/button"
import { SecurityIssuesTable } from "@/components/security-issues-table"
import { SummaryCards } from "@/components/summary-cards"
import { ArrowLeft, Download, FileText } from "lucide-react"
import Link from "next/link"

export default function ResultsPage() {
  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <Link href="/" className="flex items-center text-gray-500 hover:text-black mb-2">
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to Home
            </Link>
            <h1 className="text-3xl font-bold text-black">Security Scan Results</h1>
            <p className="text-gray-600 mt-1">
              Repository: <span className="font-medium">username/ai-deployment-project</span>
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="border-gray-300 text-gray-700 hover:text-black hover:bg-gray-50">
              <FileText className="h-4 w-4 mr-2" />
              View Raw Log
            </Button>
            <Button className="bg-black hover:bg-gray-800 text-white">
              <Download className="h-4 w-4 mr-2" />
              Download Report
            </Button>
          </div>
        </div>

        <SummaryCards />

        <div className="mt-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-black">Security Issues</h2>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Group by:</span>
              <Button variant="outline" size="sm" className="h-8 border-gray-300 bg-gray-50">
                Severity
              </Button>
              <Button variant="outline" size="sm" className="h-8 border-gray-300">
                File
              </Button>
            </div>
          </div>

          <SecurityIssuesTable />
        </div>
      </div>
    </div>
  )
}
