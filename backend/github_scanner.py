import requests
from urllib.parse import urlparse

class GitHubRepoLister:
    def __init__(self, repo_url: str):
        self.repo_url = repo_url
        self.owner, self.repo = self._parse_url()
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"

    def _parse_url(self):
        """Extract owner and repo name from the GitHub URL."""
        parsed = urlparse(self.repo_url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2:
            raise ValueError("Invalid GitHub repo URL format. Expected format: https://github.com/owner/repo")
        return parts[0], parts[1]

    def _get_repo_tree(self):
        """Get the full tree (list of files) from the repo."""
        url = f"{self.base_url}/git/trees/main?recursive=1"  # default branch = main
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch repo tree: {response.text}")
        return response.json()["tree"]

    def list_files(self):
        """List all files in the repo."""
        tree = self._get_repo_tree()
        files = [item["path"] for item in tree if item["type"] == "blob"]
        return files

valid_repos = [
    'https://github.com/Jeeevii/SlugRush',
    'https://github.com/Jeeevii/portfolio',
    'https://github.com/Jeeevii/Jeeevii'
]
# Example usage
if __name__ == "__main__":
    url = valid_repos[0] # example public repo
    lister = GitHubRepoLister(url)
    files = lister.list_files()
    print("Files found:")
    for f in files:
        print(f)
