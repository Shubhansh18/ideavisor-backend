from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import httpx
import json
import os
import re
from datetime import datetime
import uuid
import asyncio
from pathlib import Path
import PyPDF2
import io

# Create FastAPI app
app = FastAPI(
    title="VentureAI API",
    description="AI-Powered Startup Validation Platform",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

client = OpenAI(
  base_url=OPENROUTER_BASE_URL,
  api_key=OPENROUTER_API_KEY,
)

# Data models
class StartupIdea(BaseModel):
    idea: str = Field(..., min_length=10, max_length=1000)
    customer: str = Field(..., min_length=5, max_length=500)
    problem: str = Field(..., min_length=10, max_length=1000)
    solution: str = Field(..., min_length=10, max_length=1000)
    background: str = Field(..., min_length=5, max_length=5000)
    
class ValidationReport(BaseModel):
    id: str
    startup_data: StartupIdea
    viability_score: float
    market_size: str
    competition_level: str
    time_to_market: str
    market_analysis: dict
    risk_assessment: dict
    recommendations: dict
    financial_projections: dict
    action_plan: dict
    created_at: datetime
    
# In-memory storage (replace with database for production)
reports_db = {}

# AI Analysis Service
class AIAnalysisService:
    def __init__(self):
        self.client = client
    
    async def analyze_startup(self, startup_data: StartupIdea) -> dict:
        """Analyze startup idea using AI models"""
        
        # Create comprehensive analysis prompt
        analysis_prompt = self._create_analysis_prompt(startup_data)
        
        try:
            # Call OpenRouter API with structured output
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",  # Using free DeepSeek R1 model
                messages=[
                    {
                        "role": "system",
                        "content": '''You are a senior startup analyst, advisor and venture capitalist with 20+ years of experience. 
                        Provide detailed, actionable startup validation analysis in valid JSON format.
                        Respond ONLY with a valid JSON object - no additional text or formatting.'''
                    },
                    {
                        "role": "user", 
                        "content": analysis_prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7,
                response_format={"type": "json_object"}  # Enforce JSON output
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise HTTPException(status_code=500, detail="Empty AI response")
                
            ai_response_text = response.choices[0].message.content
            
            # Parse and structure the analysis
            return self._parse_analysis(ai_response_text, startup_data)
            
        except Exception as e:
            print(f"AI Analysis Error: {str(e)}")
            # Return fallback analysis if AI fails
            return self._get_fallback_analysis(startup_data)
    
    def _create_analysis_prompt(self, data: StartupIdea) -> str:
        return f'''
Please provide a comprehensive startup validation analysis for the following idea:

**Startup Idea:** {data.idea}
**Target Customer:** {data.customer}
**Problem:** {data.problem}
**Solution:** {data.solution}
**Founder Background:** {data.background}

Please provide a detailed analysis in the following JSON format:

{{
    "viability_score": 0.0,
    "market_size": "string",
    "competition_level": "High/Medium/Low",
    "time_to_market": "string",
    "market_analysis": {{
        "tam": "string",
        "sam": "string", 
        "som": "string",
        "growth_rate": "string",
        "key_trends": ["trend1", "trend2", "trend3"]
    }},
    "competitive_landscape": {{
        "direct_competitors": [
            {{"name": "string", "market_share": "string", "weakness": "string"}}
        ],
        "competitive_advantage": "string",
        "market_gap": "string"
    }},
    "risk_assessment": {{
        "high_risks": ["risk1", "risk2"],
        "medium_risks": ["risk1", "risk2"], 
        "low_risks": ["risk1", "risk2"]
    }},
    "founder_market_fit": {{
        "score": 0.0,
        "strengths": ["strength1", "strength2"],
        "gaps": ["gap1", "gap2"],
        "recommendations": ["rec1", "rec2"]
    }},
    "yc_criteria_assessment": {{
        "problem_clarity": 0,
        "solution_fit": 0,
        "market_size": 0,
        "founder_strength": 0,
        "traction_potential": 0,
        "overall_score": 0.0,
        "notes": "string"
    }},
    "recommendations": {{
        "mvp_strategy": "string",
        "funding_needs": "string",
        "key_partnerships": ["partnership1", "partnership2"],
        "success_metrics": ["metric1", "metric2"]
    }},
    "financial_projections": {{
        "revenue_model": "string",
        "avg_booking_value": "string",
        "monthly_bookings_y1": "string",
        "projected_mrr_y1": "string",
        "customer_acquisition_cost": "string",
        "customer_lifetime_value": "string",
        "break_even_timeline": "string",
        "funding_requirements": [
            {{"stage": "string", "amount": "string", "use": "string"}}
        ]
    }},
    "action_plan": {{
        "phase_1": {{
            "timeline": "string",
            "title": "string", 
            "tasks": ["task1", "task2"]
        }},
        "phase_2": {{
            "timeline": "string",
            "title": "string",
            "tasks": ["task1", "task2"] 
        }},
        "phase_3": {{
            "timeline": "string",
            "title": "string",
            "tasks": ["task1", "task2"]
        }}
    }}
}}

Analyze using proven frameworks:
1. **Viability Score (0-10):** Overall assessment of the startup's potential
2. **Market Analysis:** TAM-SAM-SOM analysis, market size estimation, growth trends
3. **Competitive Landscape:** Direct/indirect competitors, market positioning, differentiation opportunities
4. **Risk Assessment:** High/medium/low risk factors with specific examples
5. **YC Criteria Assessment:** Evaluate against Y Combinator's selection criteria
6. **Founder-Market Fit:** How well the founder's background aligns with the market
7. **Strategic Recommendations:** Actionable next steps, MVP strategy, funding requirements
8. **Financial Projections:** Revenue model, key metrics, growth projections
9. **Action Plan:** 3-phase roadmap with specific timelines and milestones

Provide specific, actionable insights with real market data estimates where possible.
'''

    def _parse_analysis(self, analysis_text: str, startup_data: StartupIdea) -> dict:
        """Parse AI analysis from JSON response"""
        
        try:
            # Clean the response text
            cleaned_text = analysis_text.strip()
            
            # Remove any markdown code blocks if present
            cleaned_text = re.sub(r'^```json\n', '', cleaned_text)
            cleaned_text = re.sub(r'\n```$', '', cleaned_text)
            cleaned_text = re.sub(r'^```\n', '', cleaned_text)
            cleaned_text = re.sub(r'\n```$', '', cleaned_text)
            
            # Parse JSON
            parsed_analysis = json.loads(cleaned_text)
            
            # Validate and ensure all required fields are present
            validated_analysis = self._validate_analysis_structure(parsed_analysis)
            
            return validated_analysis
            
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {str(e)}")
            print(f"Raw response: {analysis_text[:500]}...")
            # Return fallback analysis if JSON parsing fails
            return self._get_fallback_analysis(startup_data)
        except Exception as e:
            print(f"Analysis parsing error: {str(e)}")
            return self._get_fallback_analysis(startup_data)
    
    def _validate_analysis_structure(self, analysis: dict) -> dict:
        """Validate and ensure all required fields are present with correct types"""
        
        # Default structure template
        default_structure = {
            "viability_score": 7.5,
            "market_size": "Unknown",
            "competition_level": "Medium",
            "time_to_market": "6-12 months",
            "market_analysis": {
                "tam": "Market data not available",
                "sam": "Market data not available",
                "som": "Market data not available", 
                "growth_rate": "Unknown",
                "key_trends": ["Market trend analysis needed"]
            },
            "competitive_landscape": {
                "direct_competitors": [{"name": "Unknown", "market_share": "Unknown", "weakness": "Requires analysis"}],
                "competitive_advantage": "Needs identification",
                "market_gap": "Requires market research"
            },
            "risk_assessment": {
                "high_risks": ["Market validation needed"],
                "medium_risks": ["Competition analysis needed"],
                "low_risks": ["Technical implementation"]
            },
            "founder_market_fit": {
                "score": 7.0,
                "strengths": ["Relevant background"],
                "gaps": ["Industry-specific experience"],
                "recommendations": ["Gain market expertise"]
            },
            "yc_criteria_assessment": {
                "problem_clarity": 7,
                "solution_fit": 7,
                "market_size": 7,
                "founder_strength": 7,
                "traction_potential": 7,
                "overall_score": 7.0,
                "notes": "Requires deeper validation"
            },
            "recommendations": {
                "mvp_strategy": "Build and test minimum viable product",
                "funding_needs": "Determine based on market research",
                "key_partnerships": ["Industry partnerships needed"],
                "success_metrics": ["User acquisition", "Revenue growth"]
            },
            "financial_projections": {
                "revenue_model": "To be determined",
                "avg_booking_value": "Unknown",
                "monthly_bookings_y1": "To be projected", 
                "projected_mrr_y1": "Unknown",
                "customer_acquisition_cost": "To be calculated",
                "customer_lifetime_value": "To be calculated",
                "break_even_timeline": "12-18 months",
                "funding_requirements": [{"stage": "Seed", "amount": "TBD", "use": "Product development"}]
            },
            "action_plan": {
                "phase_1": {
                    "timeline": "Weeks 1-4",
                    "title": "Market Validation",
                    "tasks": ["Conduct market research", "Validate problem-solution fit"]
                },
                "phase_2": {
                    "timeline": "Weeks 5-12",
                    "title": "Product Development", 
                    "tasks": ["Build MVP", "Test with early users"]
                },
                "phase_3": {
                    "timeline": "Weeks 13-24",
                    "title": "Go-to-Market",
                    "tasks": ["Launch product", "Scale operations"]
                }
            }
        }
        
        def merge_dicts(default, provided):
            """Recursively merge provided data with defaults"""
            result = default.copy()
            for key, value in provided.items():
                if key in result:
                    if isinstance(value, dict) and isinstance(result[key], dict):
                        result[key] = merge_dicts(result[key], value)
                    else:
                        result[key] = value
                else:
                    result[key] = value
            return result
        
        return merge_dicts(default_structure, analysis)
    
    def _get_fallback_analysis(self, startup_data: StartupIdea) -> dict:
        """Return a basic analysis structure when AI analysis fails"""
        
        # Attempt to extract some basic insights from the startup data
        idea_keywords = startup_data.idea.lower().split()
        
        # Determine basic market characteristics based on keywords
        tech_keywords = ['app', 'platform', 'software', 'ai', 'tech', 'digital', 'online']
        service_keywords = ['service', 'marketplace', 'booking', 'delivery', 'care']
        
        is_tech = any(keyword in startup_data.idea.lower() for keyword in tech_keywords)
        is_service = any(keyword in startup_data.idea.lower() for keyword in service_keywords)
        
        # Basic scoring based on content analysis
        base_score = 7.0
        if len(startup_data.problem) > 200:  # Detailed problem description
            base_score += 0.5
        if len(startup_data.solution) > 200:  # Detailed solution 
            base_score += 0.5
        if 'experience' in startup_data.background.lower():  # Relevant experience
            base_score += 0.3
            
        return {
            "viability_score": min(base_score, 10.0),
            "market_size": "Market research required",
            "competition_level": "Medium" if is_tech else "High",
            "time_to_market": "3-6 months" if is_tech else "6-12 months",
            "market_analysis": {
                "tam": "Total addressable market analysis needed",
                "sam": "Serviceable addressable market analysis needed", 
                "som": "Serviceable obtainable market analysis needed",
                "growth_rate": "Market growth analysis required",
                "key_trends": [
                    "Digital transformation trends" if is_tech else "Service industry evolution",
                    "Consumer behavior shifts",
                    "Market consolidation opportunities"
                ]
            },
            "competitive_landscape": {
                "direct_competitors": [
                    {"name": "Competitor analysis needed", "market_share": "Unknown", "weakness": "Requires competitive research"}
                ],
                "competitive_advantage": "Differentiation strategy needs development",
                "market_gap": "Market gap analysis required"
            },
            "risk_assessment": {
                "high_risks": [
                    "Market validation uncertainty",
                    "Competitive response unknown",
                    "Customer acquisition challenges"
                ],
                "medium_risks": [
                    "Technology implementation complexity" if is_tech else "Service delivery scalability",
                    "Regulatory considerations",
                    "Team scaling requirements"
                ],
                "low_risks": [
                    "Basic infrastructure setup",
                    "Initial customer outreach",
                    "MVP development approach"
                ]
            },
            "founder_market_fit": {
                "score": 7.0 if 'experience' in startup_data.background.lower() else 6.0,
                "strengths": [
                    "Identified market problem",
                    "Solution-oriented thinking",
                    "Entrepreneurial mindset"
                ],
                "gaps": [
                    "Industry-specific expertise needed",
                    "Market research depth required",
                    "Network development needed"
                ],
                "recommendations": [
                    "Conduct customer interviews",
                    "Connect with industry experts",
                    "Validate assumptions with data"
                ]
            },
            "yc_criteria_assessment": {
                "problem_clarity": 7,
                "solution_fit": 6,
                "market_size": 6,
                "founder_strength": 7,
                "traction_potential": 6,
                "overall_score": 6.4,
                "notes": "Solid foundation with need for market validation and traction development"
            },
            "recommendations": {
                "mvp_strategy": "Build focused minimum viable product targeting core user need",
                "funding_needs": "Bootstrap initially, seek $50K-200K for validation phase",
                "key_partnerships": [
                    "Industry domain experts",
                    "Early customer partnerships", 
                    "Technology/service delivery partners"
                ],
                "success_metrics": [
                    "Customer acquisition cost < $50",
                    "User engagement > 60%",
                    "Monthly growth rate > 20%",
                    "Customer satisfaction > 4.0/5.0"
                ]
            },
            "financial_projections": {
                "revenue_model": "Revenue model needs definition based on value proposition",
                "avg_booking_value": "Average transaction value TBD",
                "monthly_bookings_y1": "Growth trajectory to be established",
                "projected_mrr_y1": "$5K-25K depending on market penetration",
                "customer_acquisition_cost": "Target: $25-75 per customer",
                "customer_lifetime_value": "Target: $200-500 per customer",
                "break_even_timeline": "12-18 months with proper execution",
                "funding_requirements": [
                    {"stage": "Bootstrap", "amount": "$10K-50K", "use": "MVP development and initial validation"},
                    {"stage": "Seed", "amount": "$100K-500K", "use": "Market expansion and team building"}
                ]
            },
            "action_plan": {
                "phase_1": {
                    "timeline": "Weeks 1-6",
                    "title": "Problem-Solution Fit Validation",
                    "tasks": [
                        "Conduct 20+ customer interviews",
                        "Refine problem definition and solution approach",
                        "Create detailed customer personas",
                        "Validate core assumptions",
                        "Define MVP feature set"
                    ]
                },
                "phase_2": {
                    "timeline": "Weeks 7-16", 
                    "title": "MVP Development & Testing",
                    "tasks": [
                        "Build minimum viable product",
                        "Recruit 10-50 beta users",
                        "Gather usage data and feedback",
                        "Iterate product based on learning",
                        "Establish key metrics tracking"
                    ]
                },
                "phase_3": {
                    "timeline": "Weeks 17-26",
                    "title": "Market Entry & Growth",
                    "tasks": [
                        "Launch product to broader market",
                        "Implement customer acquisition strategy", 
                        "Optimize conversion and retention",
                        "Seek strategic partnerships",
                        "Prepare for scaling and funding"
                    ]
                }
            }
        }

# Initialize AI service
ai_service = AIAnalysisService()

# API Routes
@app.get("/")
async def root():
    return {"message": "VentureAI API - Startup Validation Platform", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/validate", response_model=dict)
async def validate_startup(
    background_tasks: BackgroundTasks,
    idea: str = Form(...),
    customer: str = Form(...),
    problem: str = Form(...),
    solution: str = Form(...),
    background: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None)
):
    """Generate startup validation report"""
    
    background_text = ""
    if resume_file and background:
        raise HTTPException(status_code=400, detail="Provide either background text or a resume file, not both.")

    if resume_file:
        if resume_file.content_type != 'application/pdf':
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")
        try:
            pdf_content = await resume_file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            for page in pdf_reader.pages:
                background_text += page.extract_text()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process resume file: {str(e)}")
    elif background:
        background_text = background
    else:
        raise HTTPException(status_code=400, detail="Either background text or a resume file must be provided.")

    startup_data = StartupIdea(
        idea=idea,
        customer=customer,
        problem=problem,
        solution=solution,
        background=background_text
    )
    
    try:
        # Generate unique report ID
        report_id = str(uuid.uuid4())
        
        # Create initial report entry
        reports_db[report_id] = {
            "status": "processing",
            "created_at": datetime.now(),
            "startup_data": startup_data.dict()
        }
        
        # Start analysis in background
        background_tasks.add_task(generate_analysis, report_id, startup_data)
        
        return {
            "report_id": report_id,
            "status": "processing", 
            "message": "Analysis started. Use the report_id to check status.",
            "estimated_time": "30-60 seconds"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/report/{report_id}")
async def get_report(report_id: str):
    """Get validation report by ID"""
    
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report = reports_db[report_id]
    
    if report["status"] == "processing":
        return {"status": "processing", "progress": "AI analysis in progress..."}
    elif report["status"] == "failed":
        return {"status": "failed", "error": report.get("error", "Unknown error occurred")}
    
    return report

@app.get("/reports")
async def list_reports():
    """List all reports (for admin purposes)"""
    return {
        "reports": [
            {
                "id": report_id,
                "status": report["status"],
                "created_at": report["created_at"],
                "completed_at": report.get("completed_at")
            }
            for report_id, report in reports_db.items()
        ],
        "total": len(reports_db)
    }

@app.delete("/report/{report_id}")
async def delete_report(report_id: str):
    """Delete a specific report"""
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    
    del reports_db[report_id]
    return {"message": "Report deleted successfully"}

# Background task for AI analysis
async def generate_analysis(report_id: str, startup_data: StartupIdea):
    """Background task to generate AI analysis"""
    
    try:
        # Get AI analysis
        analysis = await ai_service.analyze_startup(startup_data)
        
        # Update report with analysis
        reports_db[report_id].update({
            "status": "completed",
            "analysis": analysis,
            "completed_at": datetime.now()
        })
        
        print(f"Report {report_id} completed successfully")
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        print(f"Report {report_id} failed: {error_msg}")
        
        reports_db[report_id].update({
            "status": "failed",
            "error": error_msg,
            "completed_at": datetime.now()
        })