# Page Pulse — Web Audit Tool

A lightweight, intelligent web auditing tool built with Python (FastAPI) and standard HTML/JS. Page Pulse instantly audits any target URL for performance metrics, SEO vitals, and extracts top semantic keywords using a custom Natural Language Processing (NLP) pipeline.

# Live Deployment Link
https://page-pulse-3lmb.onrender.com

## 🚀 Setup & Running Locally

1. **Clone the repository:**

   git clone <your-repo-link>
   cd page-pulse

2. Create a virtual environment and install dependencies:

    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    pip install -r requirements.txt

3.  Run the application:

    uvicorn main:app --reload

    Open your browser at http://127.0.0.1:8000.

4.  Run Unit Tests:

    pytest

    
(Note: This repository is equipped with a GitHub Actions CI/CD pipeline that automatically runs this test suite on every push to the main branch).

📜 API Contract
   Endpoint: GET /api/audit

   Query Parameter: url (string, required) - Note: The API auto-prepends https:// if the protocol is missing.

   Success Response (200 OK):

    {
      "url": "[https://example.com](https://example.com)",
      "status_code": 200,
      "response_time_ms": 142.5,
      "metrics": {
        "title": "Example Domain",
        "meta_description": "N/A",
        "h1_count": 1,
        "missing_alt_images_count": 0,
        "word_count": 32,
        "top_keywords": {
          "example": 2,
          "domain": 2,
          "illustrative": 1,
          "examples": 1,
          "documents": 1
        }
      }
    }

    Error Responses:

        400 Bad Request: Invalid URL format or non-HTML payload.

        502 Bad Gateway: Failed to connect to the provided domain.

        504 Gateway Timeout: Target server took too long to respond.

🏗️ Design Decisions

    FastAPI & Async HTTPX2: Chosen over Flask/Requests to leverage asynchronous I/O, allowing the server to handle URL audit requests concurrently without blocking worker threads. httpx2 was explicitly pinned to version 2.9.1 to ensure CI/CD and deployment stability.

    Intelligent Content Analysis (NLP): Instead of just returning a raw word count, the app processes the scraped DOM text through a custom tokenizer and stop-word filter using Python's native collections.Counter. This extracts the top 5 SEO keywords without relying on heavy external dependencies like spaCy, keeping the deployment container incredibly lightweight and fast.

    Decoupled Vanilla Frontend: Built with native HTML5/CSS3/JavaScript to eliminate heavy framework build steps (like React/Next.js). This ensures the frontend is highly performant and can be served instantly on free-tier cloud architectures.

    Automated CI/CD Pipeline: A GitHub Actions workflow (test.yml) was implemented to act as an automated quality gate, running the Pytest suite on every push to ensure code integrity before production deployment.


🤖 GenAI Usage Statement

   AI tools (specifically LLMs) were utilized during the development of this project as a pair-programming assistant. AI was primarily used to speed up the generation of boilerplates for the Pytest unit test suite, scaffold the initial CSS styling for the frontend, and draft standard Regex patterns for HTML attribute targeting.

   Following the initial generation, significant manual engineering and architectural overrides were applied:

    The HTTP request logic was manually refactored to catch strict timeout edge-cases and non-HTML response headers.

    The URL validation was upgraded to automatically inject missing https:// protocols, requiring manual restructuring of the Pytest failure-case expectations.

    The NLP keyword extraction logic and CI/CD .yml pipeline were explicitly directed, integrated, and integrated manually to elevate the project to production-ready standards.

    Package dependencies were manually audited and pinned (e.g., resolving httpx deprecation warnings by upgrading to httpx2==2.9.1) to ensure pipeline stability.