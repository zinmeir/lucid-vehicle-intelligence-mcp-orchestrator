import os
import redis.asyncio as redis
import asyncpg

class DatabaseManager:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.db_url = os.getenv("DATABASE_URL", "postgres://postgres:password@localhost:5432/vehicle_db")
        self.redis_client = None
        self.db_pool = None

    async def connect(self):
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        try:
            self.db_pool = await asyncpg.create_pool(self.db_url)
            print(" Connected to TimescaleDB & Redis")
        except Exception as e:
            print(f" Database connection failed (Mocking enabled): {e}")

    async def cache_vehicle_state(self, vehicle_id: str, state_data: dict):
        if self.redis_client:
            await self.redis_client.hset(f"vehicle:{vehicle_id}:state", mapping=state_data)

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
        if self.db_pool:
            await self.db_pool.close()

db_manager = DatabaseManager()
