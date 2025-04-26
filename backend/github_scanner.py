"""
get_repo_files_to_json.py

Recursively lists all files in a public GitHub repository and writes their paths and sanitized contents
into a JSON file, assigning each file a unique integer ID and stripping newline characters from content.

Usage:
    python get_repo_files_to_json.py https://github.com/owner/repo [-o output.json]
"""

import sys
import argparse
import requests
import json
from urllib.parse import urlparse

def parse_github_url(url):
    """Extract owner and repo name from a GitHub URL."""
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub URL: {url}")
    owner, repo = parts[0], parts[1].removesuffix('.git')
    return owner, repo

def get_default_branch(owner, repo):
    """Fetch the repository's default branch name."""
    api = f"https://api.github.com/repos/{owner}/{repo}"
    r = requests.get(api)
    r.raise_for_status()
    return r.json()['default_branch']

def get_all_files(owner, repo, branch):
    """
    Use the Git Trees API with recursive=1 to get the full tree.
    Returns a list of blobs (files) with their paths.
    """
    api = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    r = requests.get(api)
    r.raise_for_status()
    tree = r.json().get('tree', [])
    return [item for item in tree if item['type'] == 'blob']

def get_raw_content(owner, repo, branch, path):
    """Fetch a file's raw content from raw.githubusercontent.com."""
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    r = requests.get(raw_url)
    r.raise_for_status()
    return r.text

def sanitize_content(text):
    """Remove newline characters to produce a single-line content string."""
    return text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')

def main():
    parser = argparse.ArgumentParser(
        description="List all files in a GitHub repo and write their sanitized contents to JSON."
    )
    parser.add_argument('repo_url', help="e.g. https://github.com/owner/repo")
    parser.add_argument('-o', '--output', default='repo_files.json',
                        help="Output JSON file path (default: repo_files.json)")
    args = parser.parse_args()
    try:
        owner, repo = parse_github_url(args.repo_url)
    except ValueError as e:
        sys.exit(e)
    branch = get_default_branch(owner, repo)
    files = get_all_files(owner, repo, branch)
    data = []
    for idx, item in enumerate(files, start=1):
        path = item['path']
        try:
            raw = get_raw_content(owner, repo, branch, path)
            content = sanitize_content(raw)
        except requests.HTTPError:
            content = ''
        data.append({
            'id': idx,
            'path': path,
            'contents': content
        })
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Wrote {len(data)} file entries to {args.output}")
    except IOError as e:
        sys.exit(f"Error writing JSON file: {e}")

if __name__ == '__main__':
    main()
