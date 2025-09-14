import React, { useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { useNavigate } from 'react-router-dom';

interface OnboardingData {
  full_name: string;
  class_year: string;
  major: string;
  gpa?: number;
  skills_and_clubs: string[];
  interests: string[];
  preferred_industries: string[];
  preferred_locations: string[];
  preferred_company_sizes: string[];
  work_model_preference: string;
  salary_expectation_min?: number;
  salary_expectation_max?: number;
  constraints: string[];
  current_term: string;
  location: string;
  career_goals: string;
  resume_file?: File;
  resume_url?: string;
}

const ClerkOnboarding: React.FC = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<OnboardingData>({
    full_name: user?.fullName || '',
    class_year: '',
    major: '',
    gpa: undefined,
    skills_and_clubs: [],
    interests: [],
    preferred_industries: [],
    preferred_locations: [],
    preferred_company_sizes: [],
    work_model_preference: 'any',
    salary_expectation_min: undefined,
    salary_expectation_max: undefined,
    constraints: [],
    current_term: '',
    location: '',
    career_goals: ''
  });

  const [currentInput, setCurrentInput] = useState('');
  const [uploadError, setUploadError] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const validateFile = (file: File): string | null => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (file.size > maxSize) {
      return 'File size must be less than 10MB';
    }
    
    if (!allowedTypes.includes(file.type)) {
      return 'Please upload a PDF, DOC, or DOCX file';
    }
    
    return null;
  };

  const uploadResumeToStorage = async (file: File): Promise<string | null> => {
    // TODO: Implement actual file upload to storage service
    // For now, we'll just store the file in the form data
    // In production, you might want to upload to:
    // - Clerk's file storage
    // - AWS S3
    // - Supabase Storage
    // - Firebase Storage
    
    try {
      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For now, return a placeholder URL
      // In production, this would be the actual uploaded file URL
      return `resume_${Date.now()}_${file.name}`;
    } catch (error) {
      console.error('Error uploading resume:', error);
      return null;
    }
  };

  const handleNext = async () => {
    if (step < 7) {
      setStep(step + 1);
    } else {
      setIsUploading(true);
      try {
        // Upload resume if provided
        let resumeUrl = null;
        if (formData.resume_file) {
          resumeUrl = await uploadResumeToStorage(formData.resume_file);
        }

        // Save onboarding data to Clerk user metadata
        await user?.update({
          unsafeMetadata: {
            onboarding_completed: true,
            ...formData,
            resume_url: resumeUrl,
            // Don't store the actual file object in metadata
            resume_file: undefined
          }
        });
        
        navigate('/dashboard');
      } catch (error) {
        console.error('Error saving onboarding data:', error);
        // Still navigate to dashboard even if resume upload fails
        navigate('/dashboard');
      } finally {
        setIsUploading(false);
      }
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const addToList = (field: keyof OnboardingData) => {
    if (currentInput.trim() && Array.isArray(formData[field])) {
      setFormData(prev => ({
        ...prev,
        [field]: [...(prev[field] as string[]), currentInput.trim()]
      }));
      setCurrentInput('');
    }
  };

  const removeFromList = (field: keyof OnboardingData, index: number) => {
    if (Array.isArray(formData[field])) {
      setFormData(prev => ({
        ...prev,
        [field]: (prev[field] as string[]).filter((_, i) => i !== index)
      }));
    }
  };

  const toggleArrayItem = (field: keyof OnboardingData, item: string) => {
    if (Array.isArray(formData[field])) {
      const current = formData[field] as string[];
      const updated = current.includes(item)
        ? current.filter(i => i !== item)
        : [...current, item];
      setFormData(prev => ({
        ...prev,
        [field]: updated
      }));
    }
  };

  const steps = [
    { title: 'Welcome to Milo', subtitle: 'Your AI career discovery platform' },
    { title: 'Basic Information', subtitle: 'Tell us about yourself' },
    { title: 'Your Interests', subtitle: 'What excites you?' },
    { title: 'Career Goals', subtitle: 'What do you want to achieve?' },
    { title: 'Preferences', subtitle: 'Work style and location' },
    { title: 'Upload Resume', subtitle: 'Help us understand your background' },
    { title: 'Complete', subtitle: 'Ready to discover opportunities' }
  ];

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="text-center">
            <p className="text-xl text-gray-300 font-light leading-relaxed">
              We'll help you discover amazing career opportunities tailored just for you.
            </p>
            <div className="mt-8 space-y-4">
              <div className="flex items-center justify-center space-x-3">
                <div className="w-3 h-3 bg-red-600 rounded-full"></div>
                <span className="text-gray-400">Personalized job matching</span>
              </div>
              <div className="flex items-center justify-center space-x-3">
                <div className="w-3 h-3 bg-red-600 rounded-full"></div>
                <span className="text-gray-400">AI-powered opportunity discovery</span>
              </div>
              <div className="flex items-center justify-center space-x-3">
                <div className="w-3 h-3 bg-red-600 rounded-full"></div>
                <span className="text-gray-400">Yale alumni network insights</span>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData(prev => ({ ...prev, full_name: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
                placeholder="Enter your full name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Class Year
              </label>
              <select
                value={formData.class_year}
                onChange={(e) => setFormData(prev => ({ ...prev, class_year: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
              >
                <option value="">Select your class year</option>
                <option value="2025">2025</option>
                <option value="2026">2026</option>
                <option value="2027">2027</option>
                <option value="2028">2028</option>
                <option value="2029">2029</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Major
              </label>
              <input
                type="text"
                value={formData.major}
                onChange={(e) => setFormData(prev => ({ ...prev, major: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
                placeholder="e.g., Computer Science, Economics, etc."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                GPA (Optional)
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="4"
                value={formData.gpa || ''}
                onChange={(e) => setFormData(prev => ({ ...prev, gpa: parseFloat(e.target.value) || undefined }))}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
                placeholder="e.g., 3.8"
              />
            </div>
          </div>
        );

      case 3:
        const industries = [
          'Technology', 'Finance', 'Consulting', 'Healthcare', 'Education',
          'Government', 'Non-profit', 'Media', 'Real Estate', 'Energy'
        ];

        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Preferred Industries
              </label>
              <div className="grid grid-cols-2 gap-2">
                {industries.map((industry) => (
                  <button
                    key={industry}
                    onClick={() => toggleArrayItem('preferred_industries', industry)}
                    className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                      formData.preferred_industries.includes(industry)
                        ? 'bg-red-600 text-white'
                        : 'bg-gray-900 border border-gray-800 text-gray-300 hover:border-red-600'
                    }`}
                  >
                    {industry}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Skills & Activities
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addToList('skills_and_clubs')}
                  className="flex-1 px-4 py-2 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
                  placeholder="e.g., Python, Debate Team, etc."
                />
                <button
                  onClick={() => addToList('skills_and_clubs')}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.skills_and_clubs.map((item, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-red-600 text-white rounded-full text-sm flex items-center gap-2"
                  >
                    {item}
                    <button
                      onClick={() => removeFromList('skills_and_clubs', index)}
                      className="text-red-200 hover:text-white"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Career Goals
              </label>
              <textarea
                value={formData.career_goals}
                onChange={(e) => setFormData(prev => ({ ...prev, career_goals: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none h-32 resize-none"
                placeholder="What do you want to achieve in your career?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Interests & Passions
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addToList('interests')}
                  className="flex-1 px-4 py-2 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
                  placeholder="e.g., AI/ML, Fintech, Startups, etc."
                />
                <button
                  onClick={() => addToList('interests')}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.interests.map((item, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-green-600 text-white rounded-full text-sm flex items-center gap-2"
                  >
                    {item}
                    <button
                      onClick={() => removeFromList('interests', index)}
                      className="text-green-200 hover:text-white"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Preferred Locations
              </label>
              <div className="flex gap-2 mb-3">
                <input
                  type="text"
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addToList('preferred_locations')}
                  className="flex-1 px-4 py-2 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
                  placeholder="e.g., New York, San Francisco, Remote, etc."
                />
                <button
                  onClick={() => addToList('preferred_locations')}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Add
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {formData.preferred_locations.map((item, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm flex items-center gap-2"
                  >
                    {item}
                    <button
                      onClick={() => removeFromList('preferred_locations', index)}
                      className="text-blue-200 hover:text-white"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Company Size Preference
              </label>
              <div className="grid grid-cols-3 gap-2">
                {['Startup', 'Mid-size', 'Large'].map((size) => (
                  <button
                    key={size}
                    onClick={() => toggleArrayItem('preferred_company_sizes', size)}
                    className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                      formData.preferred_company_sizes.includes(size)
                        ? 'bg-red-600 text-white'
                        : 'bg-gray-900 border border-gray-800 text-gray-300 hover:border-red-600'
                    }`}
                  >
                    {size}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Work Model Preference
              </label>
              <select
                value={formData.work_model_preference}
                onChange={(e) => setFormData(prev => ({ ...prev, work_model_preference: e.target.value }))}
                className="w-full px-4 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
              >
                <option value="any">Any</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
                <option value="onsite">On-site</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Min Salary (Optional)
                </label>
                <input
                  type="number"
                  value={formData.salary_expectation_min || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, salary_expectation_min: parseInt(e.target.value) || undefined }))}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
                  placeholder="e.g., 80000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Max Salary (Optional)
                </label>
                <input
                  type="number"
                  value={formData.salary_expectation_max || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, salary_expectation_max: parseInt(e.target.value) || undefined }))}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg focus:border-red-600 focus:outline-none"
                  placeholder="e.g., 120000"
                />
              </div>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <div className="text-center mb-6">
              <p className="text-lg text-gray-300 font-light">
                Upload your resume to help us provide more personalized career advice and match you with relevant opportunities.
              </p>
            </div>
            
            <div className="border-2 border-dashed border-gray-700 rounded-lg p-8 text-center hover:border-red-600 transition-colors">
              <input
                type="file"
                id="resume-upload"
                accept=".pdf,.doc,.docx"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    const error = validateFile(file);
                    if (error) {
                      setUploadError(error);
                    } else {
                      setUploadError('');
                      setFormData(prev => ({ ...prev, resume_file: file }));
                    }
                  }
                }}
                className="hidden"
              />
              <label
                htmlFor="resume-upload"
                className="cursor-pointer flex flex-col items-center space-y-4"
              >
                <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <p className="text-white font-medium">
                    {formData.resume_file ? formData.resume_file.name : 'Click to upload resume'}
                  </p>
                  <p className="text-gray-400 text-sm mt-1">
                    PDF, DOC, or DOCX files only (max 10MB)
                  </p>
                </div>
              </label>
            </div>

            {uploadError && (
              <div className="bg-red-900/20 border border-red-600 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-red-400 text-sm">{uploadError}</p>
                </div>
              </div>
            )}

            {formData.resume_file && (
              <div className="bg-gray-900 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-red-600 rounded flex items-center justify-center">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-white font-medium">{formData.resume_file.name}</p>
                      <p className="text-gray-400 text-sm">
                        {(formData.resume_file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => setFormData(prev => ({ ...prev, resume_file: undefined }))}
                    className="text-gray-400 hover:text-red-400 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            )}

            <div className="text-center">
              <p className="text-sm text-gray-500">
                Don't have a resume? You can skip this step and add it later in your profile.
              </p>
            </div>
          </div>
        );

      case 7:
        return (
          <div className="text-center">
            <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-white text-2xl">✓</span>
            </div>
            <h3 className="text-xl font-semibold text-white mb-4">
              You're all set!
            </h3>
            <p className="text-gray-400 mb-6">
              We've gathered your information and are ready to show you personalized opportunities.
            </p>
            <div className="bg-gray-900 rounded-lg p-4 text-left">
              <h4 className="text-sm font-medium text-gray-300 mb-2">Your Profile:</h4>
              <div className="text-sm text-gray-400 space-y-1">
                <div>Name: {formData.full_name}</div>
                <div>Class: {formData.class_year}</div>
                <div>Major: {formData.major}</div>
                <div>Industries: {formData.preferred_industries.join(', ') || 'None'}</div>
                <div>Skills: {formData.skills_and_clubs.join(', ') || 'None'}</div>
                <div>Interests: {formData.interests.join(', ') || 'None'}</div>
                <div>Resume: {formData.resume_file ? formData.resume_file.name : 'Not uploaded'}</div>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white flex flex-col">
      {/* Header */}
      <div className="flex-1 flex flex-col justify-center px-8">
        <div className="max-w-lg mx-auto w-full">
          {/* Layered Milo Logo */}
          <div className="flex items-center justify-center mb-16">
            <div className="relative w-12 h-12 flex items-center justify-center">
              {/* Layer 3 - Outer ring */}
              <div className="absolute w-20 h-20 bg-red-900/20 opacity-100 scale-100"
                   style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }} />
              {/* Layer 2 - Middle ring */}
              <div className="absolute w-16 h-16 bg-red-800/40 opacity-100 scale-100"
                   style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }} />
              {/* Layer 1 - Inner ring */}
              <div className="absolute w-12 h-12 bg-red-700/60 opacity-100 scale-100"
                   style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }} />
              {/* Core logo */}
              <div className="absolute w-12 h-12 bg-red-600 opacity-100 scale-100 flex items-center justify-center"
                   style={{ top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
                <span className="text-white text-xl font-black">人</span>
              </div>
            </div>
          </div>

          {/* Step Title */}
          <div className="text-center mb-16">
            <h1 className="text-4xl font-light tracking-tight mb-4 text-white">
              {steps[step - 1].title}
            </h1>
            <p className="text-lg font-light text-gray-400">
              {steps[step - 1].subtitle}
            </p>
          </div>

          {/* Step Content */}
          <div className="mb-16">
            {renderStep()}
          </div>

          {/* Progress Dots */}
          <div className="flex justify-center mb-8">
            <div className="flex space-x-2">
              {steps.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full transition-colors duration-300 ${
                    index < step ? 'bg-red-600' : 'bg-gray-700'
                  }`}
                />
              ))}
            </div>
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <button
              onClick={handleBack}
              disabled={step === 1}
              className="px-8 py-3 bg-gray-900 border border-gray-800 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-light"
            >
              Back
            </button>
            <button
              onClick={handleNext}
              disabled={isUploading}
              className="px-8 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-light flex items-center space-x-2"
            >
              {isUploading && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              )}
              <span>{isUploading ? 'Uploading...' : (step === 7 ? 'Complete Setup' : 'Next')}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClerkOnboarding;
