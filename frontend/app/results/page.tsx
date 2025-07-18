"use client";

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { SecurityIssuesTable, SecurityIssue } from "@/components/security-issues-table"
import { PackageIssues } from "@/components/package-issues"
import { SummaryCards } from "@/components/summary-cards"
import { MalwareScanTable } from "@/components/malware-scan-table"
import { ArrowLeft, Download, Shield, Package, FileWarning } from "lucide-react"
import Link from "next/link"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useRouter } from "next/navigation"

// Define the grouping types
type GroupByType = 'none' | 'severity' | 'file';

export default function ResultsPage() {
  const [activeTab, setActiveTab] = useState("security")
  const [securityIssues, setSecurityIssues] = useState<SecurityIssue[]>([]);
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [groupBy, setGroupBy] = useState<GroupByType>('none');
  const [malwareData, setMalwareData] = useState([]);
  const router = useRouter();

  useEffect(() => {
    // Get vulnerabilities from sessionStorage (set during the scanning process)
    const vulnerabilitiesStr = sessionStorage.getItem("vulnerabilities");
    const repoUrl = sessionStorage.getItem("repositoryUrl");
    const malwareStr = sessionStorage.getItem("malware");
    
    if (!vulnerabilitiesStr || !repoUrl) {
      // If no data found, redirect to home page
      router.push("/");
      return;
    }
    
    try {
      const vulnerabilities = JSON.parse(vulnerabilitiesStr);
      // Extract security issues from the vulnerabilities data
      if (vulnerabilities.issues && Array.isArray(vulnerabilities.issues)) {
        setSecurityIssues(vulnerabilities.issues);
      }
      setRepositoryUrl(repoUrl);
      
      // Parse malware data if available
      if (malwareStr) {
        try {
          const malware = JSON.parse(malwareStr);
          setMalwareData(malware);
        } catch (error) {
          console.error("Error parsing malware data:", error);
        }
      }
    } catch (error) {
      console.error("Error parsing vulnerabilities:", error);
      // Handle error - maybe redirect or show an error message
    }
  }, [router]);

  const downloadRaw = () => {
    let textContent = "Security Issues Report\n\n";
    textContent += "ID | File | Issue Type | Severity | Line Number\n";
    textContent += "--------------------------------------------\n";

    securityIssues.forEach(issue => {
      textContent += `${issue.id} | ${issue.fileName} | ${issue.issueType} | ${issue.severity} | ${issue.lineNumber}\n`;
      textContent += `Description: ${issue.description}\n`;
      textContent += `Code Snippet:\n${issue.codeSnippet}\n`;
      textContent += `Suggested Fix:\n${issue.suggestedFix}\n`;
      textContent += "\n--------------------------------------------\n";
    });

    const blob = new Blob([textContent], { type: "text/plain" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "security_issues_report.txt";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const downloadPDF = () => {
    window.print();
  }

  // Extract repository name from URL
  const getRepoName = (url: string) => {
    try {
      const urlObj = new URL(url);
      const pathParts = urlObj.pathname.split('/').filter(Boolean);
      if (pathParts.length >= 2) {
        return `${pathParts[0]}/${pathParts[1]}`;
      }
      return url;
    } catch (e) {
      return url;
    }
  };

  const handleGroupBySeverity = () => {
    setGroupBy(groupBy === 'severity' ? 'none' : 'severity');
  };

  const handleGroupByFile = () => {
    setGroupBy(groupBy === 'file' ? 'none' : 'file');
  };
  
  const severityOrder = {
    'critical': 1,
    'high': 2, 
    'medium': 3,
    'low': 4
  };

  const sortedSecurityIssues = [...securityIssues].sort((a, b) => {
    if (groupBy === 'severity') {
      const severityA = a.severity.toLowerCase();
      const severityB = b.severity.toLowerCase();
      
      return (severityOrder[severityA as keyof typeof severityOrder] || 999) - (severityOrder[severityB as keyof typeof severityOrder] || 999);
    }
    return 0;
  });

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
              Repository: <span className="font-medium">{getRepoName(repositoryUrl)}</span>
            </p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="border-gray-300 text-gray-700 hover:text-black hover:bg-gray-50" onClick={downloadRaw}>
              <Download className="h-4 w-4 mr-2" />
              Download Report (Raw)
            </Button>
            <Button className="bg-black hover:bg-gray-800 text-white" onClick={downloadPDF}>
              <Download className="h-4 w-4 mr-2" />
              Download Report (PDF)
            </Button>
          </div>
        </div>

        <SummaryCards issues={securityIssues} />

        <div className="mt-8">
          <Tabs defaultValue="security" value={activeTab} onValueChange={setActiveTab} className="w-full">
            <div className="border-b border-gray-200">
              <TabsList className="h-12 bg-transparent p-0 w-full flex justify-start gap-8">
                <TabsTrigger
                  value="security"
                  className="data-[state=active]:border-b-2 data-[state=active]:border-black data-[state=active]:shadow-none rounded-none h-12 px-1"
                >
                  <div className="flex items-center gap-2">
                    <Shield className="h-5 w-5" />
                    <span>Security Issues</span>
                  </div>
                </TabsTrigger>
                <TabsTrigger
                  value="packages"
                  className="data-[state=active]:border-b-2 data-[state=active]:border-black data-[state=active]:shadow-none rounded-none h-12 px-1"
                >
                  <div className="flex items-center gap-2">
                    <Package className="h-5 w-5" />
                    <span>Package Issues</span>
                  </div>
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="security" className="mt-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-black">Security Issues</h2>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Group by:</span>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className={`h-8 border-gray-300 ${groupBy === 'severity' ? 'bg-gray-200 border-gray-400' : 'hover:bg-gray-50'}`}
                    onClick={handleGroupBySeverity}
                  >
                    Severity
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className={`h-8 border-gray-300 ${groupBy === 'file' ? 'bg-gray-200 border-gray-400' : 'hover:bg-gray-50'}`}
                    onClick={handleGroupByFile}
                  >
                    File
                  </Button>
                </div>
              </div>
              <SecurityIssuesTable securityIssues={sortedSecurityIssues} groupBy={groupBy} />
            </TabsContent>

            <TabsContent value="packages" className="mt-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-black">Package Vulnerabilities</h2>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">View package vulnerabilities by language</span>
                </div>
              </div>
              <PackageIssues />
            </TabsContent>
            
            <TabsContent value="malware" className="mt-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-black">Malware Detection</h2>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-600">Filter by:</span>
                  <Button variant="outline" size="sm" className="h-8 border-gray-300 bg-gray-50">
                    All
                  </Button>
                  <Button variant="outline" size="sm" className="h-8 border-gray-300">
                    Malicious
                  </Button>
                  <Button variant="outline" size="sm" className="h-8 border-gray-300">
                    Suspicious
                  </Button>
                </div>
              </div>
              <MalwareScanTable />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
