from openai import OpenAI, APIError as OpenAIError
from fastapi import HTTPException
import os
import json
from dotenv import load_dotenv
from ..models.models import StartupIdea
from ..exceptions import AIAnalysisError

# Load environment variables
load_dotenv()

# Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set")

client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)

class AIAnalysisService:
    def __init__(self):
        self.client = client
    
    async def analyze_startup(self, startup_data: StartupIdea) -> dict:
        """Analyze startup idea using AI models"""
        
        # The system prompt sets the persona, while the user prompt contains the detailed instructions and data.
        system_prompt = """You are a senior indian startup analyst and venture capitalist with 20+ years of experience. Your analysis is brutally honest, data-driven, and avoids fluff. You are a world-class expert in evaluating new business ideas.
        You will be given a startup idea submission and you must return your analysis ONLY in the requested JSON format."""

        user_prompt = self._create_analysis_prompt(startup_data)
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-r1-0528-qwen3-8b:free",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": user_prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise AIAnalysisError("The AI service returned an empty or invalid response.")
                
            ai_response_text = response.choices[0].message.content
            return self._parse_analysis(ai_response_text, startup_data)

        except OpenAIError as e:
            error_message = e.body.get("message", "An unknown error occurred with the AI provider.")
            raise AIAnalysisError(f"The AI service returned an error: {error_message}") from e
        
        except Exception as e:
            raise AIAnalysisError(f"An unexpected error occurred during AI analysis: {str(e)}") from e
    
    def _create_analysis_prompt(self, data: StartupIdea) -> str:
        return f'''
Here is the startup idea submission I need you to analyze:

<submission>
**Startup Idea:** {data.idea}
**Target Customer:** {data.customer}
**Problem:** {data.problem}
**Solution:** {data.solution}
**Founder Background:** {data.background}
</submission>


## INSTRUCTIONS

Your task is to evaluate the submission based on the following two-step process:

**Step 1: Evaluate Input**
First, assess the provided submission. 
- If the input is valid and provides significant idea that makes sense and is not just random words put together, proceed to Step 2.
- If the input is too short, vague, contains placeholder text (e.g., "test", "asdf"), or is otherwise nonsensical, **DO NOT** perform the analysis. Instead, you MUST respond with the following JSON object:

```json
{{
    "type": "clarification_request",
    "message": "<Your user-friendly message asking for more specific and meaningful input. Explain what is missing or unclear and guide the user on how to improve their submission.>"
}}
```
- Do not ask user for competitor analysis, market size, growth rate or such matrices from user as you are responsible to provide that in your validation research.

**Step 2: Perform In-Depth Validation Analysis**
If the input quality is sufficient, you MUST provide a detailed, actionable, and brutally honest startup validation analysis focused for indian startup ecosystem unless specified otherwise in target audience. Your entire response must be a single JSON object, using the exact structure and keys shown in the template below. Fill in the values based on your expert analysis.

**JSON ANALYSIS TEMPLATE (FILL THIS OUT):**
```json
{{
    "type": "analysis",
    "data": {{
        "viability_score": 0.0, // A score from 0.0 to 10.0 representing overall potential.
        "market_size": "", // Estimated market size (e.g., "$10B+").
        "competition_level": "Low/Medium/High", // Overall competition level.
        "time_to_market": "", // Estimated time to launch an MVP (e.g., "3-6 months").
        "market_analysis": {{
            "tam": "", // Total Addressable Market analysis and estimated value.
            "sam": "", // Serviceable Addressable Market analysis and estimated value.
            "som": "", // Serviceable Obtainable Market analysis and estimated value.
            "growth_rate": "", // Estimated market growth rate (e.g., "15% CAGR").
            "key_trends": [] // List of 3-5 key market trends.
        }},
        "competitive_landscape": {{
            "direct_competitors": [ // List of 2-3 main direct competitors.
                {{"name": "", "market_share": "", "weakness": ""}}
            ],
            "competitive_advantage": "", // What is this idea's unique advantage?
            "market_gap": "" // What specific market gap does this idea fill?
        }},
        "risk_assessment": {{
            "high_risks": [], // List of 2-3 high-impact risks.
            "medium_risks": [], // List of 2-3 medium-impact risks.
            "low_risks": [] // List of 2-3 low-impact risks.
        }},
        "founder_market_fit": {{
            "score": 0.0, // A score from 0.0 to 10.0.
            "strengths": [], // List of the founder's key strengths for this venture.
            "gaps": [], // List of critical gaps in the founder's experience or skills.
            "recommendations": [] // Actionable recommendations to improve founder-market fit.
        }},
        "yc_criteria_assessment": {{
            "problem_clarity": 0, // Score 0-10 for how well the problem is defined.
            "solution_fit": 0, // Score 0-10 for how well the solution fits the problem.
            "market_size": 0, // Score 0-10 for the market potential.
            "founder_strength": 0, // Score 0-10 for the founder's suitability.
            "traction_potential": 0, // Score 0-10 for the potential to gain early traction.
            "overall_score": 0.0, // The average of the scores above.
            "notes": "" // Your summary notes on the YC assessment.
        }},
        "recommendations": {{
            "mvp_strategy": "", // A concise, actionable MVP strategy.
            "funding_needs": "", // Initial funding requirements (e.g., "$25k for MVP", "Bootstrapped").
            "key_partnerships": [], // List of potential key partners.
            "success_metrics": [] // List of 2-3 key metrics to track for success.
        }},
        "financial_projections": {{
            "revenue_model": "", // e.g., "SaaS Subscription", "Commission-based".
            "avg_booking_value": "", // Estimated average value of a transaction.
            "monthly_bookings_y1": "", // Projected bookings in month 12.
            "projected_mrr_y1": "", // Projected MRR at the end of year 1.
            "customer_acquisition_cost": "", // Estimated CAC.
            "customer_lifetime_value": "", // Estimated LTV.
            "break_even_timeline": "", // Estimated time to break even.
            "funding_requirements": [
                {{"stage": "Pre-Seed/Seed", "amount": "", "use": ""}}
            ]
        }},
        "action_plan": {{
            "phase_1": {{
                "timeline": "0-3 months",
                "title": "Validation & Planning",
                "tasks": [] // List of tasks for this phase.
            }},
            "phase_2": {{
                "timeline": "3-6 months",
                "title": "Development & Alpha Testing",
                "tasks": [] // List of tasks for this phase.
            }},
            "phase_3": {{
                "timeline": "6-12 months",
                "title": "Launch & Growth",
                "tasks": [] // List of tasks for this phase.
            }}
        }}
    }}
}}
```

Remember: Your final output must be **ONLY** the single, valid JSON object specified in the templates above. Do not include any other text, explanations, or formatting.
'''

    def _validate_analysis_structure(self, analysis: dict) -> dict:
        """Validate and ensure all required fields are present with correct types"""
        
        if analysis.get("type") == "analysis":
            # Default structure template
            default_structure = {
                "viability_score": 0,
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
                    "funding_requirements": [
                        {"stage": "Seed", "amount": "$500k-1M", "use": "MVP Development & Market Entry"}
                    ]
                },
                "action_plan": {
                    "phase_1": {
                        "timeline": "0-3 months",
                        "title": "Validation & Planning",
                        "tasks": ["Market Research", "MVP Planning"]
                    },
                    "phase_2": {
                        "timeline": "3-6 months",
                        "title": "Development & Testing",
                        "tasks": ["MVP Development", "Beta Testing"]
                    },
                    "phase_3": {
                        "timeline": "6-12 months",
                        "title": "Launch & Growth",
                        "tasks": ["Market Launch", "Customer Acquisition"]
                    }
                }
            }
            
            # Merge provided analysis with default structure
            analysis_data = analysis.get("data", {})
            for key in default_structure:
                if key not in analysis_data:
                    analysis_data[key] = default_structure[key]
            analysis["data"] = analysis_data
                    
        return analysis
    
    def _parse_analysis(self, ai_response: str, startup_data: StartupIdea) -> dict:
        """Parse and validate AI response"""
        try:
            analysis = json.loads(ai_response)
            
            # Handle clarification requests, which are valid responses
            if analysis.get("type") == "clarification_request":
                return analysis

            # For analysis types, validate the structure
            if analysis.get("type") == "analysis":
                if "data" not in analysis:
                    raise AIAnalysisError("AI response is missing the 'data' field for analysis type.")
                return self._validate_analysis_structure(analysis)

            # If the type is neither clarification nor analysis, it's an unknown format
            raise AIAnalysisError(f"AI response returned an unknown type: '{analysis.get('type', 'N/A')}'")

        except json.JSONDecodeError as e:
            raise AIAnalysisError(f"Failed to decode the AI's response as JSON. Raw response: {ai_response}") from e
        except Exception as e:
            # Catch any other unexpected errors during parsing
            raise AIAnalysisError(f"An unexpected error occurred while parsing the AI response: {str(e)}") from e