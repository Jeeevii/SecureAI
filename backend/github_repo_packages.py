import sys
import argparse
import requests
import json
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor

class RepoFileFetcher:
    ALLOWED_FILES = {'package-lock.json', 'requirements.txt'}
    DEFAULT_IGNORE_DIRS = {'node_modules', '.git', '.md', '.pdf', '.css', '.json'}

    def __init__(self, repo_url, output='repo_packages.json'):
        self.owner, self.repo = self._parse_github_url(repo_url)
        self.output = output
        self.session = requests.Session()
        self.branch = self._get_default_branch()
        self.ignore_dirs = self.DEFAULT_IGNORE_DIRS

    @staticmethod
    def _parse_github_url(url):
        parsed = urlparse(url)
        parts = parsed.path.strip('/').split('/')
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub URL: {url}")
        owner, repo = parts[0], parts[1].removesuffix('.git')
        return owner, repo

    def _get_default_branch(self):
        api = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        r = self.session.get(api)
        r.raise_for_status()
        return r.json().get('default_branch')

    def _get_all_files(self):
        api = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{self.branch}?recursive=1"
        r = self.session.get(api)
        r.raise_for_status()
        tree = r.json().get('tree', [])
        return [item for item in tree if item.get('type') == 'blob']

    def _is_allowed(self, path):
        filename = os.path.basename(path)
        if filename not in self.ALLOWED_FILES:
            return False
        if any(part in self.ignore_dirs for part in path.split('/')):
            return False
        return True

    def _get_raw_content(self, path):
        raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
        r = self.session.get(raw_url)
        r.raise_for_status()
        return r.text

    def _get_file_size(self, path):
        raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
        r = self.session.head(raw_url)
        r.raise_for_status()
        return int(r.headers.get('Content-Length', 0))

    @staticmethod
    def _sanitize_content(text):
        # return text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        return text

    def fetch_file_data(self, idx, item):
        path = item.get('path')

        if not self._is_allowed(path):
            return None
        
        try:
            raw = self._get_raw_content(path)
            content = self._sanitize_content(raw)
            file_size = self._get_file_size(path)
            print("Getting: ", path)
        except requests.HTTPError:
            content = ''
            file_size = 0
        return {'id': idx, 'path': path, 'contents': content, 'file_size': file_size}

    def fetch(self):
        files = self._get_all_files()
        data = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.fetch_file_data, idx + 1, item) for idx, item in enumerate(files)]
            for future in futures:
                result = future.result()
                if result:
                    data.append(result)

        return data

    def write_json(self, data):
        num_files = len(data)
        json_data = {
            "num_files": num_files,
            "files": data
        }
        raw_json = json.dumps(json_data, ensure_ascii=False, indent=2)
        with open(self.output, 'w', encoding='utf-8') as f:
            f.write(raw_json)

    def run(self):
        data = self.fetch()
        self.write_json(data)
        print(f"Wrote {len(data)} entries to {self.output}")

def main():
    parser = argparse.ArgumentParser(
        description="Fetch allowed files from a GitHub repo and write sanitized contents to JSON."
    )
    parser.add_argument('repo_url', help="e.g. https://github.com/owner/repo")
    parser.add_argument('-o', '--output', default='repo_packages.json',
                        help="Output JSON file (default: repo_packages.json)")
    args = parser.parse_args()
    try:
        fetcher = RepoFileFetcher(args.repo_url, output=args.output)
        fetcher.run()
    except Exception as e:
        sys.exit(e)

if __name__ == '__main__':
    main()