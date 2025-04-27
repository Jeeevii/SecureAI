import json
import groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found!")

client = groq.Groq(api_key=api_key)

def validate_vulnerabilities(vulnerabilities_path):
    """ Validate each vulnerability in the JSON file using Groq """
    try:
        with open(vulnerabilities_path, 'r') as f:
            vulnerabilities = json.load(f)

        print(f"Validating {len(vulnerabilities['issues'])} vulnerabilities using Groq...")
        for vuln in vulnerabilities['issues']:
            is_valid = validate_vulnerability_with_groq(vuln)
            if not is_valid:
                vulnerabilities['issues'].remove(vuln)

        with open(vulnerabilities_path, 'w') as f:
            json.dump(vulnerabilities, f, indent=2)

    except Exception as e:
        print(f"Error loading or validating vulnerabilities: {e}")

def validate_vulnerability_with_groq(vuln):
    """ Validate a single vulnerability with Groq """
    
    query = f"""
    Please validate the following vulnerability based on your security standards and detection rules:
    {json.dumps(vuln, indent=2)}
    """

    try:
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": query}],
            temperature=0.6,
            max_completion_tokens=1024,
            top_p=0.95,
            stream=True,
            reasoning_format="raw"
        )

        collected_response = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            collected_response += content

        if "false positive" in collected_response.lower():
            return False
        return True

    except Exception as e:
        print(f"Error querying Groq: {e}")
        return False  


if __name__ == "__main__":
    validate_vulnerabilities("json_output/vulnerabilities.json")

