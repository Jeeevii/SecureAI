import sys
import argparse
import requests
import json
import os
import hashlib
from urllib.parse import urlparse
from datetime import datetime

# ===== Constants =====
NORMAL_EXTENSIONS = {
    '.py', '.js', '.cpp', '.c', '.java', '.html', '.ts',
    '.tsx', '.jsx', '.go', '.sh', '.rb', '.php', '.sql', '.xml', '.json', '.yml', '.yaml'
}
BINARY_EXTENSIONS = {'.exe', '.dll', '.sys', '.bin', '.dat', '.msi', '.apk', '.so', '.dmg'}

IGNORE_DIRS = {'node_modules', '.git', '.github', '__pycache__', '.json', '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z'}

OUTPUT_FILE = 'repo_files.json'
# OUTPUT_BINARIES = 'repo_binaries.json'
OUTPUT_FOLDER = 'json_output'

# ===== Utility =====
def sha256_file(url, hash_algorithm="sha256"):
    try:
        # Request the file content from the raw GitHub URL
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  # Raise exception for bad responses

            hasher = hashlib.new(hash_algorithm)
            for chunk in response.iter_content(chunk_size=8192):  # Process file in chunks
                if chunk:
                    hasher.update(chunk)
            return hasher.hexdigest()

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
        
# ===== Main Class =====
class GitHubScanner:
    def __init__(self, repo_url):
        self.owner, self.repo = self._parse_github_url(repo_url)
        self.session = requests.Session()
        self.branch = self._get_default_branch()
        self.repo_name = self.repo

    def create_files(self):
        """Ensure the output folder and files exist."""
        # Ensure the output folder exists
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        # Ensure the normal and binary files exist
        for filename in [OUTPUT_FILE]:
            full_path = os.path.join(OUTPUT_FOLDER, filename)
            if not os.path.exists(full_path):
                # If the file doesn't exist, create it with an empty JSON object
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2)
                    
    def _parse_github_url(self, url):
        parsed = urlparse(url)
        parts = parsed.path.strip('/').split('/')
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {url}")
        return parts[0], parts[1].removesuffix('.git')

    def _get_default_branch(self):
        api = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        r = self.session.get(api)
        r.raise_for_status()
        return r.json()['default_branch']

    def _get_repo_tree(self):
        api = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
        r = self.session.get(api)
        r.raise_for_status()
        return r.json().get('tree', [])

    def _is_ignored(self, path):
        return any(part in IGNORE_DIRS for part in path.split('/'))

    def _is_normal_file(self, path):
        _, ext = os.path.splitext(path)
        return ext.lower() in NORMAL_EXTENSIONS
    
    def _is_executable_file(self, path):
        """Check if the file is an executable based on its extension."""
        _, ext = os.path.splitext(path)
        return ext.lower() in BINARY_EXTENSIONS
    
    def _is_binary_file(self, path):
        _, ext = os.path.splitext(path)
        if ext.lower() in BINARY_EXTENSIONS:
            return True
        # If no extension, check for binary signatures (magic numbers)
        if not ext:
            return True
        return False

    def fetch(self):
        print("[*] Fetching repo tree...")
        files = self._get_repo_tree()
        normal_files, binaries = [], []
        normal_paths = set()

        idx = 1
        for item in files:
            if item['type'] != 'blob':
                continue
            path = item['path']
            if self._is_ignored(path):
                continue

            if self._is_normal_file(path):
                print(f"[+] Found normal file: {path}")
                content = self._fetch_raw_content(path)
                size = len(content.encode('utf-8'))
                normal_files.append({
                    "id": idx,
                    "path": path,
                    "contents": content,
                    "file_size": size
                })
                normal_paths.add(path)
                idx += 1

        return normal_files, files, normal_paths
    
    def fetch_binaries(self, all_files, normal_paths):
        binaries_data = []
        idx = 1

        for item in all_files:
            if item['type'] != 'blob':
                continue
            path = item['path']

            # Skip files already processed as normal or ignored
            if path in normal_paths or self._is_ignored(path):
                continue

            if self._is_binary_file(path):  # Only process binary files
                print(f"[⚡] Found binary file: {path}")
                raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"

                # If the file is executable, we process it for hashing
                if self._is_executable_file(path):  # Only hash executable files
                    file_hash = sha256_file(raw_url)  # Fallback to hash the whole file directly
                    binaries_data.append({
                        "id": idx,
                        "fileName": os.path.basename(path),
                        "path": raw_url,
                        "sha256": file_hash,
                    })
                    idx += 1

        return binaries_data


    def _fetch_raw_content(self, path):
        raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
        r = self.session.get(raw_url)
        r.raise_for_status()
        return r.text

    def save_json(self, filename, normal_files, binaries):
        """Save both normal files and binary files to a single JSON file."""
        # Ensure the necessary files and folder exist
        self.create_files()

        # Prepare the data to be written
        data = {
            "repositoryName": self.repo_name,
            "scanDate": datetime.now().isoformat() + "Z",
            "files": normal_files,
            "binaries": binaries
        }

        # Write the data to the file
        full_path = os.path.join(OUTPUT_FOLDER, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"[✅] Wrote {len(normal_files) + len(binaries)} items to {filename}")

    def run(self):
        normal_files, all_files, normal_paths = self.fetch()
        binaries = self.fetch_binaries(all_files, normal_paths)
        
        if binaries:
            print(f"[⚡] Found {len(binaries)} binary files.")
        else:
            print("[⚡] No binary files found.")
        # Save both normal files and binaries into one file
        self.save_json(OUTPUT_FILE, normal_files, binaries)

# ===== Main Entrypoint =====
def main():
    parser = argparse.ArgumentParser(description="Scan GitHub repo for files and binaries.")
    parser.add_argument('repo_url', help="Repo URL (e.g. https://github.com/owner/repo)")
    args = parser.parse_args()

    scanner = GitHubScanner(args.repo_url)
    scanner.run()

if __name__ == '__main__':
    main()
