# Milo Frontend - AI Discovery Engine for Yale Students

This is the frontend-only version of Milo, an AI-powered career discovery platform for Yale students.

## Features

- **Company Discovery**: Display personalized company recommendations with specific teams
- **High-Leverage Next Moves**: Show actionable career steps
- **Interactive UI**: Modern React interface with Tailwind CSS
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Styling**: Tailwind CSS + Framer Motion
- **Icons**: Lucide React
- **Routing**: React Router DOM

## Quick Start

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

## Project Structure

```
src/
├── components/         # React components
│   ├── SearchSection.tsx    # Chat input interface
│   ├── ResultsDisplay.tsx   # Company results display
│   ├── JobCard.tsx          # Individual company cards
│   └── ...                  # Other UI components
├── contexts/          # React contexts
├── hooks/             # Custom hooks
├── lib/               # Utility libraries
├── services/          # API services (frontend only)
├── types/             # TypeScript types
└── main.tsx           # App entry point
```

## Key Components

- **SearchSection**: Chat input for user queries
- **ResultsDisplay**: Main results container
- **JobCard**: Individual company recommendation cards
- **Navigation**: App navigation and header
- **Sidebar**: Additional navigation options

## Development

This frontend is designed to work with a backend API. The main API endpoints expected are:

- `POST /api/chat` - Send user queries and receive AI responses
- `GET /api/companies` - Fetch company recommendations
- `GET /api/pathways` - Fetch high-leverage next moves

## Building

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

## License

Private project for Yale students.
