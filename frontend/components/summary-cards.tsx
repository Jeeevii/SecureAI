"use client";

import type React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { AlertOctagon, AlertTriangle, AlertCircle } from "lucide-react";
import { SecurityIssue } from "@/components/security-issues-table";

interface SummaryCardsProps {
  issues?: SecurityIssue[];
}

export function SummaryCards({ issues = [] }: SummaryCardsProps) {
  // Count issues by severity
  console.log("Issues:", issues);
  const highIssues = issues.filter(issue => issue.severity.toLowerCase() === "high").length;
  const mediumIssues = issues.filter(issue => issue.severity.toLowerCase() === "medium").length;
  const lowIssues = issues.filter(issue => issue.severity.toLowerCase() === "low").length;
  const totalIssues = issues.length;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card className="border-gray-200 shadow-sm">
        <CardContent className="flex justify-between items-center p-6">
          <div>
            <p className="text-sm font-medium text-gray-500">Total Issues</p>
            <h3 className="text-2xl font-bold text-black">{totalIssues}</h3>
          </div>
          <div className="h-12 w-12 bg-gray-100 rounded-full flex items-center justify-center">
            <span className="text-xl font-semibold text-gray-700">{totalIssues}</span>
          </div>
        </CardContent>
      </Card>

      <Card className="border-gray-200 shadow-sm">
        <CardContent className="flex justify-between items-center p-6">
          <div>
            <p className="text-sm font-medium text-gray-500">High Risk</p>
            <h3 className="text-2xl font-bold text-red-600">{highIssues}</h3>
          </div>
          <div className="h-12 w-12 bg-red-50 rounded-full flex items-center justify-center">
            <AlertOctagon className="h-6 w-6 text-red-500" />
          </div>
        </CardContent>
      </Card>

      <Card className="border-gray-200 shadow-sm">
        <CardContent className="flex justify-between items-center p-6">
          <div>
            <p className="text-sm font-medium text-gray-500">Medium Risk</p>
            <h3 className="text-2xl font-bold text-yellow-600">{mediumIssues}</h3>
          </div>
          <div className="h-12 w-12 bg-yellow-50 rounded-full flex items-center justify-center">
            <AlertTriangle className="h-6 w-6 text-yellow-500" />
          </div>
        </CardContent>
      </Card>

      <Card className="border-gray-200 shadow-sm">
        <CardContent className="flex justify-between items-center p-6">
          <div>
            <p className="text-sm font-medium text-gray-500">Low Risk</p>
            <h3 className="text-2xl font-bold text-blue-600">{lowIssues}</h3>
          </div>
          <div className="h-12 w-12 bg-blue-50 rounded-full flex items-center justify-center">
            <AlertCircle className="h-6 w-6 text-blue-500" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
