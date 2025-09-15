// Development Configuration
// This file contains development-specific settings

export const devConfig = {
  // API Configuration
  apiBaseUrl: 'http://localhost:8001',
  
  // Development Flags
  enableMockData: true,
  enableDevMode: true,
  
  // Supabase Configuration (you'll need to set these)
  supabase: {
    url: process.env.VITE_SUPABASE_URL || 'your_supabase_url_here',
    anonKey: process.env.VITE_SUPABASE_ANON_KEY || 'your_supabase_anon_key_here'
  },
  
  // Clerk Configuration (you'll need to set these)
  clerk: {
    publishableKey: process.env.VITE_CLERK_PUBLISHABLE_KEY || 'your_clerk_publishable_key_here'
  }
};

// Instructions for setup:
// 1. Copy this file to your local environment
// 2. Set up your environment variables in your shell or IDE
// 3. Or create a .env.local file with the following variables:
//    VITE_SUPABASE_URL=your_actual_supabase_url
//    VITE_SUPABASE_ANON_KEY=your_actual_supabase_anon_key
//    VITE_CLERK_PUBLISHABLE_KEY=your_actual_clerk_publishable_key
