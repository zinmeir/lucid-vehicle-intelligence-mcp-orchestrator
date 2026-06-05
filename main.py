from fastapi import FastAPI, BackgroundTasks, HTTPException
from mcp_server import VehicleMCP
from models import TelemetryInput, DiagnosticReport, MLOutput
import asyncio

app = FastAPI(title="Vehicle Intelligence MCP Server")
mcp = VehicleMCP()

async def mock_anomaly_model(data: TelemetryInput) -> MLOutput:
    await asyncio.sleep(0.1)
    return MLOutput(model="anomaly_detection_model", score=0.87, label="HIGH_ANOMALY", explanation_features=["temperature_spike", "battery_irregularity"])

async def mock_battery_model(data: TelemetryInput) -> MLOutput:
    return MLOutput(model="battery_degradation_model", score=0.65, label="THERMAL_DEGRADATION", explanation_features=["rapid_discharge"])

async def mock_behavior_model(data: TelemetryInput) -> MLOutput:
    return MLOutput(model="driving_behavior_model", score=0.2, label="NORMAL", explanation_features=["steady_acceleration"])

# Register Tools
mcp.register_tool("anomaly_detection_model", mock_anomaly_model)
mcp.register_tool("battery_degradation_model", mock_battery_model)
mcp.register_tool("driving_behavior_model", mock_behavior_model)

@app.post("/telemetry/ingest")
async def ingest_telemetry(telemetry: TelemetryInput, background_tasks: BackgroundTasks):
    background_tasks.add_task(mcp.analyze, telemetry)
    return {"status": "queued", "vehicle_id": telemetry.vehicle_id}

@app.post("/analyze/{vehicle_id}", response_model=DiagnosticReport)
async def analyze_vehicle(vehicle_id: str, telemetry: TelemetryInput):
    if telemetry.vehicle_id != vehicle_id:
        raise HTTPException(status_code=400, detail="Vehicle ID mismatch")
    return await mcp.analyze(telemetry)

@app.get("/vehicle/{vehicle_id}/report", response_model=DiagnosticReport)
async def get_latest_report(vehicle_id: str):
    alerts = mcp.redis_state.get(f"{vehicle_id}_alerts", [])
    if not alerts:
        raise HTTPException(status_code=404, detail="No reports found for vehicle")
    return alerts[-1]

@app.post("/event/alert")
async def trigger_event_alert(report: DiagnosticReport):
    print(f"CRITICAL ALERT TRIGGERED FOR {report.vehicle_id}: {report.explanation}")
    return {"status": "alert_dispatched"}
