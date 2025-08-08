from fastapi import APIRouter, Query
from app.services.anthropic_service import call_claude
import requests

router = APIRouter()

@router.get("/anthropic/test")
def anthropic_test(prompt: str = Query(..., description="Prompt to send to Anthropic Claude")):
    try:
        # Check if API key is set
        import os
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "message": "ANTHROPIC_API_KEY environment variable not set",
                "prompt": prompt,
                "endpoint_working": True,
                "debug_info": {
                    "api_key_length": 0,
                    "api_key_prefix": "None"
                }
            }
        
        # Test the API call with more detailed error handling
        try:
            result = call_claude(prompt)
            return {"result": result, "status": "success"}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {
                    "error": "API key may be invalid or expired",
                    "status": "error",
                    "details": {
                        "status_code": e.response.status_code,
                        "response_text": e.response.text,
                        "api_key_length": len(api_key),
                        "api_key_prefix": api_key[:10] + "..." if len(api_key) > 10 else api_key
                    }
                }
            else:
                return {"error": str(e), "status": "error"}
        except Exception as e:
            return {"error": str(e), "status": "error"}
    except Exception as e:
        return {"error": str(e), "status": "error"} 