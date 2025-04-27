import sys
import argparse
import requests
import json
import os
from urllib.parse import urlparse

class RepoFileFetcher:
    DEFAULT_EXTENSIONS = {'.py', '.html', '.cpp', '.c', '.hpp', '.h', '.tsx', '.ts', '.js', '.jsx', 'Docker', '.yaml'}
    DEFAULT_IGNORE_DIRS = {'node_modules', '.git', '.md', '.pdf', '.css'}

    def __init__(self, repo_url, output='repo_files.json', allowed_extensions=None, ignore_dirs=None):
        self.owner, self.repo = self._parse_github_url(repo_url)
        self.output = output
        self.allowed_extensions = allowed_extensions or self.DEFAULT_EXTENSIONS
        self.ignore_dirs = ignore_dirs or self.DEFAULT_IGNORE_DIRS
        self.session = requests.Session()
        self.branch = self._get_default_branch()

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
        # Skip ignored directories and filter by extension
        if any(part in self.ignore_dirs for part in path.split('/')):
            return False
        _, ext = os.path.splitext(path)
        return ext.lower() in self.allowed_extensions

    def _get_raw_content(self, path):
        raw_url = f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{path}"
        r = self.session.get(raw_url)
        r.raise_for_status()
        return r.text

    @staticmethod
    def _sanitize_content(text):
        return text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')

    def fetch(self):
        files = self._get_all_files()
        data = []
        idx = 1
        for item in files:
            path = item.get('path')
            print("Getting: ", path)
            if not self._is_allowed(path):
                continue
            try:
                raw = self._get_raw_content(path)
                content = self._sanitize_content(raw)
            except requests.HTTPError:
                content = ''
            data.append({'id': idx, 'path': path, 'contents': content})
            idx += 1
        return data

    def write_json(self, data):
        raw_json = json.dumps(data, ensure_ascii=False, indent=2)
        # raw_json = raw_json.replace('\\"', '"')
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
    parser.add_argument('-o', '--output', default='/json_files/repo_files.json',
                        help="Output JSON file (default: repo_files.json)")
    args = parser.parse_args()
    try:
        fetcher = RepoFileFetcher(args.repo_url, output=args.output)
        fetcher.run()
    except Exception as e:
        sys.exit(e)


if __name__ == '__main__':
    main()