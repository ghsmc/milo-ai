# Yale Alumni API

This folder contains the API endpoints for querying Yale alumni data.

## Files

- **`simple_api.py`** - Main API implementation with core endpoints
- **`api_endpoints.py`** - Extended API with more features (experimental)
- **`api_design.md`** - Complete API design documentation
- **`__init__.py`** - Package initialization

## Current Endpoints

### Company Alumni
```
GET /api/companies/{company_name}/alumni?limit=50
```
Returns Yale alumni at a specific company.

### Position Alumni
```
GET /api/positions/{position_name}/alumni?limit=50
```
Returns Yale alumni in a specific position/role.

### Company Insights
```
GET /api/companies/{company_name}/insights
```
Returns hiring trends and insights for a company.

### Health Check
```
GET /api/health
```
Returns API status and data loaded count.

## Usage Examples

```bash
# Get Goldman Sachs alumni
curl "https://web-production-ef948.up.railway.app/api/companies/Goldman%20Sachs/alumni?limit=10"

# Get company insights
curl "https://web-production-ef948.up.railway.app/api/companies/Google/insights"

# Get analysts
curl "https://web-production-ef948.up.railway.app/api/positions/analyst/alumni?limit=5"
```

## Development

The API is mounted at `/api` in the main FastAPI application. To add new endpoints:

1. Add the endpoint to `simple_api.py`
2. Update this README
3. Test the endpoint
4. Deploy changes

## Data Source

The API uses the same data source as the main analysis (`milo.yale_data`) which loads from the PostgreSQL database with flexible company matching logic.
