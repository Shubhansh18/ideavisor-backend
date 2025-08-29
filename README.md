# VentureAI Backend

This is the backend service for IdeaVisor, an AI-Powered Startup Validation Platform. It provides the core logic for analyzing startup ideas using AI models and generating comprehensive validation reports.

## Features

*   **AI-Powered Analysis:** Integrates with AI models (via OpenRouter) to analyze startup ideas based on various frameworks (TAM-SAM-SOM, YC Criteria, Founder-Market Fit, Risk Assessment, Financial Projections, Action Plan).
*   **Asynchronous Processing:** Handles analysis requests asynchronously, allowing for polling of report status.
*   **Structured Reporting:** Generates detailed validation reports in a structured JSON format.
*   **Robust Error Handling:** Implements centralized and informative exception handling for various failure scenarios.
*   **PDF Resume Integration:** Extracts text from PDF resume files for founder background analysis.
*   **CORS Enabled:** Configured for cross-origin requests to support frontend integration.

## Technologies Used

*   **FastAPI:** High-performance web framework for building APIs.
*   **Pydantic:** Data validation and settings management.
*   **OpenAI Python Client:** For interacting with OpenRouter AI models.
*   **python-dotenv:** For managing environment variables.
*   **PyPDF2:** For PDF parsing.
*   **Uvicorn:** ASGI server for running the FastAPI application.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd AI Idea Validator/Backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv validateEnv
    # On Windows
    .\validateEnv\Scripts\activate
    # On macOS/Linux
    source validateEnv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, you'll need to create it with `fastapi`, `uvicorn`, `openai`, `python-dotenv`, `PyPDF2`, etc.)*

4.  **Configure Environment Variables:**
    Create a `.env` file in the `Backend/` directory with your OpenRouter API key:
    ```
    OPENROUTER_API_KEY="your_openrouter_api_key_here"
    ```
    You can obtain an API key from [OpenRouter](https://openrouter.ai/).

5.  **Run the Application:**
    ```bash
    uvicorn app.main:app --host 127.0.0.1 --port 8000
    ```
    The API will be accessible at `http://127.0.0.1:8000`.

## API Endpoints

*   **GET /**
    *   **Description:** Root endpoint, returns a welcome message and API status.
    *   **Response:** `{"message": "VentureAI API - Startup Validation Platform", "status": "active"}`

*   **POST /api/v1/analyze**
    *   **Description:** Analyzes a startup idea and initiates the validation report generation.
    *   **Method:** `POST`
    *   **Content-Type:** `multipart/form-data`
    *   **Form Fields:**
        *   `idea` (str): Description of the startup idea (min 10 chars).
        *   `customer` (str): Target customer description (min 10 chars).
        *   `problem` (str): Problem being solved (min 10 chars).
        *   `solution` (str): Proposed solution (min 10 chars).
        *   `background` (str, optional): Founder's background (min 10 chars if provided).
        *   `resume_file` (file, optional): PDF resume file for founder background.
    *   **Responses:**
        *   `200 OK`: `{"report_id": "uuid", "status": "completed"}` (if analysis is quick)
        *   `200 OK`: `{"report_id": "uuid", "status": "clarification_needed", "message": "..."}` (if input is insufficient)
        *   `500 Internal Server Error`: Structured error response (e.g., `{"ok": false, "error": {"code": "ai_analysis_failed", "message": "..."}}`)

*   **GET /api/v1/report/{report_id}**
    *   **Description:** Retrieves the status or the full validation report for a given `report_id`.
    *   **Method:** `GET`
    *   **Path Parameter:** `report_id` (str) - The UUID of the report.
    *   **Responses:**
        *   `200 OK`: `{"status": "processing", "progress": "AI analysis in progress..."}` (if still processing)
        *   `200 OK`: `{"status": "completed", "analysis": {...}}` (full report data)
        *   `200 OK`: `{"status": "clarification_needed", "message": "..."}` (if clarification was requested)
        *   `200 OK`: `{"status": "failed", "error": "..."}` (if analysis failed)
        *   `404 Not Found`: `{"detail": "Report with ID 'uuid' not found."}`

## Error Handling

The backend implements robust, centralized exception handling. Custom exceptions (`AIAnalysisError`, `ReportError`) are used to categorize issues, and dedicated handlers ensure structured JSON error responses are returned to the client, preventing sensitive internal details from being exposed. All critical errors are logged on the server side.
