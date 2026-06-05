import asyncio
import httpx
import random
from datetime import datetime

API_URL = "http://127.0.0.1:8000/telemetry/ingest"
VEHICLES = ["V-LUCID-GRAVITY", "V-LUCID-AIR-TOURING", "V-LUCID-AIR-SAPPHIRE"]

async def simulate_vehicle(vehicle_id: str, client: httpx.AsyncClient):
    base_temp = 85.0
    for _ in range(10):
        if vehicle_id == "V-LUCID-GRAVITY-001":
            base_temp += random.uniform(2.0, 5.0) 
            
        payload = {
            "vehicle_id": vehicle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "speed": random.uniform(40.0, 75.0),
            "temperature": base_temp + random.uniform(-2, 2),
            "battery_level": random.uniform(40.0, 80.0),
            "vibration": random.uniform(0.1, 0.5) if vehicle_id != "V-TESLA-001" else random.uniform(0.6, 0.9)
        }
        
        try:
            response = await client.post(API_URL, json=payload)
            print(f"[{vehicle_id}] Sent telemetry -> Status: {response.status_code}")
        except Exception as e:
            print(f"[{vehicle_id}] Failed to send data: {e}")
            
        await asyncio.sleep(random.uniform(0.5, 2.0))

async def main():
    print("Starting Fleet Telemetry Simulation...")
    async with httpx.AsyncClient() as client:
        tasks = [simulate_vehicle(vid, client) for vid in VEHICLES]
        await asyncio.gather(*tasks)
    print("Simulation Complete.")

if __name__ == "__main__":
    asyncio.run(main())
