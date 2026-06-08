"""Quick test to verify the analytics_service prev-period fix."""
import asyncio
import sys
import os

# Ensure we're in the backend directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

async def main():
    from app.core.database import AsyncSessionLocal
    from app.services.analytics_service import AnalyticsService

    async with AsyncSessionLocal() as db:
        service = AnalyticsService(db, "dev")
        try:
            result = await service.get_overview("30d", None)
            import json
            print(json.dumps(result, default=str, indent=2))
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("FAILED:", e, file=sys.stderr)

asyncio.run(main())
