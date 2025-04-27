# SecureAI 
*(Cybersecurity for AI Deployments Track)*

An AI-powered tool that scans a public GitHub repository, identifies potential security vulnerabilities, outdated packages, and malicious binaries, explains each one in plain English, and provides actionable remediation tips — all with a focus on developer usability and beautiful UX.

---

## Frontend
- **Framework**: React, Tailwind CSS
- **Features**:
  - Hero page with GitHub repository input form
  - Processing animation with cybersecurity-themed visuals
  - Results dashboard with severity heatmap
  - Collapsible vulnerability sections with AI-suggested fixes
  - Notifies of any outdated packages
  - Identifies potential malicious binaries

---

## Backend
- **Framework**: Python, FastAPI
- **Capabilities**:
  - GitHub REST API integration (fetch repo files)
  - Code parsing and preprocessing
  - Gemini 2.0 Flash integration (AI-based vulnerability detection)
  - MetaDefender integration (malware and binary file scanning)

---

## Tech Stack
- Python
- FastAPI
- React
- Tailwind CSS
- Gemini 2.0 Flash integration (for AI code analysis)
- MetaDefender (for malware/binary scan)
- GitHub REST API

---

## Getting Started


### 1. Clone the repository

```sh
git clone https://github.com/Jeeevii/SecureAI.git
```

### 2. Run backend server

```sh
# Change directory to backend
cd backend/

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # (On Windows: venv\Scripts\activate)

# Install required backend dependencies 
pip install -r requirements.txt

# Run the backend server
python server.py
```

### 3. Run frontend server

```sh
# Change directory to frontend
cd frontend/

# Install required frontend dependencies 
npm install

# Run the frontend server
npm run dev
```

### 4. View the application

- **Frontend URL:** http://localhost:3000
- **Backend URL:** http://localhost:8000

---

## Example Workflow
1. User inputs public GitHub repo URL.
2. Backend parses repo files.
3. Files are scanned in chunks by Gemini.
4. Vulnerabilities are detected and explained.
5. Malware scanning on binaries with MetaDefender.
6. Results are presented in a sleek, actionable dashboard.
7. Optionally export full report as a PDF.