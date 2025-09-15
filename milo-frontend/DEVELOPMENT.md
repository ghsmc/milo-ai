# Frontend Development Setup

This guide will help you set up the Milo AI frontend for local development.

## Prerequisites

- Node.js (version 18 or higher)
- npm or yarn
- Git

## Quick Start

1. **Navigate to the frontend directory:**
   ```bash
   cd milo-frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   Create a `.env.local` file in the `milo-frontend` directory with the following variables:
   ```env
   VITE_SUPABASE_URL=your_supabase_url_here
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
   VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
   VITE_API_BASE_URL=http://localhost:8001
   VITE_DEV_MODE=true
   VITE_ENABLE_MOCK_DATA=true
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:3000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run dev:local` - Start development server in local mode
- `npm run build` - Build for production
- `npm run build:dev` - Build for development
- `npm run preview` - Preview production build
- `npm run preview:local` - Preview development build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Run ESLint with auto-fix
- `npm run type-check` - Run TypeScript type checking
- `npm run clean` - Clean build artifacts

## Development Features

### Hot Reload
The development server includes hot module replacement (HMR) for instant updates when you make changes.

### API Proxy
API calls to `/api/*` are automatically proxied to `http://localhost:8001` (your backend server).

### Mock Data
When `VITE_ENABLE_MOCK_DATA=true`, the app will use mock data instead of making real API calls.

### CORS Support
CORS is enabled for development to allow cross-origin requests.

## Project Structure

```
milo-frontend/
├── src/
│   ├── components/     # React components
│   ├── lib/           # Utility libraries and API services
│   ├── services/      # Business logic services
│   ├── hooks/         # Custom React hooks
│   ├── types/         # TypeScript type definitions
│   ├── contexts/      # React contexts
│   ├── data/          # Mock data and static data
│   └── utils/         # Utility functions
├── public/            # Static assets
├── dist/              # Build output (generated)
└── node_modules/      # Dependencies (generated)
```

## Backend Integration

The frontend is configured to work with your backend running on `http://localhost:8001`. Make sure your backend is running when developing locally.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_SUPABASE_URL` | Supabase project URL | Yes |
| `VITE_SUPABASE_ANON_KEY` | Supabase anonymous key | Yes |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk authentication key | Yes |
| `VITE_API_BASE_URL` | Backend API base URL | No (defaults to localhost:8001) |
| `VITE_DEV_MODE` | Enable development mode | No |
| `VITE_ENABLE_MOCK_DATA` | Use mock data instead of API | No |

## Troubleshooting

### Port Already in Use
If port 3000 is already in use, Vite will automatically try the next available port.

### API Connection Issues
- Ensure your backend is running on `http://localhost:8001`
- Check that CORS is properly configured on your backend
- Verify your environment variables are set correctly

### Build Issues
- Run `npm run clean` to clear build cache
- Check for TypeScript errors with `npm run type-check`
- Ensure all dependencies are installed with `npm install`

## Git Workflow

This frontend development is on the `frontend-dev` branch. When you're ready to merge changes:

1. Commit your changes to the `frontend-dev` branch
2. Push the branch: `git push origin frontend-dev`
3. Create a pull request to merge into `main`

## Production Deployment

When ready for production:
1. Switch to the `main` branch
2. Merge your frontend changes
3. Update environment variables for production
4. Run `npm run build` to create production build
5. Deploy the `dist` folder to your hosting service
