from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from pydantic import BaseModel

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
async def get_vulnerabilities(repo: RepositoryRequest = Body(...)):
    try:
        vulnerabilities_path = "vulnerabilities.json"
        
        if not os.path.exists(vulnerabilities_path):
            raise HTTPException(status_code=404, detail="Vulnerabilities file not found")
            
        with open(vulnerabilities_path, 'r') as file:
            vulnerabilities = json.load(file)
            
        # Add the repository URL to the response (useful for displaying in the UI)
        vulnerabilities["repositoryUrl"] = repo.url
            
        return JSONResponse(content=vulnerabilities)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error retrieving vulnerabilities: {str(e)}")
    
if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=8000, reload=True)

