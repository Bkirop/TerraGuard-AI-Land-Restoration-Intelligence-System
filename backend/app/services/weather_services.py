"""
Weather streaming service with Supabase real-time integration
"""
import os
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List
from app.database import supabase

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"


class WeatherStreamingService:
    """Stream weather data directly to Supabase"""
    
    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_current_weather(self, lat: float, lon: float) -> Dict:
        """Fetch current weather from API"""
        if not self.api_key:
            return self._generate_sample_weather(lat, lon)
        
        url = f"{BASE_URL}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_current_weather(data)
                else:
                    return self._generate_sample_weather(lat, lon)
        except Exception as e:
            print(f"❌ Weather API error: {e}")
            return self._generate_sample_weather(lat, lon)
    
    def _parse_current_weather(self, data: Dict) -> Dict:
        """Parse OpenWeather response"""
        return {
            'temp_avg': data['main']['temp'],
            'temp_min': data['main']['temp_min'],
            'temp_max': data['main']['temp_max'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'precipitation': data.get('rain', {}).get('1h', 0),
            'description': data['weather'][0]['description'],
            'timestamp': datetime.now()
        }
    
    def _generate_sample_weather(self, lat: float, lon: float) -> Dict:
        """Fallback sample weather"""
        base_temp = 30 - (abs(lat) * 0.5)
        return {
            'temp_avg': round(base_temp, 1),
            'temp_min': round(base_temp - 3, 1),
            'temp_max': round(base_temp + 5, 1),
            'humidity': 65,
            'wind_speed': 3.5,
            'precipitation': 0,
            'description': 'Partly cloudy',
            'timestamp': datetime.now()
        }
    
    async def stream_weather_to_supabase(self, location_id: str, weather: Dict):
        """
        🔥 KEY METHOD: Stream weather data to Supabase
        This triggers real-time updates to all connected clients
        """
        try:
            climate_data = {
                'location_id': location_id,
                'date': weather['timestamp'].date().isoformat(),
                'temp_avg': weather['temp_avg'],
                'temp_max': weather['temp_max'],
                'temp_min': weather['temp_min'],
                'humidity': weather['humidity'],
                'wind_speed': weather['wind_speed'],
                'precipitation': weather['precipitation'],
                'source': 'openweathermap',
                'is_forecast': False
            }
            
            # 🔥 INSERT triggers Supabase Realtime broadcast
            response = supabase.table("climate_data").upsert(climate_data).execute()
            
            print(f"✅ Weather streamed to Supabase: {location_id} - {weather['temp_avg']}°C")
            
            # Check for extreme weather alerts
            await self.check_weather_alerts(location_id, weather)
            
            return response.data
            
        except Exception as e:
            print(f"❌ Error streaming to Supabase: {e}")
    
    async def check_weather_alerts(self, location_id: str, weather: Dict):
        """Create alerts for extreme weather"""
        
        alerts = []
        
        # Extreme heat
        if weather['temp_max'] > 35:
            alerts.append({
                'location_id': location_id,
                'alert_type': 'heat_stress',
                'severity': 'WARNING',
                'title': 'Extreme Heat Alert',
                'message': f"Temperature expected to reach {weather['temp_max']}°C. Protect crops and livestock.",
                'event_date': datetime.now().date().isoformat(),
                'recommended_actions': [
                    'Increase irrigation',
                    'Provide shade for animals',
                    'Avoid midday fieldwork'
                ]
            })
        
        # Heavy rain
        if weather['precipitation'] > 50:
            alerts.append({
                'location_id': location_id,
                'alert_type': 'heavy_rain',
                'severity': 'WARNING',
                'title': 'Heavy Rainfall Warning',
                'message': f"Heavy rainfall expected ({weather['precipitation']}mm). Risk of erosion and flooding.",
                'event_date': datetime.now().date().isoformat(),
                'recommended_actions': [
                    'Clear drainage channels',
                    'Protect topsoil',
                    'Delay planting'
                ]
            })
        
        # Insert alerts (triggers realtime broadcast)
        if alerts:
            for alert in alerts:
                supabase.table("alerts").insert(alert).execute()
                print(f"🚨 Alert created: {alert['title']}")
    
    async def stream_all_locations(self):
        """Continuously stream weather for all locations"""
        
        print("🌤️  Starting continuous weather streaming to Supabase...")
        
        while True:
            try:
                # Get all locations
                locations = supabase.table("locations").select("*").execute()
                
                print(f"\n📍 Streaming weather for {len(locations.data)} locations...")
                
                for location in locations.data:
                    # Fetch weather
                    weather = await self.get_current_weather(
                        location['latitude'],
                        location['longitude']
                    )
                    
                    # Stream to Supabase (triggers realtime)
                    await self.stream_weather_to_supabase(location['id'], weather)
                    
                    # Small delay to avoid rate limits
                    await asyncio.sleep(1)
                
                print(f"\n💤 Next update in 15 minutes...")
                await asyncio.sleep(900)  # 15 minutes
                
            except Exception as e:
                print(f"❌ Streaming error: {e}")
                await asyncio.sleep(60)


    