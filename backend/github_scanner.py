import sys
import argparse
import requests
import json
import os
from urllib.parse import urlparse

session = requests.Session()

ALLOWED_EXTENSIONS = {'.py', '.html', '.cpp', '.c', '.hpp', '.h', '.tsx', '.ts', '.js', '.jsx'}
IGNORE_DIRS = {'node_modules', '.git'}

def parse_github_url(url):
    parsed = urlparse(url)
    parts = parsed.path.strip('/').split('/')
    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub URL: {url}")
    owner, repo = parts[0], parts[1].removesuffix('.git')
    return owner, repo

def get_default_branch(owner, repo):
    api = f"https://api.github.com/repos/{owner}/{repo}"
    r = session.get(api)
    r.raise_for_status()
    return r.json().get('default_branch')

def get_all_files(owner, repo, branch):
    api = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    r = session.get(api)
    r.raise_for_status()
    tree = r.json().get('tree', [])
    return [item for item in tree if item.get('type') == 'blob']

def is_allowed(path):
    for part in path.split('/'):
        if part in IGNORE_DIRS:
            return False
    ext = os.path.splitext(path)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def get_raw_content(owner, repo, branch, path):
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    r = session.get(raw_url)
    r.raise_for_status()
    return r.text

def sanitize_content(text):
    return text.replace('\r\n', '').replace('\n', '').replace('\r', '')

def main():
    parser = argparse.ArgumentParser(
        description="Fetch only allowed file types from a GitHub repo and write sanitized contents to JSON."
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
    all_files = get_all_files(owner, repo, branch)
    data = []
    idx = 1
    for item in all_files:
        path = item.get('path')
        print("Doing: ", path)
        if not is_allowed(path):
            continue
        try:
            raw = get_raw_content(owner, repo, branch, path)
            content = sanitize_content(raw)
        except requests.HTTPError:
            content = ''
        data.append({'id': idx, 'path': path, 'contents': content})
        idx += 1

    output_path = args.output
    dirpath = os.path.dirname(output_path)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Wrote {len(data)} allowed file entries to {output_path}")
    except IOError as e:
        sys.exit(f"Error writing JSON file: {e}")

if __name__ == '__main__':
    main()
