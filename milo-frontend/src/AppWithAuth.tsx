import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import ClerkProviderWrapper from './components/ClerkProvider';
import { SignInComponent, SignUpComponent, AuthGuard } from './components/AuthComponents';
import ClerkOnboarding from './components/ClerkOnboarding';
import AppContent from './App';

const AppWithAuth: React.FC = () => {
  return (
    <ClerkProviderWrapper>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/sign-in" element={<SignInComponent />} />
          <Route path="/sign-up" element={<SignUpComponent />} />
          
          {/* Protected routes */}
          <Route path="/onboarding" element={
            <AuthGuard>
              <ClerkOnboarding />
            </AuthGuard>
          } />
          
          <Route path="/dashboard" element={
            <AuthGuard>
              <AppContent />
            </AuthGuard>
          } />
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </ClerkProviderWrapper>
  );
};

export default AppWithAuth;
