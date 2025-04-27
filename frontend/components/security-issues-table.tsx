"use client";

import React, { useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, Copy, AlertOctagon, AlertTriangle, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

// Assuming SecurityIssue is imported
export interface SecurityIssue {
  
  id: number;
  fileName: string;
  lineNumber: number;
  issueType: string;
  severity: "high" | "medium" | "low";
  description: string;
  codeSnippet: string;
  suggestedFix: string;
}

export function SecurityIssuesTable({ securityIssues }: { securityIssues: SecurityIssue[] | undefined }) {
  const [expandedRows, setExpandedRows] = useState<number[]>([]);
  const { toast } = useToast();

  const toggleRow = (id: number) => {
    setExpandedRows((prev) => (prev.includes(id) ? prev.filter((rowId) => rowId !== id) : [...prev, id]));
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: "The code has been copied to your clipboard",
    });
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "high":
        return <AlertOctagon className="h-5 w-5 text-red-500" />;
      case "medium":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case "low":
        return <AlertCircle className="h-5 w-5 text-blue-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-50 text-red-700 border-red-100";
      case "medium":
        return "bg-yellow-50 text-yellow-700 border-yellow-100";
      case "low":
        return "bg-blue-50 text-blue-700 border-blue-100";
      default:
        return "bg-gray-50 text-gray-700 border-gray-100";
    }
  };

  if (!securityIssues) {
    return (
      <div className="text-center text-gray-500">
        <p>No security issues to display.</p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-gray-200 overflow-hidden shadow-sm">
      <Table>
        <TableHeader className="bg-gray-50">
          <TableRow className="hover:bg-gray-100 border-gray-200">
            <TableHead className="w-[50px]"></TableHead>
            <TableHead className="text-black">File</TableHead>
            <TableHead className="text-black">Issue Type</TableHead>
            <TableHead className="text-black">Severity</TableHead>
            <TableHead className="text-right text-black">Line</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {securityIssues.map((issue) => (
            <React.Fragment key={issue.id}>
              <TableRow
                className={`hover:bg-gray-50 border-gray-200 cursor-pointer ${
                  expandedRows.includes(issue.id) ? "bg-gray-50" : ""
                }`}
                onClick={() => toggleRow(issue.id)}
              >
                <TableCell>
                  {expandedRows.includes(issue.id) ? (
                    <ChevronUp className="h-4 w-4 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-gray-400" />
                  )}
                </TableCell>
                <TableCell className="font-medium text-gray-900">{issue.fileName}</TableCell>
                <TableCell className="text-gray-700">{issue.issueType}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    {getSeverityIcon(issue.severity)}
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getSeverityClass(issue.severity)}`}
                    >
                      {issue.severity}
                    </span>
                  </div>
                </TableCell>
                <TableCell className="text-right text-gray-700">{issue.lineNumber}</TableCell>
              </TableRow>
              {expandedRows.includes(issue.id) && (
                <TableRow key={`expanded-${issue.id}`} className="border-gray-200 bg-gray-50">
                  <TableCell colSpan={5} className="p-0">
                    <div className="p-4">
                      <h3 className="text-lg font-semibold text-black mb-2">{issue.issueType}</h3>
                      <p className="text-gray-700 mb-4">{issue.description}</p>

                      <div className="mb-4">
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="text-sm font-medium text-gray-700">Vulnerable Code</h4>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 text-gray-500 hover:text-black"
                            onClick={(e) => {
                              e.stopPropagation();
                              copyToClipboard(issue.codeSnippet);
                            }}
                          >
                            <Copy className="h-3.5 w-3.5 mr-1" />
                            Copy
                          </Button>
                        </div>
                        <pre className="bg-gray-100 p-3 rounded-md overflow-x-auto text-sm">
                          <code className="text-gray-800">{issue.codeSnippet}</code>
                        </pre>
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <h4 className="text-sm font-medium text-gray-700">Suggested Fix</h4>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 text-gray-500 hover:text-black"
                            onClick={(e) => {
                              e.stopPropagation();
                              copyToClipboard(issue.suggestedFix);
                            }}
                          >
                            <Copy className="h-3.5 w-3.5 mr-1" />
                            Copy Fix
                          </Button>
                        </div>
                        <pre className="bg-gray-100 p-3 rounded-md overflow-x-auto text-sm">
                          <code className="text-gray-800">{issue.suggestedFix}</code>
                        </pre>
                      </div>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </React.Fragment>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}