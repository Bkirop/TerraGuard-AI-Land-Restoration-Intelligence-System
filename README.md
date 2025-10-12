# 🌍 TerraGuard AI - Land Degradation Monitoring & Management System
 **A real-time AI-powered platform for monitoring land health, assessing degradation risks, and generating actionable recommendations for sustainable land management in Africa.**

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Setup](#environment-setup)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🌟 Overview

**TerraGuard AI** is a comprehensive land degradation monitoring system designed specifically for African agricultural contexts. It combines satellite imagery analysis, climate data, and AI-powered recommendations to help farmers, land managers, and policymakers make informed decisions about land conservation and restoration.

### Problem Statement

Land degradation affects over **65% of arable land in Africa**, threatening food security and livelihoods. Traditional monitoring methods are expensive, time-consuming, and often inaccessible to smallholder farmers.

### Our Solution

TerraGuard AI provides:
- **Real-time monitoring** of land health using vegetation indices (NDVI)
- **Risk assessment** for drought, erosion, and soil degradation
- **AI-powered recommendations** tailored to local conditions
- **Climate forecasting** integration for proactive planning
- **Accessible interface** designed for users with varying technical expertise

---

## ✨ Key Features

### 🛰️ Real-Time Monitoring
- **NDVI (Normalized Difference Vegetation Index)** tracking
- **Vegetation cover** percentage analysis
- **Interactive dashboards** with live data updates via Supabase Realtime

### ⚠️ Risk Assessment
- Multi-factor degradation risk scoring (0-100 scale)
- Risk categorization: Low, Moderate, High, Critical
- Individual risk metrics:
  - Drought risk
  - Erosion risk
  - Soil degradation risk
  - Vegetation loss risk
  - Temperature stress
  - Water scarcity

### 🤖 AI-Powered Recommendations
- **HuggingFace AI integration** for context-aware recommendations
- **Rule-based fallback** system for offline/low-resource scenarios
- Prioritized action plans (High, Medium, Low urgency)
- Cost estimates and expected risk reduction
- Native species recommendations for restoration
- Categories: Restoration, Irrigation, Soil Management, Vegetation, Monitoring

### 🌦️ Climate Integration
- 7-day weather forecasts
- Historical climate data analysis
- Temperature and precipitation tracking
- Real-time weather alerts

### 📊 Interactive Visualizations
- Real-time charts (Recharts)
- Risk trend analysis
- Climate forecast graphs
- Geographic location mapping

### 🔔 Smart Alerts
- Critical risk notifications
- Drought warnings
- Extreme weather alerts
- Customizable alert thresholds

---

## 🛠️ Tech Stack

### Frontend
- **React 18.3.1** - UI framework
- **Recharts** - Data visualization
- **Lucide React** - Icon library
- **Supabase JS Client** - Real-time database
- **Axios** - HTTP client

### Backend
- **FastAPI** - High-performance Python web framework
- **Supabase** - PostgreSQL database with real-time capabilities
- **HuggingFace Hub** - AI model integration
- **Uvicorn** - ASGI server
- **Python 3.11+** - Core language

### Database & Infrastructure
- **Supabase (PostgreSQL)** - Primary database
- **Supabase Realtime** - WebSocket-based live updates
- **Row Level Security (RLS)** - Data access control

### AI/ML
- **HuggingFace Inference API** - Natural language generation
- **Mistral-7B-Instruct** - Default AI model
- Custom rule-based recommendation engine (fallback)

### Deployment
- **Vercel** - Frontend hosting
- **Render/Railway** - Backend hosting

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React + Supabase Client)                    │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             │ REST API                           │ WebSocket
             │                                    │ (Realtime)
             ▼                                    ▼
┌─────────────────────────┐        ┌──────────────────────────────┐
│    FastAPI Backend      │        │    Supabase Realtime         │
│  - REST Endpoints       │◄───────┤  - Live Data Sync            │
│  - Business Logic       │        │  - Push Notifications        │
│  - AI Integration       │        └──────────────────────────────┘
└────────┬────────────────┘
         │
         │ SQL Queries
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPABASE (PostgreSQL)                        │
│  ┌──────────────┬─────────────┬──────────────┬────────────────┐│
│  │  Locations   │ Land Health │ Climate Data │ Risk Assessment││
│  ├──────────────┼─────────────┼──────────────┼────────────────┤│
│  │Recommendations│   Alerts    │  Real-time   │    Views       ││
│  └──────────────┴─────────────┴──────────────┴────────────────┘│
└─────────────────────────────────────────────────────────────────┘
         │
         │ API Calls
         ▼
┌─────────────────────────┐
│  HuggingFace Inference  │
│  - Mistral-7B-Instruct  │
│  - Text Generation      │
└─────────────────────────┘
```

### Data Flow

1. **User selects location** → Frontend requests data via REST API
2. **Backend queries Supabase** → Fetches health, risk, and climate data
3. **User requests recommendations** → Backend generates AI/rule-based recommendations
4. **Real-time updates** → Supabase pushes new data to frontend via WebSocket
5. **Alerts triggered** → System notifies users of critical conditions

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.11+
- **Git**
- **Supabase account** (free tier available)
- **HuggingFace account** (optional, for AI features)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/terraguard-ai.git
cd terraguard-ai
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install
```

### Environment Setup

#### Backend Environment Variables

Create `backend/.env`:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# HuggingFace API (Optional - for AI recommendations)
HUGGINGFACE_API_TOKEN=hf_your_token_here

# Server Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Optional: Frontend URL for production
FRONTEND_URL=https://your-app.vercel.app
```

#### Frontend Environment Variables

Create `frontend/.env`:

```env
# Backend API
REACT_APP_API_URL=http://localhost:8000

# Supabase Configuration
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-supabase-anon-key
```

#### Get Supabase Credentials

1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to **Settings → API**
4. Copy:
   - Project URL → `SUPABASE_URL`
   - `anon` `public` key → `SUPABASE_KEY` / `REACT_APP_SUPABASE_ANON_KEY`

#### Get HuggingFace Token (Optional)

1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create new token with "Read" access
3. Copy token → `HUGGINGFACE_API_TOKEN`

### Database Setup

Run the SQL schema from `backend/database/schema.sql` in your Supabase SQL editor:

```sql
-- See backend/database/schema.sql for full schema
-- Includes tables: locations, land_health, degradation_risk, 
-- climate_data, recommendations, alerts
```

---

## 💻 Usage

### Running Locally

#### Start Backend

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`

#### Start Frontend

```bash
cd frontend
npm start
# or
yarn start
```

Frontend will be available at: `http://localhost:3000`

### Using the Application

1. **Select a Location**
   - Choose from the location dropdown in the navbar
   - Dashboard will load real-time data for that location

2. **Monitor Land Health**
   - View NDVI score (0-1 scale)
   - Check vegetation cover percentage
   - Monitor soil moisture levels

3. **Assess Risks**
   - View overall degradation risk score (0-100)
   - Analyze individual risk factors
   - Track risk trends over time

4. **Get Recommendations**
   - Click "Generate New" in the recommendations panel
   - Review AI-powered or rule-based action plans
   - Implement prioritized recommendations

5. **Monitor Weather**
   - View 7-day forecast
   - Check temperature and precipitation trends
   - Respond to weather alerts

---

## 📚 API Documentation

### Base URL

- **Local:** `http://localhost:8000`
- **Production:** `https://terraguard-api.onrender.com`

### Authentication

Currently using Supabase service role key. For production, implement JWT-based authentication.

### Endpoints

#### Locations

```http
GET /api/locations/
```
Fetch all locations.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Nakuru Farm",
      "latitude": -0.3031,
      "longitude": 36.0800,
      "description": "Sample farm location"
    }
  ]
}
```

---

```http
GET /api/locations/{location_id}
```
Fetch single location by ID.

---

#### Land Health

```http
GET /api/land-health/{location_id}/latest
```
Get latest land health metrics for a location.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "location_id": "uuid",
    "ndvi": 0.65,
    "vegetation_cover": 68.5,
    "soil_moisture": 45.2,
    "observation_date": "2025-10-12"
  }
}
```

---

#### Risk Assessment

```http
GET /api/risk/{location_id}/latest
```
Get latest degradation risk assessment.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "location_id": "uuid",
    "total_risk_score": 61.29,
    "risk_level": "HIGH",
    "drought_risk": 3.73,
    "erosion_risk": 4.81,
    "soil_degradation_risk": 0.18,
    "vegetation_loss_risk": 8.75,
    "assessment_date": "2025-10-11"
  }
}
```

---

```http
GET /api/risk/{location_id}/trend?months=6
```
Get risk trend over time.

---

#### Climate Data

```http
GET /api/climate/{location_id}/forecast?days=7
```
Get climate forecast for next X days.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-10-13",
      "temperature": 25.5,
      "humidity": 65,
      "precipitation": 2.5
    }
  ]
}
```

---

#### Recommendations

```http
GET /api/recommendations/{location_id}
```
Fetch recommendations for a location.

---

```http
POST /api/recommendations/generate/{location_id}
```
Generate new AI-powered recommendations.

**Response:**
```json
{
  "success": true,
  "message": "Generated 3 recommendations",
  "data": [
    {
      "id": "uuid",
      "priority": "high",
      "category": "restoration",
      "action_title": "Implement soil conservation measures",
      "action_description": "Establish contour bunds...",
      "urgency_hours": 72,
      "expected_risk_reduction": 25.0,
      "expected_cost_usd": 500
    }
  ],
  "ai_powered": true
}
```

---

#### Health Check

```http
GET /health
```
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-12T10:30:00",
  "ai_service": "available"
}
```

---

### Interactive API Docs

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

---

## 🌐 Deployment

### Quick Deploy (Recommended)

#### Backend → Render

1. Push code to GitHub
2. Create account at [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect repository, select `backend` folder
5. Add environment variables
6. Deploy!

**URL:** `https://terraguard-api.onrender.com`

#### Frontend → Vercel

1. Create account at [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import repository, select `frontend` folder
4. Add environment variables
5. Deploy!

**URL:** `https://terraguard.vercel.app`

---

## 🤝 Contributing

We welcome contributions! 

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- **Python:** Follow PEP 8, use Black formatter
- **JavaScript:** Follow Airbnb style guide, use Prettier
- **Commits:** Use conventional commits (feat:, fix:, docs:, etc.)

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
# or
yarn test
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Team

- **Brian Kirop** - *Developer* - [@Bkirop](https://github.com/Bkirop)
- **Rose B** - *Developer* - [@wacuk-a](https://github.com/wacuk-a)

---

## 🙏 Acknowledgments

- **Supabase** - For providing excellent real-time database infrastructure
- **HuggingFace** - For AI model hosting and inference API
- **FastAPI** - For the high-performance backend framework
- **React Team** - For the amazing frontend library
- African farmers and land managers who inspired this project

---

## 📞 Contact & Support

- **Email:** briankirop@gmail.com or wacukakaru@gmail.com

---

## 🗺️ Roadmap

### Version 2.0 (Coming Soon)

- [ ] Mobile app (React Native)
- [ ] Multi-language support (Swahili, French, Arabic)
- [ ] Satellite imagery integration (Sentinel-2, Landsat)
- [ ] Machine learning models for predictive analytics
- [ ] Community features (farmers forum, knowledge sharing)
- [ ] Offline mode for low-connectivity areas
- [ ] SMS/WhatsApp alerts
- [ ] Integration with agricultural extension services

### Future Features

- [ ] Drone imagery support
- [ ] Crop-specific recommendations
- [ ] Market price integration
- [ ] Carbon credit tracking
- [ ] Soil testing lab integration
- [ ] Government policy compliance checker

---


**Made with ❤️ for sustainable agriculture in Africa**
