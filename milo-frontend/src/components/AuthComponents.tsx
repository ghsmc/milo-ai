import React from 'react';
import { SignIn, SignUp, UserButton, useUser } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';

export const SignInComponent: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">

        
        <SignIn 
          afterSignInUrl="/dashboard"
          appearance={{
            baseTheme: undefined,
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
              card: 'bg-black border-gray-800 shadow-2xl',
              headerTitle: 'text-white text-2xl font-light',
              headerSubtitle: 'text-gray-400 font-light',
              socialButtonsBlockButton: 'bg-gray-800 border-gray-700 text-white hover:bg-gray-700 hover:border-red-600 transition-colors',
              formFieldInput: 'bg-gray-800 border-gray-700 text-white focus:border-red-600 focus:ring-red-600/20',
              formButtonPrimary: 'bg-red-600 hover:bg-red-700 text-white font-light',
              footerActionLink: 'text-red-400 hover:text-red-300',
              identityPreviewText: 'text-gray-300',
              formFieldLabel: 'text-gray-300',
              dividerLine: 'bg-gray-700',
              dividerText: 'text-gray-400',
              formFieldInputShowPasswordButton: 'text-gray-400 hover:text-white',
              formFieldInputShowPasswordIcon: 'text-gray-400',
            }
          }}
        />
      </div>
    </div>
  );
};

export const SignUpComponent: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">

        
        <SignUp 
          afterSignUpUrl="/onboarding"
          appearance={{
            baseTheme: undefined,
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
              card: 'bg-black border-gray-800 shadow-2xl',
              headerTitle: 'text-white text-2xl font-light',
              headerSubtitle: 'text-gray-400 font-light',
              socialButtonsBlockButton: 'bg-gray-800 border-gray-700 text-white hover:bg-gray-700 hover:border-red-600 transition-colors',
              formFieldInput: 'bg-gray-800 border-gray-700 text-white focus:border-red-600 focus:ring-red-600/20',
              formButtonPrimary: 'bg-red-600 hover:bg-red-700 text-white font-light',
              footerActionLink: 'text-red-400 hover:text-red-300',
              identityPreviewText: 'text-gray-300',
              formFieldLabel: 'text-gray-300',
              dividerLine: 'bg-gray-700',
              dividerText: 'text-gray-400',
              formFieldInputShowPasswordButton: 'text-gray-400 hover:text-white',
              formFieldInputShowPasswordIcon: 'text-gray-400',
              phoneInputBox: 'bg-gray-800 border-gray-700 text-white',
              phoneInputButton: 'bg-gray-800 border-gray-700 text-white hover:bg-gray-700',
            }
          }}
        />
      </div>
    </div>
  );
};

export const UserProfileButton: React.FC = () => {
  return (
    <UserButton 
      appearance={{
        elements: {
          avatarBox: 'w-8 h-8',
          userButtonPopoverCard: 'bg-gray-800 border-gray-700',
          userButtonPopoverActionButton: 'text-white hover:bg-gray-700',
        }
      }}
    />
  );
};

export const AuthGuard: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isSignedIn, isLoaded } = useUser();

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto mb-4"></div>
          <p className="text-gray-400 font-light">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isSignedIn) {
    return <SignInComponent />;
  }

  return <>{children}</>;
};
