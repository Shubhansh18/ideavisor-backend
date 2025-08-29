from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from datetime import datetime
import uuid
from ..models.models import StartupIdea, ValidationReport
from ..services.service import AIAnalysisService
from ..reports import save_report, get_report
from ..exceptions import AIAnalysisError, ReportError

# Create router
router = APIRouter()

@router.get("/")
async def root():
    return {"message": "IdeaVisor API - Startup Validation Platform", "status": "active"}

@router.post("/analyze")
async def analyze_startup(
    background_tasks: BackgroundTasks,
    startup_data: StartupIdea = Depends(StartupIdea.as_form)
):
    """Analyze startup idea and generate validation report"""
    
    report_id = str(uuid.uuid4())
    
    try:
        # Initialize report status
        initial_status = {"status": "processing"}
        save_report(report_id, initial_status)
        
        # Create AI service instance and run analysis
        ai_service = AIAnalysisService()
        analysis_result = await ai_service.analyze_startup(startup_data)
        
        if analysis_result.get("type") == "clarification_request":
            clarification_data = {
                "status": "clarification_needed", 
                "message": analysis_result.get("message", "The AI requires more information to proceed.")
            }
            save_report(report_id, clarification_data)
            return {"report_id": report_id, "status": "clarification_needed", "message": clarification_data["message"]}

        if analysis_result.get("type") == "analysis":
            report = ValidationReport(
                id=report_id,
                startup_data=startup_data,
                viability_score=analysis_result["data"]["viability_score"],
                market_size=analysis_result["data"]["market_size"],
                competition_level=analysis_result["data"]["competition_level"],
                time_to_market=analysis_result["data"]["time_to_market"],
                market_analysis=analysis_result["data"]["market_analysis"],
                risk_assessment=analysis_result["data"]["risk_assessment"],
                recommendations=analysis_result["data"]["recommendations"],
                financial_projections=analysis_result["data"]["financial_projections"],
                action_plan=analysis_result["data"]["action_plan"],
                competitive_landscape=analysis_result["data"]["competitive_landscape"],
                founder_market_fit=analysis_result["data"]["founder_market_fit"],
                yc_criteria_assessment=analysis_result["data"]["yc_criteria_assessment"],
                created_at=datetime.now()
            )
            
            report_data = {"status": "completed", "analysis": report.dict()}
            save_report(report_id, report_data)
            
            return {"report_id": report_id, "status": "completed"}
        
        # If the AI service returns a valid but unexpected response type
        raise AIAnalysisError(f"Unexpected response type from AI service: {analysis_result.get('type')}")

    except Exception as e:
        # Save a failed status before re-raising the exception for the handler
        error_data = {"status": "failed", "error": str(e)}
        save_report(report_id, error_data)
        # Re-raise the exception to be caught by the centralized handler
        raise

@router.get("/report/{report_id}")
async def get_report_status(report_id: str):
    """Get validation report by ID"""
    try:
        report_data = get_report(report_id)
    except Exception as e:
        raise ReportError(f"Failed to retrieve report {report_id}: {str(e)}")
    
    if report_data is None:
        raise HTTPException(status_code=404, detail=f"Report with ID '{report_id}' not found.")
    
    return report_data
