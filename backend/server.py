from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/scan")
async def scan_repo(repo_url: str):
    return {"message": f"Scanning repository at {repo_url}"}
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)