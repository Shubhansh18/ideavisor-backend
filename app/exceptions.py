# app/exceptions.py

class AIAnalysisError(Exception):
    """Custom exception for errors related to the AI analysis service."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ReportError(Exception):
    """Custom exception for errors related to report generation or retrieval."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
