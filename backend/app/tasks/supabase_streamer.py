"""
Background task to stream data to Supabase
"""
import asyncio
from app.services.weather_services import WeatherStreamingService


async def start_weather_streaming():
    """Start continuous weather streaming to Supabase"""
    
    async with WeatherStreamingService() as service:
        await service.stream_all_locations()


if __name__ == "__main__":
    print("🚀 Starting Supabase Weather Streaming...")
    asyncio.run(start_weather_streaming())

