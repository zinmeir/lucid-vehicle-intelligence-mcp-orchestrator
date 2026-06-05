from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime

class TelemetryInput(BaseModel):
    vehicle_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    speed: float
    temperature: float
    battery_level: float
    vibration: float
    
class MLOutput(BaseModel):
    model: str
    score: float
    label: str
    explanation_features: List[str]

class DiagnosticReport(BaseModel):
    vehicle_id: str
    timestamp: datetime
    risk_score: float = Field(ge=0.0, le=1.0)
    category: str
    root_cause_hypothesis: str
    recommended_action: str
    explanation: str
    contributing_models: List[MLOutput]
