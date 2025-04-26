import type React from "react"
import { Card, CardContent } from "@/components/ui/card"
import { AlertTriangle, AlertCircle, AlertOctagon, CheckCircle } from "lucide-react"

export function SummaryCards() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
      <SummaryCard
        title="Total Issues"
        value="10"
        icon={<AlertCircle className="h-5 w-5 text-gray-600" />}
        className="border-gray-200"
      />
      <SummaryCard
        title="High Risk"
        value="3"
        icon={<AlertOctagon className="h-5 w-5 text-red-500" />}
        className="border-red-100"
      />
      <SummaryCard
        title="Medium Risk"
        value="5"
        icon={<AlertTriangle className="h-5 w-5 text-yellow-500" />}
        className="border-yellow-100"
      />
      <SummaryCard
        title="Low Risk"
        value="2"
        icon={<CheckCircle className="h-5 w-5 text-blue-500" />}
        className="border-blue-100"
      />
    </div>
  )
}

interface SummaryCardProps {
  title: string
  value: string
  icon: React.ReactNode
  className?: string
}

function SummaryCard({ title, value, icon, className }: SummaryCardProps) {
  return (
    <Card className={`border shadow-sm ${className}`}>
      <CardContent className="p-6">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-3xl font-bold mt-1 text-black">{value}</p>
          </div>
          <div className="bg-gray-50 p-3 rounded-full">{icon}</div>
        </div>
      </CardContent>
    </Card>
  )
}
