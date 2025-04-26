"use client"

import React, { useState } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { ChevronDown, ChevronUp, Copy, AlertOctagon, AlertTriangle, AlertCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

// Mock security issues data
const securityIssues = [
  {
    id: 1,
    fileName: "app/api/generate.js",
    lineNumber: 12,
    issueType: "Hardcoded API Key",
    severity: "high",
    description:
      "API key is hardcoded in the source code, making it vulnerable to exposure if the code is shared or leaked.",
    codeSnippet: `const openaiApiKey = "sk-1234567890abcdefghijklmnopqrstuvwxyz";
const response = await fetch("https://api.openai.com/v1/completions", {
  headers: {
    "Authorization": \`Bearer \${openaiApiKey}\`,
    "Content-Type": "application/json"
  },
  // ...
});`,
    suggestedFix: `// Store API keys in environment variables
const openaiApiKey = process.env.OPENAI_API_KEY;
const response = await fetch("https://api.openai.com/v1/completions", {
  headers: {
    "Authorization": \`Bearer \${openaiApiKey}\`,
    "Content-Type": "application/json"
  },
  // ...
});`,
  },
  {
    id: 2,
    fileName: "app/api/chat.js",
    lineNumber: 28,
    issueType: "Prompt Injection Vulnerability",
    severity: "high",
    description:
      "User input is directly concatenated into the prompt without sanitization, allowing potential prompt injection attacks.",
    codeSnippet: `// User input is directly concatenated into the prompt
const prompt = \`Answer the following question: \${userQuestion}\`;
const completion = await openai.createCompletion({
  model: "text-davinci-003",
  prompt: prompt,
  max_tokens: 500
});`,
    suggestedFix: `// Sanitize and validate user input before using it in prompts
const sanitizedQuestion = sanitizeUserInput(userQuestion);
// Use a template with clear boundaries
const prompt = \`Answer the following question: ""\${sanitizedQuestion}""\`;
// Consider using a system message to set boundaries
const completion = await openai.createChatCompletion({
  model: "gpt-3.5-turbo",
  messages: [
    { role: "system", content: "You are a helpful assistant that only answers the question provided." },
    { role: "user", content: sanitizedQuestion }
  ]
});`,
  },
  {
    id: 3,
    fileName: "Dockerfile",
    lineNumber: 15,
    issueType: "Insecure Docker Configuration",
    severity: "medium",
    description: "Container is running as root, which is a security risk if the container is compromised.",
    codeSnippet: `FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
EXPOSE 3000
CMD ["npm", "start"]`,
    suggestedFix: `FROM node:18-alpine
WORKDIR /app
COPY . .
RUN npm install
# Create a non-root user
RUN addgroup -g 1001 -S appuser && adduser -u 1001 -S appuser -G appuser
# Change ownership of app files
RUN chown -R appuser:appuser /app
# Switch to non-root user
USER appuser
EXPOSE 3000
CMD ["npm", "start"]`,
  },
  {
    id: 4,
    fileName: "app/api/completions/route.js",
    lineNumber: 5,
    issueType: "Missing Rate Limiting",
    severity: "medium",
    description:
      "API endpoint lacks rate limiting, making it vulnerable to abuse and potential denial of service attacks.",
    codeSnippet: `export async function POST(req) {
  const { prompt } = await req.json();
  
  // No rate limiting implemented
  const completion = await openai.createCompletion({
    model: "text-davinci-003",
    prompt,
    max_tokens: 500
  });
  
  return new Response(JSON.stringify(completion.data));
}`,
    suggestedFix: `import { rateLimit } from '@/lib/rate-limit';

// Create a rate limiter that allows 10 requests per minute
const limiter = rateLimit({
  interval: 60 * 1000, // 1 minute
  uniqueTokenPerInterval: 500,
  maxRequests: 10,
});

export async function POST(req) {
  const ip = req.headers.get('x-forwarded-for') || 'anonymous';
  
  try {
    // Apply rate limiting
    await limiter.check(ip);
    
    const { prompt } = await req.json();
    const completion = await openai.createCompletion({
      model: "text-davinci-003",
      prompt,
      max_tokens: 500
    });
    
    return new Response(JSON.stringify(completion.data));
  } catch (error) {
    if (error.message === 'Rate limit exceeded') {
      return new Response(JSON.stringify({ error: 'Too many requests' }), { 
        status: 429,
        headers: { 'Retry-After': '60' }
      });
    }
    return new Response(JSON.stringify({ error: error.message }), { status: 500 });
  }
}`,
  },
  {
    id: 5,
    fileName: "app/api/images/route.js",
    lineNumber: 18,
    issueType: "Insufficient Input Validation",
    severity: "high",
    description:
      "User input for image generation is not properly validated, potentially allowing malicious prompts or content policy violations.",
    codeSnippet: `export async function POST(req) {
  const { prompt } = await req.json();
  
  // No validation of the prompt
  const response = await openai.createImage({
    prompt,
    n: 1,
    size: "1024x1024",
  });
  
  return new Response(JSON.stringify(response.data));
}`,
    suggestedFix: `import { validateImagePrompt } from '@/lib/content-validation';

export async function POST(req) {
  const { prompt } = await req.json();
  
  // Validate the prompt for inappropriate content
  const validationResult = validateImagePrompt(prompt);
  
  if (!validationResult.isValid) {
    return new Response(
      JSON.stringify({ 
        error: 'Content policy violation', 
        details: validationResult.reason 
      }), 
      { status: 400 }
    );
  }
  
  const response = await openai.createImage({
    prompt: validationResult.sanitizedPrompt,
    n: 1,
    size: "1024x1024",
  });
  
  return new Response(JSON.stringify(response.data));
}`,
  },
]

export function SecurityIssuesTable() {
  const [expandedRows, setExpandedRows] = useState<number[]>([])
  const { toast } = useToast()

  const toggleRow = (id: number) => {
    setExpandedRows((prev) => (prev.includes(id) ? prev.filter((rowId) => rowId !== id) : [...prev, id]))
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast({
      title: "Copied to clipboard",
      description: "The code has been copied to your clipboard",
    })
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "high":
        return <AlertOctagon className="h-5 w-5 text-red-500" />
      case "medium":
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
                              e.stopPropagation()
                              copyToClipboard(issue.codeSnippet)
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
                              e.stopPropagation()
                              copyToClipboard(issue.suggestedFix)
                            }}
                          >
                            <Copy className="h-3.5 w-3.5 mr-1" />
                            Copy Fix
                          </Button>
                        </div>
                        <pre className="bg-gray-100 p-3 rounded-md overflow-x-auto text-sm">
                          <code className="text-green-700">{issue.suggestedFix}</code>
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
  )
}
