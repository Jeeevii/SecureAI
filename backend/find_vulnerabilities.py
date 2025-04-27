import os
import json
import asyncio
import hashlib
from dotenv import load_dotenv
from datetime import datetime, timezone
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tenacity import retry, wait_random_exponential, stop_after_attempt
import aiohttp  # Needed for VirusTotal lookup

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
virustotal_api_key = os.getenv("VIRUSTOTAL_API_KEY")  # Add this to your .env file
if not api_key:
    raise ValueError("GEMINI_API_KEY not found!")

genai.configure(api_key=api_key)

# --- Model and Constants ---
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

CHUNK_SIZE = 8000
CHUNK_OVERLAP = 500
CONTEXT_TAIL_LINES = 15
CONCURRENCY_LIMIT = 5  # slight bump
LARGE_FILE_SIZE_THRESHOLD = 5000

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)

# --- Gemini API Call (optimized) ---
@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(5))
async def safe_api_call(model, messages):
    try:
        response = await model.generate_content_async(messages)
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        raise

# --- Split Text Helper ---
def split_file_contents(contents):
    return splitter.split_text(contents)

# --- Analyze One File ---
async def analyze_file(file_info, model):
    file_path = file_info["path"]
    contents = file_info["contents"]
    
    print(f"Starting scan for: {file_path}")
    
    chunks = split_file_contents(contents)
    vulnerabilities = []
    
    lines = contents.splitlines()
    previous_tail = ""
    line_cursor = 0

    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx + 1}/{len(chunks)} of {file_path}")

        if previous_tail:
            chunk = previous_tail + "\n" + chunk
        
        current_lines = chunk.splitlines()

        prompt = f"""
        You are a world-class cybersecurity auditor analyzing source code part {idx + 1} of {len(chunks)} for file {file_path}.

        Only detect REAL, exploitable vulnerabilities. Ignore non-security stuff.

        Focus on:
        - Injection, auth flaws, bad access control
        - Misuse of libraries or syscalls
        - Hardcoded secrets
        - Malware-like behavior (downloads, network ops)
        - CI/CD unsafe scripts
        - Unsafe AI model deployment configs

        Return ONLY a valid JSON array like:
        [{{
            "id": 1,
            "fileName": "example.py",
            "lineNumber": 42,
            "issueType": "SQL Injection",
            "severity": "High",
            "description": "Detailed desc here",
            "codeSnippet": "snippet here",
            "suggestedFix": "Specific fix here"
        }}]
        """

        try:
            response_content = await safe_api_call(model, [
                {"role": "user", "parts": [prompt + "\n\nCode:\n" + chunk]}
            ])

            json_start = response_content.find('[')
            json_end = response_content.rfind(']') + 1
            parsed = json.loads(response_content[json_start:json_end])

            for vuln in parsed:
                clean_vuln = {
                    "id": None,  
                    "fileName": file_path,
                    "lineNumber": vuln.get("lineNumber") if isinstance(vuln.get("lineNumber"), int) else None,
                    "issueType": vuln.get("issueType") or "Unknown Issue",
                    "severity": vuln.get("severity") or "Medium",
                    "description": vuln.get("description") or "No description provided.",
                    "codeSnippet": vuln.get("codeSnippet") or "No snippet provided.",
                    "suggestedFix": vuln.get("suggestedFix") or "No fix suggested."
                }
                vulnerabilities.append(clean_vuln)

        except Exception as e:
            print(f"Error analyzing {file_path} chunk {idx + 1}: {e}")

        previous_tail = "\n".join(current_lines[-CONTEXT_TAIL_LINES:])
        line_cursor += len(current_lines) - CONTEXT_TAIL_LINES

    return vulnerabilities

# --- Semaphore Wrapper ---
async def sem_task(semaphore, task_func, model, *args):
    async with semaphore:
        return await task_func(*args, model)

# --- Main Scan ---
async def find_vulnerabilities(input_file, output_file=None):
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
    with open(input_file, 'r') as f:
        file_data = json.load(f)

    all_vulnerabilities = []
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    tasks = [sem_task(semaphore, analyze_file, model, file_info) for file_info in file_data["files"]]
    results = await asyncio.gather(*tasks)

    for file_vulns in results:
        all_vulnerabilities.extend(file_vulns)

    for idx, vuln in enumerate(all_vulnerabilities, 1):
        vuln["id"] = idx

    result_data = {
        "repositoryName": "TEMP",  # Add your repository name here
        "scanDate": datetime.now(timezone.utc).isoformat() + "Z",
        "issues": all_vulnerabilities
    }

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(result_data, f, indent=2)
    else:
        print(json.dumps(result_data, indent=2))

    return all_vulnerabilities

# --- Binary Hashing and VirusTotal Check ---
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

async def lookup_virustotal(file_hash):
    if not virustotal_api_key:
        print("VIRUSTOTAL_API_KEY not found, skipping VirusTotal lookup.")
        return None

    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {
        "x-apikey": virustotal_api_key
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"VirusTotal Lookup for {file_hash}: {data}")
                return data
            else:
                print(f"VirusTotal Error: {resp.status}")
                return None

# --- Main ---
def main():
    input_file = "json_output/repo_files.json"
    output_file = "json_output/vulnerabilities.json"

    print("Launching Secure Code + Binary Scanner...")
    asyncio.run(find_vulnerabilities(input_file, output_file))
    print(f"Analysis complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
