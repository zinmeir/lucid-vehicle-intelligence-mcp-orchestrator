import asyncio
from typing import Callable, Dict, List, Any
from models import TelemetryInput, MLOutput, DiagnosticReport

class VehicleMCP:
    def __init__(self):
        self.tool_registry: Dict[str, Callable] = {}
        self.redis_state = {} 
        self.faiss_memory = {} 

    def register_tool(self, name: str, func: Callable):
        self.tool_registry[name] = func

    async def build_context(self, vehicle_id: str, current_telemetry: TelemetryInput) -> Dict[str, Any]:
        historical_baseline = self.faiss_memory.get(vehicle_id, {"avg_temp": 85, "baseline_vibration": 0.2})
        recent_alerts = self.redis_state.get(f"{vehicle_id}_alerts", [])
        
        current_dict = current_telemetry.model_dump() if hasattr(current_telemetry, "model_dump") else current_telemetry.dict()
        
        return {
            "current": current_dict,
            "baseline": historical_baseline,
            "recent_alerts": recent_alerts
        }

    def decision_engine(self, context: Dict[str, Any]) -> List[str]:
        tools_to_run = ["driving_behavior_model"]
        current = context["current"]
        baseline = context["baseline"]
        
        if current["temperature"] > baseline["avg_temp"] * 1.1 or current["vibration"] > 0.4:
            tools_to_run.extend(["anomaly_detection_model", "maintenance_prediction_model"])
            
        if current["battery_level"] < 20 or current["temperature"] > 95:
            tools_to_run.append("battery_degradation_model")
            
        return list(set(tools_to_run).intersection(set(self.tool_registry.keys())))

    async def synthesize_response(self, vehicle_id: str, context: Dict, ml_outputs: List[MLOutput]) -> DiagnosticReport:
        weights = {"anomaly_detection_model": 0.5, "battery_degradation_model": 0.3, "maintenance_prediction_model": 0.2, "driving_behavior_model": 0.1}
        
        total_weight = sum(weights.get(m.model, 0) for m in ml_outputs) or 1
        consensus_score = sum(m.score * weights.get(m.model, 0.1) for m in ml_outputs) / total_weight
        
        category = "Critical" if consensus_score > 0.75 else "Warning" if consensus_score > 0.4 else "Normal"
        explanation = (f"Vehicle {vehicle_id} shows early signs of deviation. "
                       f"Models flagged {', '.join([m.label for m in ml_outputs])}. "
                       f"Temperature fluctuations and voltage inconsistency suggest cooling system inefficiency.")
        
        return DiagnosticReport(
            vehicle_id=vehicle_id,
            timestamp=context["current"]["timestamp"],
            risk_score=round(consensus_score, 2),
            category=category,
            root_cause_hypothesis="Cooling system inefficiency leading to battery thermal stress.",
            recommended_action="Schedule inspection within 7 days. Throttle max speed limit.",
            explanation=explanation,
            contributing_models=ml_outputs
        )

    async def analyze(self, telemetry: TelemetryInput) -> DiagnosticReport:
        context = await self.build_context(telemetry.vehicle_id, telemetry)
        tools_to_run = self.decision_engine(context)
        
        tasks = [self.tool_registry[tool](telemetry) for tool in tools_to_run]
        ml_outputs = await asyncio.gather(*tasks)
        
        report = await self.synthesize_response(telemetry.vehicle_id, context, ml_outputs)
        
        if report.category in ["Warning", "Critical"]:
            report_dict = report.model_dump() if hasattr(report, "model_dump") else report.dict()
            self.redis_state.setdefault(f"{telemetry.vehicle_id}_alerts", []).append(report_dict)
            
        return report
