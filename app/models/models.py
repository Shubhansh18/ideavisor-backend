from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Dict, Optional
from fastapi import Form, UploadFile
import PyPDF2
from io import BytesIO

class StartupIdea(BaseModel):
    idea: str = Field(..., min_length=10, max_length=1000)
    customer: str = Field(..., min_length=10, max_length=500)
    problem: str = Field(..., min_length=10, max_length=1000)
    solution: str = Field(..., min_length=10, max_length=1000)
    background: str = Field(..., min_length=10, max_length=5000)
    resume_file: Optional[UploadFile] = None
    
    @classmethod
    async def extract_text_from_pdf(cls, file: UploadFile) -> str:
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError('Only PDF files are supported')
            
        content = await file.read()
        pdf_file = BytesIO(content)
        
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
            return text.strip()
        except Exception as e:
            raise ValueError(f'Error reading PDF file: {str(e)}')

    @classmethod
    async def as_form(
        cls,
        idea: str = Form(...),
        customer: str = Form(...),
        problem: str = Form(...),
        solution: str = Form(...),
        background: str = Form(None),
        resume_file: UploadFile = None
    ):
        if resume_file:
            background = await cls.extract_text_from_pdf(resume_file)
        elif not background:
            raise ValueError('Either background text or resume_file must be provided')
            
        return cls(
            idea=idea,
            customer=customer,
            problem=problem,
            solution=solution,
            background=background,
            resume_file=resume_file
        )

    @validator('background')
    def background_must_not_be_empty(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('background must be at least 10 characters')
        return v

class ValidationReport(BaseModel):
    id: str
    startup_data: StartupIdea
    viability_score: float
    market_size: str
    competition_level: str
    time_to_market: str
    market_analysis: Dict
    risk_assessment: Dict
    recommendations: Dict
    financial_projections: Dict
    action_plan: Dict
    competitive_landscape: Dict
    founder_market_fit: Dict
    yc_criteria_assessment: Dict
    created_at: datetime
