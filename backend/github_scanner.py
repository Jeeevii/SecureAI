import sys
import argparse
import requests
import json
import os
import hashlib
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
NORMAL_EXTENSIONS = {
    '.py', '.pyx', '.pyd', '.pyi', '.pyc',
    '.rs', '.rlib',
    '.html', '.htm', '.scss', '.sass', '.less',
    '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte',
    '.cpp', '.c', '.cc', '.cxx', '.h', '.hpp', '.hxx',
    '.java', '.kt', '.kts', '.groovy',
    '.cs', '.vb', '.fs', '.go',
    '.rb', '.erb', '.rake',
    '.php', '.phtml', '.php3', '.php4', '.php5',
    '.swift', '.m', '.mm',
    '.sh', '.bash', '.zsh', '.fish',
    '.yaml', '.yml', '.toml', '.xml', '.ini', '.config',
    'Dockerfile', '.dockerfile', '.dockerignore',
    '.sql', '.graphql', '.proto',
    '.scala', '.sbt',          
    '.lua',                    
    '.r', '.rmd',               
    '.dart',                    
    '.ex', '.exs',             
    '.hs', '.lhs',               
    '.pl', '.pm',               
    '.jsp', '.aspx', '.cshtml',  
    '.ipynb',                   
    '.pas', '.pp',              
    'Makefile',                  
}

BINARY_EXTENSIONS = {
    '.exe', '.dll', '.sys', '.bin', '.dat', '.msi', '.apk', '.so', '.dmg',
    '.jar', '.war',            
    '.wasm',                     
    '.pyc',                     
    '.class',                                
    '.iso', '.img',              
}

IGNORE_DIRS = {
    'node_modules', '.git', 'tests', 'static', 'dist', 'build', 
    'vendor', 'bower_components', 'coverage', '__pycache__', 
    '.venv', 'venv', 'env',      
    '.idea', '.vscode',          
    'target', 'out',            
    'logs', 'log',             
    'tmp', 'temp',               
    'cache', '.cache',           
    'assets', 'public/assets',   
    'terraform.tfstate.d',       
    '.pytest_cache',             
    '.next', '.nuxt'             
}

MAX_LINE_COUNT = 8000
def sha256_file(url, hash_algorithm="sha256"):
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            hasher = hashlib.new(hash_algorithm)
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    hasher.update(chunk)
            return hasher.hexdigest()
    except requests.exceptions.RequestException as e:
        print(f"[x] Error hashing file: {e}")
        return None

class RepoFileFetcher:
    def __init__(self, repo_url, output='repo_files.json'):
        self.owner, self.repo = self._parse_github_url(repo_url)
        self.output = output
        self.allowed_extensions = NORMAL_EXTENSIONS
        self.ignore_dirs = IGNORE_DIRS
        self.session = requests.Session()
        self.branch = self._get_default_branch()

    @staticmethod
    def _parse_github_url(url):
        parsed = urlparse(url)
        parts = parsed.path.strip('/').split('/')
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {url}")
        return parts[0], parts[1].removesuffix('.git')

    def _get_default_branch(self):
        api = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        r = self.session.get(api)
        r.raise_for_status()
        return r.json().get('default_branch')

    def _get_repo_tree(self):
        api = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
        r = self.session.get(api)
        r.raise_for_status()
        return r.json().get('tree', [])

    def _is_ignored(self, path):
        parts = path.split('/')
        return any(part in self.ignore_dirs for part in parts)

    def _is_allowed(self, path):
        _, ext = os.path.splitext(path)
        return ext.lower() in self.allowed_extensions or path in self.allowed_extensions

    def _is_binary_file(self, path):
        _, ext = os.path.splitext(path)
        if ext.lower() in BINARY_EXTENSIONS:
            return True
        if not ext:
            return True  
        return False

    def _fetch_text_content(self, path):
        raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
        r = self.session.get(raw_url)
        r.raise_for_status()
        return r.text

    def _fetch_file_size(self, path):
        raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
        r = self.session.head(raw_url)
        r.raise_for_status()
        return int(r.headers.get('Content-Length', 0))

    def fetch_normal_file(self, idx, item):
        path = item.get('path')
        if self._is_ignored(path):
            return None
        if not self._is_allowed(path):
            return None

        try:
            raw = self._fetch_text_content(path)
            file_size = self._fetch_file_size(path)
            line_count = raw.count('\n') + (not raw.endswith('\n') and len(raw) > 0)
            
            # Skip files with more than MAX_LINE_COUNT lines
            if line_count > MAX_LINE_COUNT:
                print(f"[!] Skipping large file: {path} ({line_count} lines)")
                return None
                
            print(f"[+] Normal file: {path}")
        except requests.HTTPError:
            return None

        return {
            'id': idx,
            'path': path,
            'contents': raw,
            'file_size': file_size,
            'line_count': line_count
        }

    def fetch_binary_file(self, idx, item):
        path = item.get('path')
        if self._is_ignored(path):
            return None
        if self._is_allowed(path):
            return None
        if not self._is_binary_file(path):
            return None

        raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
        file_hash = sha256_file(raw_url)
        print(f"[⚡] Binary file: {path}")

        return {
            'id': idx,
            'fileName': os.path.basename(path),
            'path': raw_url,
            'sha256': file_hash
        }

    def fetch(self):
        files = self._get_repo_tree()
        normal_files, binaries = [], []

        idx_normal = 1
        idx_binary = 1

        with ThreadPoolExecutor() as executor:
            futures = []
            for item in files:
                if item.get('type') != 'blob':
                    continue
                futures.append(executor.submit(self.fetch_normal_file, idx_normal, item))
                futures.append(executor.submit(self.fetch_binary_file, idx_binary, item))
                idx_normal += 1
                idx_binary += 1

            for future in futures:
                result = future.result()
                if result:
                    if 'contents' in result:
                        normal_files.append(result)
                    elif 'sha256' in result:
                        binaries.append(result)

        return normal_files, binaries

    def save_json(self, normal_files, binaries):

        data = {
            "repositoryName": self.repo,
            "scanDate": datetime.now().isoformat() + "Z",
            "files": normal_files,
            "binaries": binaries
        }

        with open(self.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f" Wrote {len(normal_files)} normal files and {len(binaries)} binaries to {self.output}")

    def run(self):
        normal_files, binaries = self.fetch()
        self.save_json(normal_files, binaries)

# ===== Main Entrypoint =====
def main():
    parser = argparse.ArgumentParser(description="Scan GitHub repo for files and binaries.")
    parser.add_argument('repo_url', help="Repo URL (e.g. https://github.com/owner/repo)")
    parser.add_argument('-o', '--output', default='repo_files.json',
                        help="Output JSON file (default: repo_files.json)")
    args = parser.parse_args()

    try:
        scanner = RepoFileFetcher(args.repo_url, output=args.output)
        scanner.run()
    except Exception as e:
        sys.exit(e)

if __name__ == '__main__':
    main()
