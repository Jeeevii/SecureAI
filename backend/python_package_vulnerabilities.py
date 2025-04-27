import json
import os
import re
import subprocess
import sys
from safety_parser import SafetyReportParser

"""
Module: safety_scan_and_extract.py

Provides a single function `scan_and_extract(output_path)` which:
  - Reads requirements from json_output/repo_packages.json
  - Runs Safety to generate a raw JSON report
  - Writes raw report to output_path
  - Parses and simplifies vulnerabilities via SafetyReportParser
  - Overwrites output_path with simplified list
  - Returns the simplified vulnerabilities list

If no requirements.txt is found, writes an empty array to output_path.

When invoked as a script, supports an optional --output argument.
"""
REPO_PKGS_PATH = os.path.join("json_output", "repo_packages.json")

def collect_reqs() -> list:
    """
    Read json_output/repo_packages.json and return a flat list of requirement specs,
    splitting on whitespace and ignoring comments.
    """
    if not os.path.isfile(REPO_PKGS_PATH):
        return []
    with open(REPO_PKGS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    reqs = []
    for entry in data.get("files", []):
        if entry.get("path", "").endswith("requirements.txt"):
            tokens = re.split(r"\s+", entry.get("contents", "").strip())
            reqs.extend(t for t in tokens if t and not t.startswith("#"))
    return reqs

def run_safety(reqs: list) -> str:
    """
    Run `safety check --stdin --json` on the given reqs list and return raw JSON string.
    """
    proc = subprocess.run(
        ["safety", "check", "--stdin", "--json"],
        input="\n".join(reqs).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.stderr:
        sys.stderr.write(proc.stderr.decode(errors="ignore"))
    raw = proc.stdout.decode(errors="ignore")
    m = re.search(r"[\[\{]", raw)
    return raw[m.start():] if m else raw

def scan_and_extract(output_path: str = os.path.join("json_output", "safety.json")) -> list:
    """
    Perform the full Safety scan and extraction pipeline, always reading
    from json_output/repo_packages.json.

    Args:
      output_path: File to write both raw and simplified reports

    Returns:
      A list of simplified vulnerability dicts.
    """
    reqs = collect_reqs()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not reqs:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []
    raw = run_safety(reqs)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(raw)
    try:
        parser = SafetyReportParser(raw)
    except TypeError:
        parser = SafetyReportParser.from_file(output_path)
    simplified = parser.get_vulnerabilities()
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(simplified, f, indent=2)
    return simplified


def parse_requirements_string(requirements_content: str) -> list:
    """
    Parse a requirements.txt string content and return a list of requirement specs.
    """
    tokens = re.split(r"\s+", requirements_content.strip())
    return [t for t in tokens if t and not t.startswith("#")]

def scan_requirements_string(requirements_content: str) -> dict:
    """
    Analyze a requirements string for vulnerabilities and return the results as a dict.
    
    Args:
        requirements_content: String content of requirements.txt
        
    Returns:
        A dict containing the simplified vulnerability data
    """
    reqs = parse_requirements_string(requirements_content)
    
    if not reqs:
        return {"vulnerabilities": []}
    
    raw = run_safety(reqs)
    try:
        parser = SafetyReportParser(raw)
    except TypeError:
        temp_path = os.path.join("json_output", "temp_safety.json")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(raw)
        parser = SafetyReportParser.from_file(temp_path)
        os.remove(temp_path)
    
    simplified = parser.get_vulnerabilities()
    return {"vulnerabilities": simplified}

if __name__ == '__main__':
    import argparse
    cli = argparse.ArgumentParser(
        description="Run Safety scan on json_output/repo_packages.json and extract simplified vulnerabilities"
    )
    cli.add_argument(
        "-o", "--output",
        default=os.path.join("json_output", "safety.json"),
        help="File to write the raw and simplified Safety JSON report"
    )
    args = cli.parse_args()
    simplified = scan_and_extract(args.output)
    print(f" Output written to {args.output}")
