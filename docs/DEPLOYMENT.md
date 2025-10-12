# TerraGuard AI Deployment Guide

## Backend
1. Set up Postgres/Supabase database and run `scripts/setup_supabase.sql` for schema.
2. Create `.env` file with Supabase and Claude API keys.
3. Install Python dependencies with `pip install -r backend/requirements.txt`.
4. Run the FastAPI server: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`.

## Frontend
1. Navigate to `frontend/`.
2. Run `npm install` to install dependencies.
3. Start frontend: `npm run start`.
4. Frontend will run at http://localhost:3000 by default.

## Notes
- Ensure connection URLs and API keys are correctly configured.
- Seed database if needed with `python scripts/seed_data.py`.
