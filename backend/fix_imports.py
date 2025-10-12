import os

# Check if .env exists
if not os.path.exists('.env'):
    print("❌ .env file not found!")
    print("Create .env with:")
    print("SUPABASE_URL=your_url")
    print("SUPABASE_ANON_KEY=your_key")
else:
    # Load and check
    from dotenv import load_dotenv
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Supabase credentials missing in .env")
    else:
        print("✅ .env configured")
        print(f"URL: {url[:30]}...")
        print(f"Key: {key[:30]}...")

# Check weather service file
if os.path.exists('app/services/weather_services.py'):
    print("✅ weather_services.py exists")
elif os.path.exists('app/services/weather_services.py'):
    print("⚠️  Found weather_services.py - rename to weather_service.py")
    print("Run: mv app/services/weather_services.py app/services/weather_service.py")
else:
    print("❌ Weather service file not found!")