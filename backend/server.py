from fastapi import FastAPI, HTTPException
from github_scanner import fetch_repo_files

app = FastAPI()

@app.post("/scan")
async def scan_repo(request: RepoRequest):
    repo_url = request.repo_url
    if not repo_url.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Invalid GitHub URL.")
    
    try:
        files = fetch_repo_files(repo_url)
        return {
            "message": f"Found {len(files)} scannable files.",
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=8000, reload=True)