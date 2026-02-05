# API Service Integration

## Overview
The frontend uses a service layer (`src/services/api.ts`) to fetch data. Currently, it returns mock data, but it's prepared to switch to a real FastAPI backend.

## Current Setup
- **Mock Data**: `src/data/mockApiData.ts` contains all mock data
- **API Service**: `src/services/api.ts` contains all API calls with mock implementations
- **Configuration**: API URL can be set via `VITE_API_URL` environment variable

## Setup Instructions

### For Development (with Mock Data)
```bash
npm run dev
```
The app will use mock data defined in `src/data/mockApiData.ts`.

### Switching to Real FastAPI Backend

When the FastAPI backend is ready, follow these steps:

1. **Create `.env.local`** in the `Frontend` folder:
```
VITE_API_URL=http://localhost:8000/api
```

2. **Replace mock implementations** in `src/services/api.ts`:

Each function currently has a comment showing what to replace. For example:

**Current (Mock):**
```typescript
export async function getDashboardStats() {
  return new Promise(resolve => {
    setTimeout(() => resolve(mockDashboardStats), 100)
  })
}
```

**To be replaced with (Real API):**
```typescript
export async function getDashboardStats() {
  const response = await fetch(`${API_BASE_URL}/dashboard/stats`)
  return response.json()
}
```

3. **Update the mock data** in `src/data/mockApiData.ts` to match your API response format if needed.

## Available Endpoints (Placeholders)

### Dashboard
- `GET /api/dashboard/stats` - Returns `{ valides, enCours, refuses }`
- `GET /api/dashboard/activity` - Returns array of activity values
- `GET /api/dashboard/validation-rate` - Returns array of validation rate values

### Flux Management
- `GET /api/flux/all` - Returns `{ valides[], encours[], refuses[] }`
- `POST /api/flux/{id}/valider` - Validate a flux
- `POST /api/flux/{id}/refuser` - Reject a flux

### Cleaning
- `GET /api/nettoyage/all` - Returns array of cleaning items
- `POST /api/nettoyage/{id}/clean` - Mark item as cleaned

## Important Notes
- All functions include error handling and use TypeScript
- Mock responses have a 100ms delay to simulate network latency
- Environment variable `VITE_API_URL` defaults to `http://localhost:8000/api` if not set
