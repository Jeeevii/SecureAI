"use client";

import React, { useState, useMemo } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, Copy, AlertOctagon, AlertTriangle, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

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

type GroupByType = 'none' | 'severity' | 'file';

interface GroupedIssues {
  groupName: string;
  issues: SecurityIssue[];
}

export function SecurityIssuesTable({ 
  securityIssues, 
  groupBy = 'none' 
}: { 
  securityIssues: SecurityIssue[] | undefined;
  groupBy?: GroupByType;
}) {
  const [expandedRows, setExpandedRows] = useState<number[]>([]);
  const [expandedGroups, setExpandedGroups] = useState<string[]>([]);
  const { toast } = useToast();

  // Group issues based on the selected grouping method
  const groupedIssues = useMemo(() => {
    if (!securityIssues || groupBy === 'none') {
      return null;
    }

    const groups: Record<string, SecurityIssue[]> = {};
    
    securityIssues.forEach(issue => {
      const groupKey = groupBy === 'severity' ? issue.severity : issue.fileName;
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(issue);
    });

    return Object.entries(groups).map(([groupName, issues]) => ({
      groupName,
      issues
    })).sort((a, b) => {
      // For severity, sort in order of high, medium, low
      if (groupBy === 'severity') {
        const severityOrder: Record<string, number> = { high: 0, medium: 1, low: 2 };
        return severityOrder[a.groupName as keyof typeof severityOrder] - 
               severityOrder[b.groupName as keyof typeof severityOrder];
      }
      // For files, sort alphabetically
      return a.groupName.localeCompare(b.groupName);
    });
  }, [securityIssues, groupBy]);

  const toggleRow = (id: number) => {
    setExpandedRows((prev) => (prev.includes(id) ? prev.filter((rowId) => rowId !== id) : [...prev, id]));
  };

  const toggleGroup = (groupName: string) => {
    setExpandedGroups((prev) => 
      prev.includes(groupName) ? prev.filter(g => g !== groupName) : [...prev, groupName]
    );
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

  if (!securityIssues || securityIssues.length === 0) {
    return (
      <div className="text-center text-gray-500">
        <p>No security issues to display.</p>
      </div>
    );
  }

  if (groupBy === 'none') {
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
                        <p className="text-gray-700 mb-4 whitespace-pre-wrap break-words">{issue.description}</p>

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
                          <pre className="bg-gray-100 p-3 rounded-md overflow-x-auto text-sm whitespace-pre-wrap break-all">
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
                          <pre className="bg-gray-100 p-3 rounded-md overflow-x-auto text-sm whitespace-pre-wrap break-all">
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

  // Render grouped issues
  return (
    <div className="rounded-md border border-gray-200 overflow-hidden shadow-sm">
      {groupedIssues && groupedIssues.map((group) => (
        <div key={group.groupName} className="border-b border-gray-200 last:border-0">
          <div 
            className={`flex items-center justify-between p-4 bg-gray-50 cursor-pointer ${
              expandedGroups.includes(group.groupName) ? 'border-b border-gray-200' : ''
            }`}
            onClick={() => toggleGroup(group.groupName)}
          >
            <div className="flex items-center gap-2">
              {groupBy === 'severity' && getSeverityIcon(group.groupName)}
              <h3 className="font-medium text-black">
                {groupBy === 'severity' 
                  ? `${group.groupName.charAt(0).toUpperCase() + group.groupName.slice(1)} Severity Issues` 
                  : group.groupName}
              </h3>
              <span className="bg-gray-200 text-gray-700 px-2 py-0.5 rounded-full text-xs">
                {group.issues.length}
              </span>
            </div>
            {expandedGroups.includes(group.groupName) 
              ? <ChevronUp className="h-4 w-4 text-gray-400" />
              : <ChevronDown className="h-4 w-4 text-gray-400" />
            }
          </div>

          {expandedGroups.includes(group.groupName) && (
            <Table>
              <TableHeader className="bg-gray-50">
                <TableRow className="hover:bg-gray-100 border-gray-200">
                  <TableHead className="w-[50px]"></TableHead>
                  {groupBy === 'severity' ? (
                    <TableHead className="text-black">File</TableHead>
                  ) : (
                    <TableHead className="text-black">Issue Type</TableHead>
                  )}
                  {groupBy === 'severity' ? (
                    <TableHead className="text-black">Issue Type</TableHead>
                  ) : (
                    <TableHead className="text-black">Severity</TableHead>
                  )}
                  <TableHead className="text-right text-black">Line</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {group.issues.map((issue) => (
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
                      {groupBy === 'severity' ? (
                        <TableCell className="font-medium text-gray-900">{issue.fileName}</TableCell>
                      ) : (
                        <TableCell className="text-gray-700">{issue.issueType}</TableCell>
                      )}
                      {groupBy === 'severity' ? (
                        <TableCell className="text-gray-700">{issue.issueType}</TableCell>
                      ) : (
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
                      )}
                      <TableCell className="text-right text-gray-700">{issue.lineNumber}</TableCell>
                    </TableRow>
                    {expandedRows.includes(issue.id) && (
                      <TableRow key={`expanded-${issue.id}`} className="border-gray-200 bg-gray-50">
                        <TableCell colSpan={5} className="p-0">
                          <div className="p-4">
                            <h3 className="text-lg font-semibold text-black mb-2">{issue.issueType}</h3>
                            <p className="text-gray-700 mb-4 whitespace-pre-wrap break-words">{issue.description}</p>

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
                              <pre className="bg-gray-100 p-3 rounded-md overflow-x-auto text-sm whitespace-pre-wrap break-all">
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
                              <pre className="bg-gray-100 p-3 rounded-md overflow-x-auto text-sm whitespace-pre-wrap break-all">
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
          )}
        </div>
      ))}
    </div>
  );
}