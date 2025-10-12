# TerraGuard AI Backend API Documentation

## Climate Endpoints
- GET /climate/temperature?country_code=XXX&start_year=YYYY&end_year=YYYY
  Returns historical temperature data for a country.

## Land Health Endpoints
- GET /land-health/status?region=region_name
  Returns degradation index of land health for a region.

## Predictions Endpoints
- POST /predictions/degradation
  Request: JSON { region: str, years_ahead: int }
  Response: Predicted land degradation index.

## Recommendations Endpoints
- GET /recommendations?region=region_name
  Returns land restoration recommendations from Claude AI.

