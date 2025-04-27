from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from pydantic import BaseModel
from github_scanner import RepoFileFetcher
from backend.vulnerability_detector import find_vulnerabilities
from check_packages import check_packages
from github_repo_packages import RepoFileFetcher as PackageRepoFileFetcher

class RepositoryRequest(BaseModel):
    url: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/vulnerabilities")
async def scan_repo(repo: RepositoryRequest = Body(...)):
    try:
        os.makedirs("json_output", exist_ok=True)
        
        temp_files_json = "json_output/repo_files.json"
        fetcher = RepoFileFetcher(repo.url, output=temp_files_json)
        fetcher.run()
        
        packages_json = "json_output/repo_packages.json"
        package_fetcher = PackageRepoFileFetcher(repo.url, output=packages_json)
        package_fetcher.run()
        
        vulnerabilities_path = "json_output/vulnerabilities.json"
        await find_vulnerabilities(temp_files_json, vulnerabilities_path)
        
        if not os.path.exists(vulnerabilities_path):
            raise HTTPException(status_code=500, detail="Failed to create vulnerabilities file")
            
        with open(vulnerabilities_path, 'r') as file:
            vulnerabilities = json.load(file)
        
        vulnerabilities["repositoryUrl"] = repo.url
        vulnerabilities["scanDate"] = os.path.getmtime(vulnerabilities_path)
        
        package_vulnerabilities = check_packages()
        vulnerabilities["packagesVulnerabilities"] = package_vulnerabilities
    
        return JSONResponse(content=vulnerabilities)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving vulnerabilities: {str(e)}")
    
if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=8000, reload=True)

