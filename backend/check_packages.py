import json 
from node_package_vulnerabilities import find_vulnerabilities as node_check
"""
Fetch data from json_output/repo_packages.json and check for vulnerabilities in Node.js and Python packages.
Format of json_output/repo_packages.json:
{
    "num_files": Int,
    "files": [
        {
            "id: Int,
            "path": String,
            "contents": String,
        },
        {
            "id: Int,
            "path": String,
            "contents": String,
            },
        ...
    ]
}
"""
def check_packages():
    vulnerabilities_found = {}
    node_vulnerabilities = {}
    python_vulnerabilities = {}
    try:
        with open('json_output/repo_packages.json', 'r') as infile:
            repo_packages = json.load(infile)
            
            # Process each file looking for package files
            for file_entry in repo_packages.get('files', []):
                file_path = file_entry.get('path', '')
                
                print(f"Checking file: {file_path}")
                if file_path.endswith('package-lock.json'):
                    print(f"Checking Node.js packages in: {file_path}")
                    # Extract contents and check for vulnerabilities
                    file_contents = file_entry.get('contents', '')
                    vulnerabilities = node_check(file_contents)
                    if vulnerabilities:
                        node_vulnerabilities[file_path] = vulnerabilities
                elif file_path.endswith('requirements.txt'):
                    pass
            vulnerabilities_found['node'] = node_vulnerabilities
            vulnerabilities_found['python'] = python_vulnerabilities
    except FileNotFoundError:
        print("Repository packages file not found. Please scan the repository first.")
    
    # Write vulnerabilities to output file
    with open('json_output/package_vulnerabilities.json', 'w') as outfile:
        json.dump(vulnerabilities_found, outfile, indent=2)
    
    return vulnerabilities_found

if __name__ == "__main__":
    check_packages()
    



