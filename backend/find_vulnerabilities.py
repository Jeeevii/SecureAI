import json
import os
import re
import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def analyze_file_for_vulnerabilities(file_data, repository_name="unknown_repository"):
    """
    Analyze a single file for vulnerabilities using an LLM.
    
    Args:
        file_data (dict): File data containing id, path, and contents
        repository_name (str): Name of the repository being analyzed
        
    Returns:
        list: List of vulnerability dictionaries
    """
    file_id = file_data["id"]
    file_path = file_data["path"]
    contents = file_data["contents"]
    
    # Split contents into lines for better line number identification
    lines = contents.split('\n')
    
    # Get current date for scan date
    scan_date = datetime.datetime.now().isoformat()
    
    # Construct prompt for the LLM
    prompt = f"""
    Analyze the following code for security vulnerabilities:
    File: {file_path}
    
    {contents}
    
    Identify any potential security issues including but not limited to:
    - Hardcoded credentials or API keys
    - Insecure data handling
    - Potential cross-site scripting (XSS)
    - Information leakage
    - Insecure API calls
    - Unsafe user input handling
    - Privacy concerns in data collection
    - Other security or privacy issues
    
    For each vulnerability found, provide:
    1. The approximate line number where the vulnerability occurs
    2. The type of security issue
    3. The severity (Low, Medium, or High)
    4. A detailed description of the vulnerability
    5. The exact code snippet where the vulnerability occurs
    6. A suggested fix for the vulnerability
    
    Format your response as a JSON object with the following structure:
    {{
      "repositoryName": "{repository_name}",
      "scanDate": "{scan_date}",
      "issues": [
        {{
          "fileName": "{file_path}",
          "lineNumber": int,
          "issueType": string,
          "severity": string,
          "description": string,
          "codeSnippet": string,
          "suggestedFix": string
        }},
        // Additional issues as needed
      ]
    }}
    
    Only include actual security concerns, not code quality issues unless they directly impact security.
    """
    
    # Call the LLM API to analyze the file
    try:
        response = client.chat.completions.create(
            model="gpt-4", # or another suitable model
            messages=[
                {"role": "system", "content": "You are a security expert analyzing code for vulnerabilities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000,
        )
        
        # Extract the LLM's response
        analysis_result = response.choices[0].message.content
        
        # Try to parse any JSON in the response
        vulnerabilities = []
        try:
            # Look for JSON object in the response
            json_match = re.search(r'\{[\s\S]*\}', analysis_result)
            if json_match:
                json_str = json_match.group(0)
                parsed_result = json.loads(json_str)
                
                # Extract issues from the parsed result
                if "issues" in parsed_result and isinstance(parsed_result["issues"], list):
                    raw_vulnerabilities = parsed_result["issues"]
                    
                    # Format vulnerabilities according to expected output
                    for vuln in raw_vulnerabilities:
                        vulnerabilities.append({
                            "fileName": vuln.get("fileName", file_path),
                            "lineNumber": vuln.get("lineNumber", 0),
                            "issueType": vuln.get("issueType", "Unknown"),
                            "severity": vuln.get("severity", "Medium"),
                            "description": vuln.get("description", ""),
                            "codeSnippet": vuln.get("codeSnippet", ""),
                            "suggestedFix": vuln.get("suggestedFix", "")
                        })
            
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract information using regex
            print(f"Warning: Could not parse JSON from LLM response for {file_path}. Falling back to heuristics.")
            
            # Try to extract issues using patterns
            issue_patterns = re.finditer(r'(?:Issue|Vulnerability)[\s\S]*?Line(?:\s+number)?[\s:]+(\d+)[\s\S]*?Type[\s:]+([^\n]+)[\s\S]*?Severity[\s:]+([^\n]+)[\s\S]*?Description[\s:]+([^\n]+(?:\n[^\n]+)*)[\s\S]*?Code[\s\S]*?(`[^`]+`|```[^`]+```)[\s\S]*?(?:Fix|Suggestion)[\s:]+([^\n]+(?:\n[^\n]+)*)', analysis_result, re.IGNORECASE)
            
            for match in issue_patterns:
                line_num = int(match.group(1))
                issue_type = match.group(2).strip()
                severity = match.group(3).strip()
                description = match.group(4).strip()
                code_snippet = match.group(5).strip('`').strip()
                suggested_fix = match.group(6).strip()
                
                vulnerabilities.append({
                    "fileName": file_path,
                    "lineNumber": line_num,
                    "issueType": issue_type,
                    "severity": severity,
                    "description": description,
                    "codeSnippet": code_snippet,
                    "suggestedFix": suggested_fix
                })
        
        return vulnerabilities, repository_name, scan_date
    
    except Exception as e:
        print(f"Error analyzing {file_path}: {str(e)}")
        return [], repository_name, scan_date

def find_vulnerabilities(input_file, output_file=None, repository_name=None):
    """
    Process the input file containing code files and find vulnerabilities in each file.
    
    Args:
        input_file (str): Path to the input JSON file
        output_file (str, optional): Path to the output file. If None, print to stdout.
        repository_name (str, optional): Name of the repository being analyzed
        
    Returns:
        dict: Dictionary with repository name, scan date, and issues found
    """
    # Load the JSON file
    with open(input_file, 'r') as f:
        file_data = json.load(f)
    
    # Extract repository name from input file if not provided
    if not repository_name:
        # Try to get repository name from the path
        input_path_parts = os.path.abspath(input_file).split(os.path.sep)
        if 'SecureAI' in input_path_parts:
            repository_name = input_path_parts[input_path_parts.index('SecureAI') - 1]
        else:
            repository_name = "unknown_repository"
    
    all_vulnerabilities = []
    scan_date = datetime.datetime.now().isoformat()
    
    # Process each file in the input
    for file_info in file_data:
        print(f"Analyzing file: {file_info['path']}")
        vulnerabilities, repo_name, current_scan_date = analyze_file_for_vulnerabilities(file_info, repository_name)
        all_vulnerabilities.extend(vulnerabilities)
        # Use the first non-empty repository name and scan date
        if repo_name != "unknown_repository":
            repository_name = repo_name
        if scan_date == datetime.datetime.now().isoformat() and current_scan_date != scan_date:
            scan_date = current_scan_date
    
    # Assign unique IDs to vulnerabilities
    for i, vuln in enumerate(all_vulnerabilities, 1):
        vuln["id"] = i
    
    # Format the results according to the expected output
    result = {
        "repositoryName": repository_name,
        "scanDate": scan_date,
        "issues": all_vulnerabilities
    }
    
    # Output the results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))
    
    return result

def main():
    """Main function to find vulnerabilities in test.json"""
    input_file = "/home/aryan/natsechack/SecureAI/backend/test.json"
    output_file = "/home/aryan/natsechack/SecureAI/backend/vulnerabilities.json"
    
    find_vulnerabilities(input_file, output_file)
    print(f"Analysis complete. Results written to {output_file}")

if __name__ == "__main__":
    main()
