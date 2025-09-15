#!/bin/bash

# Milo AI Frontend Development Setup Script
# This script sets up the frontend development environment

echo "🚀 Setting up Milo AI Frontend Development Environment..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Navigate to frontend directory
cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "📝 Creating .env.local file..."
    cat > .env.local << EOF
# Local Development Environment Variables
# Replace these with your actual values

# Supabase Configuration
VITE_SUPABASE_URL=your_supabase_url_here
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Clerk Authentication
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here

# API Configuration
VITE_API_BASE_URL=http://localhost:8001

# Development Flags
VITE_DEV_MODE=true
VITE_ENABLE_MOCK_DATA=true
EOF
    echo "✅ Created .env.local file"
    echo "⚠️  Please update .env.local with your actual environment variables"
else
    echo "✅ .env.local already exists"
fi

# Run type check
echo "🔍 Running TypeScript type check..."
npm run type-check

if [ $? -ne 0 ]; then
    echo "⚠️  TypeScript type check found issues. Please review and fix them."
else
    echo "✅ TypeScript type check passed"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env.local with your actual environment variables"
echo "2. Start the development server: npm run dev"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "For more information, see DEVELOPMENT.md"
