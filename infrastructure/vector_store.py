import numpy as np
import faiss
from typing import List

class VehicleBehaviorMemory:
    def __init__(self, dimension: int = 4):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(self.dimension) 
        self.vehicle_map = [] 

    def _normalize_telemetry(self, speed: float, temp: float, battery: float, vib: float) -> np.ndarray:
        return np.array([[speed/150.0, temp/120.0, battery/100.0, vib/1.0]], dtype=np.float32)

    def add_behavior_baseline(self, vehicle_id: str, speed: float, temp: float, battery: float, vib: float):
        vector = self._normalize_telemetry(speed, temp, battery, vib)
        self.index.add(vector)
        self.vehicle_map.append(vehicle_id)

    def is_anomalous(self, vehicle_id: str, speed: float, temp: float, battery: float, vib: float, threshold: float = 0.5) -> bool:
        if self.index.ntotal == 0:
            return False
            
        vector = self._normalize_telemetry(speed, temp, battery, vib)
        distances, indices = self.index.search(vector, k=1)
        
        return distances[0][0] > threshold

vector_memory = VehicleBehaviorMemory()
