"use client"

import { useState } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { AlertOctagon, AlertTriangle, AlertCircle, CheckCircle, Package, OctagonX } from "lucide-react"

// Properly parse the data from sessionStorage with a fallback structure
const getPackageIssuesData = () => {
  try {
    const data = sessionStorage.getItem("packagesVulnerabilities")
    if (!data) return { node: {}, python: {} }
    
    const parsedData = JSON.parse(data)
    return {
      node: parsedData.node || {},
      python: parsedData.python || {}
    }
  } catch (error) {
    console.error("Error parsing package vulnerabilities data:", error)
    return { node: {}, python: {} }
  }
}

interface PythonPackageIssue {
  package_name: string;
  analyzed_version: string;
  vulnerabilities_found: number;
}

interface NodePackageIssue {
  name: string;
  severity: string;
  isDirect: boolean;
  range: string;
  fixAvailable: boolean;
}

export function PackageIssues() {
  const [activeTab, setActiveTab] = useState("node")
  // Using state to ensure the component re-renders if sessionStorage updates
  const [packageData, setPackageData] = useState(() => getPackageIssuesData())

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
        case "critical":
            return <OctagonX className="h-5 w-5 text-red-700" />

      case "high":
        return <AlertOctagon className="h-5 w-5 text-red-500" />
      case "medium":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
    case "moderate":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />

      case "low":
        return <AlertCircle className="h-5 w-5 text-blue-500" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-400" />
    }
  }

  const getSeverityClass = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-50 text-red-700 border-red-100"
      case "medium":
        return "bg-yellow-50 text-yellow-700 border-yellow-100"
      case "low":
        return "bg-blue-50 text-blue-700 border-blue-100"
      default:
        return "bg-gray-50 text-gray-700 border-gray-100"
    }
  }

  const getVulnerabilityBadge = (count: number) => {
    if (count === 0) {
      return <Badge className="bg-green-50 text-green-700 border-green-100 hover:bg-green-100">{count}</Badge>
    } else if (count <= 1) {
      return <Badge className="bg-blue-50 text-blue-700 border-blue-100 hover:bg-blue-100">{count}</Badge>
    } else if (count <= 2) {
      return <Badge className="bg-yellow-50 text-yellow-700 border-yellow-100 hover:bg-yellow-100">{count}</Badge>
    } else {
      return <Badge className="bg-red-50 text-red-700 border-red-100 hover:bg-red-100">{count}</Badge>
    }
  }

  return (
    <div className="rounded-md border border-gray-200 overflow-hidden shadow-sm">
      <Tabs defaultValue="node" value={activeTab} onValueChange={setActiveTab}>
        <div className="bg-gray-50 border-b border-gray-200 px-4 py-2">
          <TabsList className="grid grid-cols-2 w-[400px]">
            <TabsTrigger value="node" className="data-[state=active]:bg-white">
              Node.js Packages
            </TabsTrigger>
            <TabsTrigger value="python" className="data-[state=active]:bg-white">
              Python Packages
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="node" className="p-0">
          {Object.keys(packageData.node || {}).length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              No Node.js package vulnerabilities found
            </div>
          ) : (
            Object.entries(packageData.node).map(([filepath, issuesArray]) => {
              // Ensure issues is an array
              const issues = Array.isArray(issuesArray) ? issuesArray : [];
              return (
                <div key={filepath} className="mb-4">
                  <div className="px-4 py-2 bg-gray-50 border-b border-t border-gray-200">
                    <h3 className="text-sm font-medium text-gray-700 flex items-center">
                      <Package className="h-4 w-4 mr-2 text-gray-500" />
                      {filepath}
                    </h3>
                  </div>
                  <Table>
                    <TableHeader>
                      <TableRow className="hover:bg-gray-100 border-gray-200">
                        <TableHead className="text-black">Package</TableHead>
                        <TableHead className="text-black">Severity</TableHead>
                        <TableHead className="text-black">Dependency</TableHead>
                        <TableHead className="text-black">Version Range</TableHead>
                        <TableHead className="text-black text-right">Fix Available</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {issues.map((issue, index) => (
                        <TableRow key={index} className="hover:bg-gray-50 border-gray-200">
                          <TableCell className="font-medium text-gray-900">{issue?.name || "Unknown"}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              {getSeverityIcon(issue?.severity || "unknown")}
                              <span
                                className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getSeverityClass(
                                  issue?.severity || "unknown",
                                )}`}
                              >
                                {issue?.severity || "Unknown"}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell className="text-gray-700">{issue?.isDirect ? "Direct" : "Indirect"}</TableCell>
                          <TableCell className="text-gray-700">{issue?.range || "Unknown"}</TableCell>
                          <TableCell className="text-right">
                            {issue?.fixAvailable ? (
                              <span className="text-green-600 flex items-center justify-end">
                                <CheckCircle className="h-4 w-4 mr-1" /> Yes
                              </span>
                            ) : (
                              <span className="text-red-600">No</span>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              );
            })
          )}
        </TabsContent>

        <TabsContent value="python" className="p-0">
          {Object.keys(packageData.python || {}).length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              No Python package vulnerabilities found
            </div>
          ) : (
            Object.entries(packageData.python).map(([filepath, issuesArray]) => {
              // Ensure issues is an array
              const issues = Array.isArray(issuesArray) ? issuesArray : [];
              return (
                <div key={filepath} className="mb-4">
                  <div className="px-4 py-2 bg-gray-50 border-b border-t border-gray-200">
                    <h3 className="text-sm font-medium text-gray-700 flex items-center">
                      <Package className="h-4 w-4 mr-2 text-gray-500" />
                      {filepath}
                    </h3>
                  </div>
                  <Table>
                    <TableHeader>
                      <TableRow className="hover:bg-gray-100 border-gray-200">
                        <TableHead className="text-black">Package</TableHead>
                        <TableHead className="text-black">Analyzed Version</TableHead>
                        <TableHead className="text-black text-right">Vulnerabilities</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {issues.map((issue, index) => (
                        <TableRow key={index} className="hover:bg-gray-50 border-gray-200">
                          <TableCell className="font-medium text-gray-900">{issue?.package_name || "Unknown"}</TableCell>
                          <TableCell className="text-gray-700">{issue?.analyzed_version || "Unknown"}</TableCell>
                          <TableCell className="text-right">
                            {getVulnerabilityBadge(issue?.vulnerabilities_found || 0)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              );
            })
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
