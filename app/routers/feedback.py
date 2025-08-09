from fastapi import APIRouter
import json
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/feedback", tags=["Feedback"])

class FeedbackInput(BaseModel):
    question: str
    answer: str
    score: float
    source: str
    is_helpful: bool  # True = 👍, False = 👎
    timestamp: str = datetime.utcnow().isoformat()

@router.post("/")
def collect_feedback(feedback: FeedbackInput):
    try:
        with open("feedback_logs.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback.dict()) + "\n")
        return {"message": "Geri bildirim alındı ✅"}
    except Exception as e:
        return {"error": str(e)}
