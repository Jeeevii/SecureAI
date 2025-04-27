import subprocess
import json
import tempfile
import os
"""
It's in this format 

{
  "MobileView/package-lock.json": {
      "package-lock.json": {
      "@babel/helpers": {
        "name": "@babel/helpers",
        "severity": "moderate",
        "isDirect": false,
        "via": [
          {
            "source": 1104001,
            "name": "@babel/helpers",
            "dependency": "@babel/helpers",
            "title": "Babel has inefficient RegExp complexity in generated code with .replace when transpiling named capturing groups",
            "url": "https://github.com/advisories/GHSA-968p-4wvh-cqc8",
            "severity": "moderate",
            "cwe": [
              "CWE-1333"
            ],
            "cvss": {
              "score": 6.2,
              "vectorString": "CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H"
            },
            "range": "<7.26.10"
          }
        ],
        "effects": [],
        "range": "<7.26.10",
        "nodes": [
          "node_modules/@babel/helpers"
        ],
        "fixAvailable": true
      }
    }
}

Convert it to this format:
{
    "MobileView/package-lock.json": {
      [
        "name": "@babel/helpers",
        "severity": "moderate",
        "isDirect": false,
        "range": "<7.26.10",
        "fixAvailable": true
      ]
    }
}
"""
def find_vulnerabilities(package_lock_content: str, file_path="package-lock.json"):
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_path = os.path.join(tmpdir, "package-lock.json")
        with open(lock_path, "w") as f:
            f.write(package_lock_content)
        
        package_json_path = os.path.join(tmpdir, "package.json")
        with open(package_json_path, "w") as f:
            f.write('{"name": "temp", "version": "1.0.0"}')
        
        result = subprocess.run(
            ["npm", "audit", "--package-lock-only", "--json"],
            cwd=tmpdir,
            capture_output=True,
            text=True
        )

        try:
            audit_data = json.loads(result.stdout)
            vulnerabilities = audit_data.get("vulnerabilities", {})
            
            simplified_vulnerabilities = simplify_vulnerabilities(vulnerabilities)
            
            return simplified_vulnerabilities
        except json.JSONDecodeError:
            print("Error parsing npm audit output")
            return {}

def simplify_vulnerabilities(vulnerabilities_data):
    """
    Convert the detailed vulnerability format to a simplified array format
    
    Args:
        vulnerabilities_data (dict): The original vulnerability data
        
    Returns:
        list: Array of simplified vulnerability objects
    """
    simplified_array = []
    
    for package_name, package_info in vulnerabilities_data.items():
        simplified_array.append({
            "name": package_info.get("name"),
            "severity": package_info.get("severity", "unknown"),
            "isDirect": package_info.get("isDirect", False),
            "range": package_info.get("range", ""),
            "fixAvailable": package_info.get("fixAvailable", False)
        })
    
    return simplified_array
    """
    Convert the detailed vulnerability format to a simplified format
    
    Args:
        vulnerabilities_data (dict): The original vulnerability data
        
    Returns:
        dict: Simplified vulnerability data
    """
    simplified_data = {}
    
    # Original data is expected to have the file path as the first key
    for file_path, packages in vulnerabilities_data.items():
        simplified_data[file_path] = {}
        
        # Process each package in the file
        for package_name, package_info in packages.items():
            # Extract only the fields we need
            simplified_data[file_path][package_name] = {
                "name": package_info.get("name"),
                "severity": package_info.get("severity"),
                "isDirect": package_info.get("isDirect", False),
                "range": package_info.get("range"),
                "fixAvailable": package_info.get("fixAvailable", False)
            }
    
    return simplified_data