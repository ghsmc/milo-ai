import React from 'react';
import { ClerkProvider, ClerkLoaded, ClerkLoading } from '@clerk/clerk-react';
import { dark } from '@clerk/themes';

interface ClerkProviderWrapperProps {
  children: React.ReactNode;
}

const ClerkProviderWrapper: React.FC<ClerkProviderWrapperProps> = ({ children }) => {
  const publishableKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
  const isProduction = publishableKey?.startsWith('pk_live_');

  if (!publishableKey) {
    console.warn('Clerk publishable key not found. Please add VITE_CLERK_PUBLISHABLE_KEY to your .env.local file');
    return <>{children}</>;
  }

  // Log environment for debugging
  console.log(`🔐 Clerk initialized in ${isProduction ? 'PRODUCTION' : 'DEVELOPMENT'} mode`);

  return (
    <ClerkProvider
      publishableKey={publishableKey}
      appearance={{
        baseTheme: dark,
        variables: {
          colorPrimary: '#dc2626',
          colorBackground: '#000000',
          colorInputBackground: '#1f2937',
          colorInputText: '#ffffff',
          colorText: '#ffffff',
          colorTextSecondary: '#9ca3af',
          borderRadius: '0.5rem',
        },
        elements: {
          formButtonPrimary: 'bg-red-600 hover:bg-red-700 text-white font-light',
          card: 'bg-black border-gray-800 shadow-2xl',
          headerTitle: 'text-white text-2xl font-light',
          headerSubtitle: 'text-gray-400 font-light',
          socialButtonsBlockButton: 'bg-gray-800 border-gray-700 text-white hover:bg-gray-700 hover:border-red-600 transition-colors',
          formFieldInput: 'bg-gray-800 border-gray-700 text-white focus:border-red-600 focus:ring-red-600/20',
          footerActionLink: 'text-red-400 hover:text-red-300',
          identityPreviewText: 'text-gray-300',
          formFieldLabel: 'text-gray-300',
          dividerLine: 'bg-gray-700',
          dividerText: 'text-gray-400',
        }
      }}
    >
      <ClerkLoading>
        <div className="min-h-screen bg-gray-950 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
            <p className="text-gray-400 font-light">Loading...</p>
          </div>
        </div>
      </ClerkLoading>
      <ClerkLoaded>
        {children}
      </ClerkLoaded>
    </ClerkProvider>
  );
};

export default ClerkProviderWrapper;
