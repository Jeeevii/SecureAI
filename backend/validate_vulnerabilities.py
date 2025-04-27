import json
import groq
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found!")

# Groq client setup
client = groq.Groq(api_key=api_key)

def validate_vulnerabilities(vulnerabilities_path):
    """ Validate each vulnerability in the JSON file using Groq """
    try:
        with open(vulnerabilities_path, 'r') as f:
            vulnerabilities = json.load(f)

        print(f"Validating {len(vulnerabilities['issues'])} vulnerabilities using Groq...")

        # Iterate over each vulnerability to validate it
        for vuln in vulnerabilities['issues']:
            # Validate the vulnerability using Groq
            is_valid = validate_vulnerability_with_groq(vuln)
            if not is_valid:
                # If a vulnerability is invalid (false positive), remove it from the list
                print(f"Removing invalid vulnerability: {vuln['id']}")
                vulnerabilities['issues'].remove(vuln)

        # Save the updated list of vulnerabilities (removing false positives)
        with open(vulnerabilities_path, 'w') as f:
            json.dump(vulnerabilities, f, indent=2)

    except Exception as e:
        print(f"Error loading or validating vulnerabilities: {e}")

def validate_vulnerability_with_groq(vuln):
    """ Validate a single vulnerability with Groq """
    
    # Prepare the query for Groq to validate this vulnerability
    query = f"""
    Please validate the following vulnerability based on your security standards and detection rules:
    {json.dumps(vuln, indent=2)}
    """

    try:
        # Make a Groq API call for validation
        completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": query}],
            temperature=0.6,
            max_completion_tokens=1024,
            top_p=0.95,
            stream=True,
            reasoning_format="raw"  # Keeping the raw response for debugging
        )

        # Process the streamed response from Groq
        collected_response = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            collected_response += content

        # TODO: Remove debug print: Show the full response for inspection 
        print("Groq response:", collected_response)

        # Check if Groq indicates this is a false positive
        if "false positive" in collected_response.lower():
            # Debug print: Show the decision logic
            print(f"Vulnerability {vuln['id']} is a false positive based on Groq response.")
            return False
        
        # Debug print: If not a false positive, confirm that it's valid
        print(f"Vulnerability {vuln['id']} is valid based on Groq response.")
        return True

    except Exception as e:
        print(f"Error querying Groq: {e}")
        return False  # Return False if an error occurs


# TODO: Call from server.py, not from here!
# Example usage:
# Call the validate_vulnerabilities function with your vulnerabilities JSON path
validate_vulnerabilities("json_output/vulnerabilities.json")
