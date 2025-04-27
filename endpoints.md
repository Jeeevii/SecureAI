## Frontend

### `find_repository_vulnerabilities`
- **Input**: String containing repository URL  
- **Output**: JSON in the following format:

```javascript
const securityIssues = [
  {
    id: Int,              // Unique identifier for the issue
    fileName: String,     // Name of the file where the issue is found
    lineNumber: Int,      // Line number of the issue
    issueType: String,    // Type of the security issue
    severity: String,     // Severity level: Low, Medium, High
    description: String,  // Description of the issue
    codeSnippet: String,  // Code snippet where the issue occurs
    suggestedFix: String, // Suggested fix for the issue
  },
];
```

## Backend

### `fetch_github_repository`
- **Input**: String containing the repository URL  
- **Output**: JSON in the following format:

{
  "num_files": Int
  "files": 
  [
    {
      id: Int // id that goes from 1 to n
      path: String,    // Path of the file in the repository
      contents: String // Contents of the file
    }
  ]
}

### `find_file_vulnerabilities`
- **Input**: 
  - `file_contents`: String containing the file's contents  
  - `file_path`: String containing the file's path  
- **Output**: JSON in the following format:

```javascript
{
  repositoryName: String, 
  scanDate: String
  issues: [
  {
    id: Int,              // Unique identifier for the issue
    fileName: String,     // Name of the file where the issue is found
    lineNumber: Int,      // Line number of the issue
    issueType: String,    // Type of the security issue
    severity: String,     // Severity level: Low, Medium, High
    description: String,  // Description of the issue
    codeSnippet: String,  // Code snippet where the issue occurs
    suggestedFix: String, // Suggested fix for the issue
  }
  ]
}
```
