import os
import json
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv
import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found!")

genai.configure(api_key=api_key)

# --- Constants ---
CHUNK_SIZE = 8000
CHUNK_OVERLAP = 500
CONTEXT_TAIL_LINES = 15
CONCURRENCY_LIMIT = 3

# --- Text Splitter Setup ---
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)

# --- Retry Decorator ---
@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(5))
async def safe_api_call(messages):
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = await model.generate_content_async(messages)
    return response.text

# --- File splitting function ---
def split_file_contents(contents):
    return splitter.split_text(contents)

# --- Analyze single file ---
async def analyze_file(file_info):
    file_path = file_info["path"]
    contents = file_info["contents"]

    print(f"Starting scan for: {file_path}")

    chunks = split_file_contents(contents)
    vulnerabilities = []

    lines = contents.splitlines()
    total_lines = len(lines)

    previous_tail = ""
    line_cursor = 0

    for idx, chunk in enumerate(chunks):
        print(f"Processing chunk {idx + 1}/{len(chunks)} of {file_path}")

        if previous_tail:
            chunk = previous_tail + "\n" + chunk

        current_lines = chunk.splitlines()
        chunk_start_line = line_cursor + 1

        prompt = f"""
            You are a world-class cybersecurity auditor analyzing source code part {idx + 1} of {len(chunks)} for file {file_path}.

            You must ONLY detect and report real, exploitable vulnerabilities.
            You must IGNORE non-security code quality, formatting, or style issues.

            When reviewing code, focus on:
            - Insecure code patterns (injection, auth flaws, access control)
            - Misuse of libraries or system calls
            - Hardcoded secrets, tokens, keys
            - Misconfigured Dockerfiles, open ports, unnecessary files
            - Malware-like behavior (downloads, writes, network calls)
            - CI/CD pipeline risks (unsafe scripts, unvalidated inputs)
            - AI model deployment risks (unsafe environment configs)

            If a vulnerability spans multiple chunks, note it and analyze the surrounding context carefully.

            Return ONLY a JSON array where each object includes:
            - "id" (unique integer ID starting from 1)
            - "fileName" (the filename)
            - "lineNumber" (first line of issue if known, else null)
            - "issueType" (short label)
            - "severity" (Low, Medium, High, Critical)
            - "description" (one paragraph why it's a real issue)
            - "codeSnippet" (minimal reproducing snippet)
            - "suggestedFix" (specific and practical)

            Return pure valid JSON array — no prose outside JSON.
            """

        try:
            response_content = await safe_api_call([
                {"role": "user", "parts": [prompt + "\n\nCode:\n" + chunk]}
            ])

            json_start = response_content.find('[')
            json_end = response_content.rfind(']') + 1
            parsed = json.loads(response_content[json_start:json_end])

            for vuln in parsed:
                clean_vuln = {
                    "id": None,  # To be assigned later
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

# --- Semaphore wrapper for controlled concurrency ---
async def sem_task(semaphore, task_func, *args):
    async with semaphore:
        return await task_func(*args)

# --- Main scanning function ---
async def find_vulnerabilities(input_file, output_file=None):
    with open(input_file, 'r') as f:
        file_data = json.load(f)

    all_vulnerabilities = []
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    tasks = [sem_task(semaphore, analyze_file, file_info) for file_info in file_data]
    results = await asyncio.gather(*tasks)

    for file_vulns in results:
        all_vulnerabilities.extend(file_vulns)

    for idx, vuln in enumerate(all_vulnerabilities, 1):
        vuln["id"] = idx

    output_data = {
        "repositoryName": os.getenv("REPOSITORY_NAME", "UnknownRepo"),
        "scanDate": datetime.now(timezone.utc).isoformat() + "Z",
        "issues": all_vulnerabilities
    }

    if output_file:
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
    else:
        print(json.dumps(output_data, indent=2))

    return output_data

# --- CLI Entry Point ---
def main():
    input_file = "json_output/repo_files.json"
    output_file = "json_output/vulnerabilities.json"

    print("Launching Secure Code Scanner...")
    asyncio.run(find_vulnerabilities(input_file, output_file))
    print(f"Analysis complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()
