"""
Background task for weather streaming
"""
import asyncio
from app.services.weather_services import WeatherStreamingService


async def start_weather_streaming():
    """Start continuous weather streaming"""
    
    async with WeatherStreamingService() as service:
        await service.stream_weather_for_all_locations()


if __name__ == "__main__":
    print("🌤️  Starting Weather Streaming Service...")
    asyncio.run(start_weather_streaming())