from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/scan")
async def scan_repo(repo_url: str):
    return {"message": f"Scanning repository at {repo_url}"}
    
if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=8000, reload=True)

    