import React from 'react';
import { ProfessionalHeader } from './ProfessionalHeader';
import { ProfessionalSidebar } from './ProfessionalSidebar';

interface ProfessionalLayoutProps {
  children: React.ReactNode;
  showSidebar?: boolean;
}

export const ProfessionalLayout: React.FC<ProfessionalLayoutProps> = ({ 
  children, 
  showSidebar = true 
}) => {
  return (
    <div className="min-h-screen bg-background">
      <ProfessionalHeader />
      
      <div className="flex">
        {showSidebar && (
          <aside className="hidden lg:block">
            <ProfessionalSidebar />
          </aside>
        )}
        
        <main className="flex-1 overflow-auto">
          <div className="container mx-auto p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
